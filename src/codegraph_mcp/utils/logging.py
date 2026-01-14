"""
Logging Utilities
=================

구조화된 로깅 및 로그 설정을 제공합니다.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# 전역 로그 포맷 설정
DEFAULT_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
DEBUG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)

# 로그 레벨 매핑
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class ColoredFormatter(logging.Formatter):
    """
    터미널 출력용 컬러 포맷터
    """

    COLORS = {
        logging.DEBUG: "\033[36m",     # Cyan
        logging.INFO: "\033[32m",      # Green
        logging.WARNING: "\033[33m",   # Yellow
        logging.ERROR: "\033[31m",     # Red
        logging.CRITICAL: "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        use_colors: bool = True,
    ):
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors and sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        if self.use_colors:
            color = self.COLORS.get(record.levelno, "")
            record.levelname = f"{color}{record.levelname}{self.RESET}"

        return super().format(record)


class StructuredLogger(logging.Logger):
    """
    구조화된 로깅을 지원하는 사용자 정의 로거
    """

    def structured(
        self,
        level: int,
        msg: str,
        **kwargs: Any,
    ) -> None:
        """
        구조화된 데이터를 포함하여 로그를 출력합니다.

        Args:
            level: 로그 레벨
            msg: 메시지
            **kwargs: 구조화 데이터
        """
        if kwargs:
            extra_str = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            msg = f"{msg} | {extra_str}"
        self.log(level, msg)

    def info_struct(self, msg: str, **kwargs: Any) -> None:
        self.structured(logging.INFO, msg, **kwargs)

    def debug_struct(self, msg: str, **kwargs: Any) -> None:
        self.structured(logging.DEBUG, msg, **kwargs)

    def warning_struct(self, msg: str, **kwargs: Any) -> None:
        self.structured(logging.WARNING, msg, **kwargs)

    def error_struct(self, msg: str, **kwargs: Any) -> None:
        self.structured(logging.ERROR, msg, **kwargs)


# 커스텀 로거 클래스를 등록
logging.setLoggerClass(StructuredLogger)


def setup_logging(
    level: str = "INFO",
    log_file: Path | None = None,
    use_colors: bool = True,
    debug_mode: bool = False,
) -> None:
    """
    로깅을 설정합니다.

    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로 (지정 시 파일에도 출력)
        use_colors: 터미널 출력에 색상을 사용할지 여부
        debug_mode: 디버그 모드 (더 상세한 포맷)
    """
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    log_format = DEBUG_FORMAT if debug_mode else DEFAULT_FORMAT

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 기존 핸들러 정리
    root_logger.handlers.clear()

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter(log_format, use_colors=use_colors)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 파일 핸들러 (선택 사항)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # codegraph_mcp 이름 공간의 로거 설정
    pkg_logger = logging.getLogger("codegraph_mcp")
    pkg_logger.setLevel(log_level)


def get_logger(name: str) -> StructuredLogger:
    """
    지정한 이름의 로거를 가져옵니다.

    Args:
        name: 로거 이름 (보통 __name__)

    Returns:
        구조화 로깅을 지원하는 로거 인스턴스
    """
    return logging.getLogger(name)  # type: ignore


class LogContext:
    """
    로그 컨텍스트 매니저

    처리 시작/종료를 자동으로 로그로 남깁니다.

    Usage:
        with LogContext(logger, "Processing file"):
            process_file()
    """

    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        level: int = logging.INFO,
        **context,
    ):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.context = context
        self.start_time: datetime | None = None

    def __enter__(self) -> "LogContext":
        self.start_time = datetime.now()
        context_str = " | ".join(
            f"{k}={v}" for k, v in self.context.items()
        ) if self.context else ""

        msg = f"Starting: {self.operation}"
        if context_str:
            msg = f"{msg} | {context_str}"

        self.logger.log(self.level, msg)
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        elapsed = datetime.now() - self.start_time if self.start_time else None
        elapsed_ms = elapsed.total_seconds() * 1000 if elapsed else 0

        if exc_type is not None:
            self.logger.error(
                f"Failed: {self.operation} | "
                f"error={exc_type.__name__}: {exc_val} | "
                f"elapsed_ms={elapsed_ms:.2f}"
            )
        else:
            self.logger.log(
                self.level,
                f"Completed: {self.operation} | elapsed_ms={elapsed_ms:.2f}"
            )


class PerformanceLogger:
    """
    성능 측정용 로거

    Usage:
        perf = PerformanceLogger(logger)
        perf.mark("start")
        # ... processing ...
        perf.mark("after_parse")
        # ... more processing ...
        perf.mark("end")
        perf.report()
    """

    def __init__(self, logger: logging.Logger, operation: str = ""):
        self.logger = logger
        self.operation = operation
        self.marks: list[tuple[str, datetime]] = []

    def mark(self, name: str) -> None:
        """마크 포인트를 기록"""
        self.marks.append((name, datetime.now()))

    def report(self, level: int = logging.DEBUG) -> None:
        """측정 결과를 로그 출력"""
        if len(self.marks) < 2:
            return

        parts = []
        for i in range(1, len(self.marks)):
            prev_name, prev_time = self.marks[i - 1]
            curr_name, curr_time = self.marks[i]
            elapsed_ms = (curr_time - prev_time).total_seconds() * 1000
            parts.append(f"{prev_name}->{curr_name}: {elapsed_ms:.2f}ms")

        total_ms = (
            self.marks[-1][1] - self.marks[0][1]
        ).total_seconds() * 1000

        msg = f"Performance[{self.operation}] | " + " | ".join(parts)
        msg += f" | total: {total_ms:.2f}ms"

        self.logger.log(level, msg)
