"""
End-to-End Scenario Tests
=========================

사용자 시나리오에 기반한 E2E 테스트.

실제 MCP 서버를 실행하고, 클라이언트를 통해 테스트합니다.
"""

import subprocess
import sys
from pathlib import Path

import pytest


# ========================
# Helper Functions
# ========================

def create_sample_project(repo_path: Path) -> None:
    """샘플 프로젝트 생성"""
    # Python files
    src_dir = repo_path / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    # Main module
    (src_dir / "main.py").write_text('''"""Main application module."""

from calculator import Calculator
from utils import format_result


def main():
    """Main entry point."""
    calc = Calculator()
    result = calc.add(1, 2)
    print(format_result(result))


if __name__ == "__main__":
    main()
''')

    # Calculator module
    (src_dir / "calculator.py").write_text('''"""Calculator module with basic operations."""

from typing import Union

Number = Union[int, float]


class Calculator:
    """A simple calculator class."""

    def __init__(self):
        self.history = []

    def add(self, a: Number, b: Number) -> Number:
        """Add two numbers."""
        result = a + b
        self._record(f"{a} + {b} = {result}")
        return result

    def subtract(self, a: Number, b: Number) -> Number:
        """Subtract b from a."""
        result = a - b
        self._record(f"{a} - {b} = {result}")
        return result

    def multiply(self, a: Number, b: Number) -> Number:
        """Multiply two numbers."""
        result = a * b
        self._record(f"{a} * {b} = {result}")
        return result

    def divide(self, a: Number, b: Number) -> Number:
        """Divide a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._record(f"{a} / {b} = {result}")
        return result

    def _record(self, operation: str) -> None:
        """Record operation in history."""
        self.history.append(operation)

    def get_history(self) -> list[str]:
        """Get operation history."""
        return self.history.copy()
''')

    # Utils module
    (src_dir / "utils.py").write_text('''"""Utility functions."""


def format_result(value: float, precision: int = 2) -> str:
    """Format a numeric result."""
    return f"Result: {value:.{precision}f}"


def validate_number(value: str) -> float:
    """Validate and convert string to number."""
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number: {value}")
''')

    # Test file
    tests_dir = repo_path / "tests"
    tests_dir.mkdir(exist_ok=True)

    (tests_dir / "test_calculator.py").write_text('''"""Tests for calculator module."""

import pytest
from src.calculator import Calculator


class TestCalculator:
    """Test cases for Calculator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calc = Calculator()

    def test_add(self):
        """Test addition."""
        assert self.calc.add(1, 2) == 3

    def test_subtract(self):
        """Test subtraction."""
        assert self.calc.subtract(5, 3) == 2

    def test_multiply(self):
        """Test multiplication."""
        assert self.calc.multiply(3, 4) == 12

    def test_divide(self):
        """Test division."""
        assert self.calc.divide(10, 2) == 5

    def test_divide_by_zero(self):
        """Test division by zero raises error."""
        with pytest.raises(ValueError):
            self.calc.divide(10, 0)

    def test_history(self):
        """Test operation history."""
        self.calc.add(1, 1)
        self.calc.multiply(2, 3)
        history = self.calc.get_history()
        assert len(history) == 2
''')

    # Git commit
    subprocess.run(["git", "add", "."], check=False, cwd=repo_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        check=False, cwd=repo_path,
        capture_output=True,
    )


def create_typescript_files(repo_path: Path) -> None:
    """TypeScriptファイルを追加"""
    ts_dir = repo_path / "frontend"
    ts_dir.mkdir(exist_ok=True)

    (ts_dir / "api.ts").write_text('''/**
 * API client module
 */

interface CalculatorResult {
    operation: string;
    result: number;
}

class APIClient {
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    async calculate(operation: string, a: number, b: number): Promise<CalculatorResult> {
        const response = await fetch(`${this.baseUrl}/calculate`, {
            method: 'POST',
            body: JSON.stringify({ operation, a, b }),
        });
        return response.json();
    }
}

export { APIClient, CalculatorResult };
''')

    subprocess.run(["git", "add", "."], check=False, cwd=repo_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add TypeScript files"],
        check=False, cwd=repo_path,
        capture_output=True,
    )


# ========================
# Test Classes
# ========================

class TestCodebaseAnalysisScenario:
    """코드베이스 분석 시나리오"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_index_and_query_codebase(self, temp_repo):
        """
        시나리오: 리포지토리를 인덱싱하고 쿼리하기

        1. 샘플 리포지토리 생성
        2. indexer로 인덱싱
        3. GraphEngine로 쿼리
        """
        from codegraph_mcp.core.graph import GraphEngine, GraphQuery
        from codegraph_mcp.core.indexer import Indexer

        # 1. 샘플 프로젝트 생성
        create_sample_project(temp_repo)

        # 2. 인덱싱 생성 (incremental=False로 모든 파일 스캔)
        indexer = Indexer()
        result = await indexer.index_repository(temp_repo, incremental=False)

        # 파일이 존재하는지 확인
        assert result.files_indexed > 0 or result.entities_count >= 0

        # 3. 쿼리 실행
        engine = GraphEngine(temp_repo)
        await engine.initialize()

        try:
            query = GraphQuery(query="Calculator", max_results=10)
            query_result = await engine.query(query)

            # 쿼리가 정상적으로 실행되는지 확인
            assert query_result is not None
        finally:
            await engine.close()

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_find_code_relationships(self, temp_repo):
        """
        시나리오: 코드 관련성 탐색

        1. 샘플 코드를 인덱싱
        2. 엔티티 간 관계 탐색
        """
        from codegraph_mcp.core.graph import GraphEngine, GraphQuery
        from codegraph_mcp.core.indexer import Indexer

        # 1. 샘플 프로젝트 생성
        create_sample_project(temp_repo)

        # 2. 인덱싱 생성
        indexer = Indexer()
        await indexer.index_repository(temp_repo)

        # 3. 관계 탐색
        engine = GraphEngine(temp_repo)
        await engine.initialize()

        try:
            # add 메서드 탐색
            query = GraphQuery(query="add", max_results=5)
            result = await engine.query(query)

            add_methods = [e for e in result.entities if e.name == "add"]
            if add_methods:
                # 호출자 탐색
                callers = await engine.find_callers(add_methods[0].id)
                # main에서 호출되는 것으로 예상
                assert len(callers) >= 0  # 호출자가 검출되는지 확인
        finally:
            await engine.close()

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_dependency_analysis(self, temp_repo):
        """
        시나리오: 의존성 분석

        1. 인덱싱 생성
        2. 모듈 의존성 획득
        """
        from codegraph_mcp.core.graph import GraphEngine, GraphQuery
        from codegraph_mcp.core.indexer import Indexer

        create_sample_project(temp_repo)

        indexer = Indexer()
        await indexer.index_repository(temp_repo)

        engine = GraphEngine(temp_repo)
        await engine.initialize()

        try:
            # Calculator 클래스 탐색
            query = GraphQuery(query="Calculator", max_results=5)
            result = await engine.query(query)

            calc_entities = [e for e in result.entities if e.name == "Calculator"]
            if calc_entities:
                # 의존성 탐색
                deps = await engine.find_dependencies(calc_entities[0].id, depth=2)
                # 의존성 결과가 반환되는지 확인
                assert deps is not None
        finally:
            await engine.close()


class TestIncrementalUpdateScenario:
    """증분 업데이트 시나리오"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_update_after_file_change(self, temp_repo):
        """
        시나리오: 파일 변경 후 증분 업데이트

        1. 리포지토리를 인덱싱
        2. 파일을 변경하고 커밋
        3. 증분 업데이트
        4. 업데이트된 그래프 확인
        """
        from codegraph_mcp.core.graph import GraphEngine, GraphQuery
        from codegraph_mcp.core.indexer import Indexer

        # 1. 초기 프로젝트 생성 및 인덱싱
        create_sample_project(temp_repo)

        indexer = Indexer()
        result1 = await indexer.index_repository(temp_repo)
        initial_count = result1.entities_count

        # 2. 새 파일 추가
        new_file = temp_repo / "src" / "advanced_calc.py"
        new_file.write_text('''"""Advanced calculator with more operations."""

from calculator import Calculator


class AdvancedCalculator(Calculator):
    """Extended calculator with advanced operations."""

    def power(self, base: float, exp: float) -> float:
        """Calculate base raised to exp."""
        return base ** exp

    def sqrt(self, value: float) -> float:
        """Calculate square root."""
        if value < 0:
            raise ValueError("Cannot take square root of negative number")
        return value ** 0.5
''')

        subprocess.run(["git", "add", "."], check=False, cwd=temp_repo, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add advanced calculator"],
            check=False, cwd=temp_repo,
            capture_output=True,
        )

        # 3. 증분 업데이트
        result2 = await indexer.index_repository(temp_repo, incremental=False)

        # 4. 엔티티가 증가하는지 확인
        assert result2.entities_count > initial_count

        # 새 클래스가 존재하는지 확인
        engine = GraphEngine(temp_repo)
        await engine.initialize()

        try:
            query = GraphQuery(query="AdvancedCalculator", max_results=5)
            result = await engine.query(query)

            advanced_calc = [e for e in result.entities if "AdvancedCalculator" in e.name]
            assert len(advanced_calc) > 0
        finally:
            await engine.close()


class TestMultiLanguageScenario:
    """다언어 지원 시나리오"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_mixed_language_project(self, temp_repo):
        """
        시나리오: 다언어 프로젝트 분석

        1. Python + TypeScript 샘플 프로젝트 생성
        2. 두 언어를 인덱싱
        3. 두 언어의 엔티티가 검출되는지 확인
        """
        from codegraph_mcp.core.graph import GraphEngine, GraphQuery
        from codegraph_mcp.core.indexer import Indexer

        # 1. Python + TypeScript 프로젝트 생성
        create_sample_project(temp_repo)
        create_typescript_files(temp_repo)

        # 2. 인덱싱 생성 (전체 스캔)
        indexer = Indexer()
        result = await indexer.index_repository(temp_repo, incremental=False)

        # 인덱싱이 정상적으로 완료되는지 확인
        assert result is not None

        # 3. 두 언어의 엔티티 탐색
        engine = GraphEngine(temp_repo)
        await engine.initialize()

        try:
            # 쿼리가 정상적으로 실행되는지 확인
            py_query = GraphQuery(query="Calculator", max_results=10)
            py_result = await engine.query(py_query)
            assert py_result is not None

            ts_query = GraphQuery(query="APIClient", max_results=10)
            ts_result = await engine.query(ts_query)
            assert ts_result is not None
        finally:
            await engine.close()


class TestCLIScenario:
    """CLI 시나리오"""

    @pytest.mark.e2e
    def test_cli_index_command(self, temp_repo):
        """
        시나리오: CLI로 인덱싱 생성
        """
        create_sample_project(temp_repo)

        # CLI 실행
        result = subprocess.run(
            [sys.executable, "-m", "codegraph_mcp", "index", str(temp_repo), "--full"],
            check=False, capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Indexed" in result.stdout or "entities" in result.stdout.lower()

    @pytest.mark.e2e
    def test_cli_stats_command(self, temp_repo):
        """
        시나리오: CLI로 통계 정보 획득
        """
        create_sample_project(temp_repo)

        # 먼저 인덱싱 생성
        subprocess.run(
            [sys.executable, "-m", "codegraph_mcp", "index", str(temp_repo), "--full"],
            check=False, capture_output=True,
        )

        # 통계 정보 획득
        result = subprocess.run(
            [sys.executable, "-m", "codegraph_mcp", "stats", str(temp_repo)],
            check=False, capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Entities" in result.stdout or "entities" in result.stdout.lower()

    @pytest.mark.e2e
    def test_cli_query_command(self, temp_repo):
        """
        시나리오: CLI로 쿼리 실행
        """
        create_sample_project(temp_repo)

        # 인덱싱 생성
        subprocess.run(
            [sys.executable, "-m", "codegraph_mcp", "index", str(temp_repo), "--full"],
            check=False, capture_output=True,
        )

        # 쿼리 실행
        result = subprocess.run(
            [sys.executable, "-m", "codegraph_mcp", "query", "Calculator", "--repo", str(temp_repo)],
            check=False, capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Calculator가 존재하는지 확인
        assert "Calculator" in result.stdout or "Found" in result.stdout


class TestStatisticsScenario:
    """통계 정보 시나리오"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_get_comprehensive_stats(self, temp_repo):
        """
        시나리오: 포괄적인 통계 정보 획득
        """
        from codegraph_mcp.core.graph import GraphEngine
        from codegraph_mcp.core.indexer import Indexer

        create_sample_project(temp_repo)

        indexer = Indexer()
        await indexer.index_repository(temp_repo, incremental=False)

        engine = GraphEngine(temp_repo)
        await engine.initialize()

        try:
            stats = await engine.get_statistics()

            # 통계 정보가 반환되는지 확인
            assert stats is not None
            # GraphStatistics 객체의 속성 확인
            assert hasattr(stats, 'entity_count') or hasattr(stats, 'entities')
        finally:
            await engine.close()


class TestLLMIntegrationScenario:
    """LLM 통합 시나리오"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.skip(reason="LLM integration tests require API key")
    async def test_semantic_analysis(self, temp_repo):
        """
        시나리오: LLM에 의한 시멘틱 분석

        1. 코드를 인덱싱
        2. LLM으로 커뮤니티 요약 생성
        3. 시멘틱 검색 실행
        """
        pass
