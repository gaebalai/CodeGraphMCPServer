"""
Git Operations Utility
======================

Git 변경 사항 감지 및 파일 조작 기능을 제공합니다.
REQ-STR-004: Git 연동을 통한 인크리멘털(증분) 업데이트를 지원
"""

import asyncio
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

from .logging import get_logger


logger = get_logger(__name__)


class ChangeType(Enum):
    """Git 변경 유형"""
    ADDED = auto()
    MODIFIED = auto()
    DELETED = auto()
    RENAMED = auto()
    COPIED = auto()
    UNTRACKED = auto()


@dataclass
class GitChange:
    """Git 변경 정보"""
    path: Path
    change_type: ChangeType
    old_path: Path | None = None  # For renames
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        if self.change_type == ChangeType.RENAMED and self.old_path:
            return f"{self.change_type.name}: {self.old_path} -> {self.path}"
        return f"{self.change_type.name}: {self.path}"


class GitOperations:
    """
    Git 작업 유틸리티 클래스

    REQ-STR-004: Git 연동을 통한 차이 감지
    - 변경 파일 감지
    - 커밋 기록 조회
    - 파일 내용 조회 (특정 리비전)
    """

    def __init__(self, repo_path: Path):
        """
        Args:
            repo_path: Git 리포지토리의 루트 경로
        """
        self.repo_path = repo_path.resolve()
        self._validate_repo()

    def _validate_repo(self) -> None:
        """리포지토리의 유효성을 검증"""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")

    async def get_changed_files(
        self,
        since: str | None = None,
        include_untracked: bool = True,
    ) -> list[GitChange]:
        """
        변경된 파일을 가져오기

        Args:
            since: 비교 대상 (커밋 해시, 브랜치 이름 등)
            include_untracked: 미추적 파일 포함 여부

        Returns:
            변경 파일 목록
        """
        changes: list[GitChange] = []

        # Staged and unstaged changes
        if since:
            cmd = ["git", "diff", "--name-status", since]
        else:
            cmd = ["git", "diff", "--name-status", "HEAD"]

        try:
            result = await self._run_git_command(cmd)
            changes.extend(self._parse_diff_output(result))
        except subprocess.CalledProcessError:
            # No commits yet or other error
            pass

        # Staged changes
        try:
            staged_cmd = ["git", "diff", "--name-status", "--cached"]
            result = await self._run_git_command(staged_cmd)
            changes.extend(self._parse_diff_output(result))
        except subprocess.CalledProcessError:
            pass

        # Untracked files
        if include_untracked:
            try:
                untracked_cmd = [
                    "git", "ls-files", "--others", "--exclude-standard"
                ]
                result = await self._run_git_command(untracked_cmd)
                for line in result.strip().split("\n"):
                    if line:
                        changes.append(GitChange(
                            path=Path(line),
                            change_type=ChangeType.UNTRACKED,
                        ))
            except subprocess.CalledProcessError:
                pass

        return self._deduplicate_changes(changes)

    def _parse_diff_output(self, output: str) -> list[GitChange]:
        """git diff --name-status 의 출력을 파싱"""
        changes = []
        for line in output.strip().split("\n"):
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) < 2:
                continue

            status = parts[0]
            path = Path(parts[1])

            if status.startswith("R"):
                # Rename: R100\told_path\tnew_path
                old_path = path
                new_path = Path(parts[2]) if len(parts) > 2 else path
                changes.append(GitChange(
                    path=new_path,
                    change_type=ChangeType.RENAMED,
                    old_path=old_path,
                ))
            elif status.startswith("C"):
                # Copy
                changes.append(GitChange(
                    path=Path(parts[2]) if len(parts) > 2 else path,
                    change_type=ChangeType.COPIED,
                    old_path=path,
                ))
            elif status == "A":
                changes.append(GitChange(
                    path=path,
                    change_type=ChangeType.ADDED,
                ))
            elif status == "D":
                changes.append(GitChange(
                    path=path,
                    change_type=ChangeType.DELETED,
                ))
            elif status == "M":
                changes.append(GitChange(
                    path=path,
                    change_type=ChangeType.MODIFIED,
                ))

        return changes

    def _deduplicate_changes(
        self, changes: list[GitChange]
    ) -> list[GitChange]:
        """중복된 변경을 제거"""
        seen = set()
        result = []
        for change in changes:
            key = (str(change.path), change.change_type)
            if key not in seen:
                seen.add(key)
                result.append(change)
        return result

    async def get_file_content(
        self,
        path: Path,
        revision: str = "HEAD",
    ) -> str | None:
        """
        특정 리비전의 파일 내용 가져오기

        Args:
            path: 파일 경로 (리포지토리 루트에서의 상대 경로)
            revision: Git 리비전 (커밋 해시, 브랜치 이름 등)

        Returns:
            파일 내용, 가져올 수 없는 경우 None
        """
        cmd = ["git", "show", f"{revision}:{path}"]
        try:
            return await self._run_git_command(cmd)
        except subprocess.CalledProcessError:
            logger.warning(f"Failed to get content: {path}@{revision}")
            return None

    async def get_current_branch(self) -> str | None:
        """현재 브랜치 이름 가져오기"""
        cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        try:
            result = await self._run_git_command(cmd)
            return result.strip()
        except subprocess.CalledProcessError:
            return None

    async def get_commit_hash(self, revision: str = "HEAD") -> str | None:
        """커밋 해시 가져오기"""
        cmd = ["git", "rev-parse", revision]
        try:
            result = await self._run_git_command(cmd)
            return result.strip()
        except subprocess.CalledProcessError:
            return None

    async def get_tracked_files(
        self,
        patterns: list[str] | None = None,
    ) -> list[Path]:
        """
        추적 대상 파일 목록 가져오기

        Args:
            patterns: 파일 패턴 (glob 형식)

        Returns:
            파일 경로 목록
        """
        cmd = ["git", "ls-files"]
        if patterns:
            cmd.extend(patterns)

        try:
            result = await self._run_git_command(cmd)
            return [
                Path(line)
                for line in result.strip().split("\n")
                if line
            ]
        except subprocess.CalledProcessError:
            return []

    async def _run_git_command(self, cmd: list[str]) -> str:
        """Git 명령을 비동기적으로 실행"""
        logger.debug(f"Running git command: {' '.join(cmd)}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error(f"Git command failed: {error_msg}")
            raise subprocess.CalledProcessError(
                process.returncode or 1,
                cmd,
                stdout,
                stderr,
            )

        return stdout.decode()

    def get_repo_root(self) -> Path:
        """리포지토리 루트 경로 반환"""
        return self.repo_path
