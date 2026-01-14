# 기술 스택 (Technology Stack)

**Project**: CodeGraph MCP Server
**Last Updated**: 2025-12-11
**Version**: 2.8
**Synced With**: design-adr.md (ADR-001〜010), pyproject.toml (v0.8.0)

---

## Overview

본 문서는 CodeGraph MCP Server에서 **승인된 기술 스택**을 정의한다.  
모든 개발은 Phase -1 Gate(Article VIII: Anti-Abstraction)에서 **명시적으로 승인되지 않는 한**, 본 문서에 정의된 기술만 사용해야 한다.

**아키텍처 결정 근거**: 기술 선택의 배경은 `storage/specs/design-adr.md`를 참조한다.

---

## Primary Technologies

### Programming Language

| 언어 | 버전 | 용도 | 비고 |
|------|------|------|------|
| Python | 3.11+ | 애플리케이션 언어 | REQ-NFR-009 |
| SQL | SQLite 3 | 데이터베이스 쿼리 | SQLite 네이티브 |

### Runtime Environment

- **Python**: 3.11+ (REQ-NFR-009)
- **Package Manager**: pip / uv

---

## Core Dependencies

### MCP SDK (ADR-004)

| 라이브러리 | 버전 | 용도 | 요구사항 ID | ADR |
|------------|------|------|-------------|-----|
| mcp | >=1.0.0 | MCP 프로토콜 SDK | REQ-TRP-001~005 | ADR-004 |

### AST Parsing - Tree-sitter (ADR-003)

| 라이브러리 | 버전 | 용도 | 요구사항 ID | 비고 |
|-------------|------|------|-------------|------|
| tree-sitter | >=0.21.0 | AST 분석 기반 | REQ-AST-001~005 | |
| tree-sitter-python | >=0.21.0 | Python 분석 | REQ-AST-001 | |
| tree-sitter-javascript | >=0.21.0 | JavaScript 분석 | ✅ | |
| tree-sitter-typescript | >=0.21.0 | TypeScript 분석 | REQ-AST-002 | |
| tree-sitter-rust | >=0.21.0 | Rust 분석 | REQ-AST-003 | |
| tree-sitter-go | >=0.21.0 | Go 분석 | ✅ v0.2.0 | |
| tree-sitter-java | >=0.21.0 | Java 분석 | ✅ v0.2.0 | |
| tree-sitter-php | >=0.21.0 | PHP 분석 | ✅ v0.3.0 | |
| tree-sitter-c-sharp | >=0.21.0 | C# 분석 | ✅ v0.3.0 | |
| tree-sitter-cpp | >=0.21.0 | C++ 분석 | ✅ v0.3.0 | |
| tree-sitter-hcl | >=0.21.0 | HCL(Terraform) 분석 | ✅ v0.3.0 | |
| tree-sitter-ruby | >=0.21.0 | Ruby 분석 | ✅ v0.3.0 | |
| tree-sitter-kotlin | >=1.0.0 | Kotlin 분석 | ✅ v0.8.0 | |
| tree-sitter-swift | >=0.0.1 | Swift 분석 | ✅ v0.8.0 | |
| tree-sitter-scala | >=0.20.0 | Scala 분석 | ✅ v0.8.0 | |
| tree-sitter-lua | >=0.1.0 | Lua 분석 | ✅ v0.8.0 | |

### Database & Storage (ADR-002)

| 라이브러리 | 버전 | 용도 | 요구사항 ID | ADR |
|------------|------|------|-------------|-----|
| aiosqlite | >=0.19.0 | 비동기 SQLite | REQ-STR-001, REQ-GRF-005 | ADR-002 |

### 데이터 검증 (ADR-006)

| 라이브러리 | 버전 | 용도 | ADR |
|------------|------|------|-----|
| pydantic | >=2.0.0 | 데이터 검증 및 직렬화 | ADR-006 |
| pydantic-settings | >=2.0.0 | 환경 변수 관리 | - |

### 그래프 알고리즘 (ADR-005)

| 라이브러리 | 버전 | 용도 | 요구사항 ID | ADR |
|------------|------|------|-------------|-----|
| networkx | >=3.0 | 그래프 알고리즘(Louvain, PageRank 등) | REQ-SEM-003 | ADR-005 |

### 벡터 연산

| 라이브러리 | 버전 | 용도 | 요구사항 ID |
|------------|------|------|-------------|
| numpy | >=1.24.0 | 벡터 연산 | REQ-STR-003 |

### 유틸리티

| 라이브러리 | 버전 | 용도 | 요구사항 ID |
|------------|------|------|-------------|
| tiktoken | >=0.5.0 | 토큰 카운트 | - |
| watchfiles | >=0.21.0 | 파일 감시 | - |
| gitpython | >=3.1.0 | Git 조작 | REQ-STR-004 |
| rich | >=13.0.0 | CLI 출력 포맷 | REQ-CLI-003 |
| typer | >=0.9.0 | CLI 프레임워크 | REQ-CLI-001~004 |

---

## 선택적 의존성 (Optional Dependencies)

### 임베딩 (선택)

| 라이브러리 | 버전 | 용도 |
|------------|------|------|
| sentence-transformers | >=2.2.0 | 로컬 임베딩 |

### OpenAI 연동 (선택)

| 라이브러리 | 버전 | 용도 | 요구사항 ID |
|------------|------|------|-------------|
| openai | >=1.0.0 | OpenAI API | REQ-SEM-001~002 |

### Anthropic 연동 (선택)

| 라이브러리 | 버전 | 용도 | 요구사항 ID |
|------------|------|------|-------------|
| anthropic | >=0.18.0 | Anthropic Claude API | REQ-SEM-001~002 |

---

## 구현된 모듈 (Phase 3 기준)

### Core Modules

| 모듈 | 파일 | 설명 | 상태 |
|------|------|------|------|
| Parser | `core/parser.py` | Tree-sitter AST 분석 | ✅ Implemented |
| Graph | `core/graph.py` | NetworkX 그래프 엔진 | ✅ Implemented |
| Indexer | `core/indexer.py` | 리포지토리 인덱서 | ✅ Implemented |
| Community | `core/community.py` | Louvain 커뮤니티 탐지 | ✅ Implemented |
| Semantic | `core/semantic.py` | 시맨틱 분석 | ✅ Implemented |
| LLM | `core/llm.py` | 멀티 프로바이더 LLM 통합 | ✅ Implemented |
| GraphRAG | `core/graphrag.py` | GraphRAG 검색 | ✅ Implemented |

### MCP Modules

| 모듈 | 파일 | 설명 | 상태 |
|------|------|------|------|
| Tools | `mcp/tools.py` | MCP 툴(14종) | ✅ Implemented |
| Resources | `mcp/resources.py` | MCP 리소스(4종) | ✅ Implemented |
| Prompts | `mcp/prompts.py` | MCP 프롬프트(6종) | ✅ Implemented |

### Storage Modules

| 모듈 | 파일 | 설명 | 상태 |
|------|------|------|------|
| SQLite | `storage/sqlite.py` | SQLite 스토리지 | ✅ Implemented |
| Cache | `storage/cache.py` | 파일 캐시 | ✅ Implemented |
| Vectors | `storage/vectors.py` | 벡터 스토어 | ✅ Implemented |

---

## pyproject.toml 설정

```toml
[project]
name = "codegraph-mcp"
version = "0.1.0"
requires-python = ">=3.11"
description = "GraphRAG 기능을 포함한 코드 그래프 분석용 MCP 서버"
authors = [
    {name = "Your Name", email = "your@email.com"}
]
license = {text = "MIT"}
readme = "README.md"
keywords = ["mcp", "code-analysis", "graphrag", "ast", "tree-sitter"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "mcp>=1.0.0",
    "tree-sitter>=0.21.0",
    "tree-sitter-python>=0.21.0",
    "tree-sitter-javascript>=0.21.0",
    "tree-sitter-typescript>=0.21.0",
    "tree-sitter-rust>=0.21.0",
    "aiosqlite>=0.19.0",
    "pydantic>=2.0.0",
    "networkx>=3.0",
    "numpy>=1.24.0",
    "tiktoken>=0.5.0",
    "watchfiles>=0.21.0",
    "gitpython>=3.1.0",
    "rich>=13.0.0",
    "typer>=0.9.0",
]

[project.optional-dependencies]
embeddings = [
    "sentence-transformers>=2.2.0",
]
openai = [
    "openai>=1.0.0",
]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.scripts]
codegraph-mcp = "codegraph_mcp.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/codegraph_mcp"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true
```

---

## Testing Stack

### 테스트 프레임워크 (Test Frameworks)

| 라이브러리          | 버전       | 용도          |
| -------------- | -------- | ----------- |
| pytest         | >=7.0.0  | 테스트 러너      |
| pytest-asyncio | >=0.21.0 | 비동기 테스트     |
| pytest-cov     | >=4.0.0  | 테스트 커버리지 측정 |

### 테스트 가이드라인 (Article III, IX)

- **유닛 테스트 (Unit Tests)**: 목(mock) 사용 가능, 라이브러리 단위로 독립적으로 작성
- **통합 테스트 (Integration Tests)**: 실제 SQLite 데이터베이스 사용 (Article IX)
- **커버리지 (Coverage)**: 최소 80% 이상 필수

---

## 코드 품질 도구 (Code Quality Tools)

| 도구   | 버전      | 용도       |
| ---- | ------- | -------- |
| ruff | >=0.1.0 | 린터 & 포매터 |
| mypy | >=1.0.0 | 정적 타입 체크 |

### Ruff 설정 (Ruff Configuration)

```toml
[tool.ruff]
target-version = "py311"
line-length = 100
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = []

[tool.ruff.isort]
known-first-party = ["codegraph_mcp"]
```

---

## 성능 요구사항 (Performance Requirements)

| 지표              | 목표값              | 실측값 (v0.5.0)                | 요구사항 ID     |
| --------------- | ---------------- | --------------------------- | ----------- |
| 초기 인덱싱 (10만 라인) | < 30초            | **0.63초** (67 파일, 942 엔티티)  | REQ-NFR-001 |
| 증분 인덱싱          | < 2초             | < 0.5초                      | REQ-NFR-002 |
| 쿼리 응답 시간        | < 500ms          | < 2ms                       | REQ-NFR-003 |
| 기동 시간           | < 2초             | < 1초                        | REQ-NFR-004 |
| 메모리 사용량         | < 500MB          | 약 200MB                     | REQ-NFR-005 |
| 디스크 사용량         | < 100MB / 10만 라인 | 약 5MB                       | REQ-NFR-006 |
| 엔티티 처리량 (초당)    | -                | **1,495** (v0.5.0에서 47배 개선) | -           |

---

## 개발 도구 (Development Tools)

### 권장 IDE

- **Visual Studio Code** 및 확장 기능:
  - Python
  - Pylance
  - Ruff
  - GitLens

### 데이터베이스 도구 (Database Tools)

| 도구                    | 용도                 |
| --------------------- | ------------------ |
| DB Browser for SQLite | SQLite 데이터 확인      |
| SQLite CLI            | 커맨드라인 기반 SQLite 조작 |

---

## 안티 추상화 정책 (Anti-Abstraction Policy, Article VIII)

**중요 (CRITICAL)**: 프레임워크 API를 직접 사용해야 합니다.
임의의 커스텀 추상화 레이어를 생성하는 것은 금지합니다.

### ✅ 허용

```python
# Tree-sitter 직접 사용
parser = tree_sitter.Parser()
parser.set_language(tree_sitter_python.language())
tree = parser.parse(source_code)

# aiosqlite 직접 사용
async with aiosqlite.connect(db_path) as db:
    await db.execute("INSERT INTO entities ...")

# MCP 직접 사용
@mcp.tool()
async def query_codebase(query: str) -> list[CodeEntity]:
    ...
```

### ❌ 금지 (Phase -1 Gate 승인 없이는 불가)

```python
# ❌ 커스텀 데이터베이스 래퍼
class MyDatabase:
    async def find(self, id: str): ...  # aiosqlite를 래핑

# ❌ 커스텀 파서 래퍼
class MyParser:
    def parse(self, code: str): ...  # Tree-sitter를 래핑
```

---

## 보안 요구사항 (Security Requirements)

| 요구사항    | 설명               | 요구사항 ID     |
| ------- | ---------------- | ----------- |
| 셸 명령 실행 | 타임아웃 제한 적용       | REQ-NFR-012 |
| 파일 접근   | 지정된 리포지토리 경로로 제한 | REQ-NFR-013 |

---

## 호환성 요구사항 (Compatibility Requirements)

| 대상        | 요구사항                                          | 요구사항 ID     |
| --------- | --------------------------------------------- | ----------- |
| Python    | 3.11 이상                                       | REQ-NFR-009 |
| MCP 사양    | 1.0                                           | REQ-NFR-010 |
| MCP 클라이언트 | GitHub Copilot, Claude Code, Cursor, Windsurf | REQ-NFR-011 |

---

## Changelog

### Version 2.5 (2025-11-27)

- v0.7.0 릴리스:
    - watch 명령어: 파일 감시 및 자동 재인덱싱
    - GitHub Actions 기반 CI/CD 워크플로
    - watchfiles 라이브러리 활용
    - 커뮤니티 탐지 최적화: add_nodes_from() / add_edges_from() 배치 처리
    - executemany()를 통한 DB 쓰기 성능 개선
    - max_nodes=50000 샘플링으로 대규모 그래프 대응
    - 230K+ 엔티티 (Rust 컴파일러) 기준 검증 완료
테스트 결과: 308개 통과, 1개 스킵

### Version 2.0 (2025-11-27)

- 11개 언어 지원 (PHP, C#, C++, HCL, Ruby 추가)
- 성능 실측치 추가 (47배 개선)
- 배치 DB 쓰기 기반 최적화
- Phase 3 구현 완료에 따른 업데이트
- Anthropic SDK 추가 (LLM 통합)
- 구현 모듈(Implemented Modules) 섹션 추가
- ADR 참조 추가 (ADR-001 ~ ADR-010)
- 설계 문서(design-*.md)와 동기화
- pydantic-settings 추가

### Version 1.0 (2025-11-26)

- 기술 스택 최초 정의

---

**최종 업데이트**: 2025-11-27
**관리 주체**: ITDA SDD
