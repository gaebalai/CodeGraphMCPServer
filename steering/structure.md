# Project Structure

**Project**: CodeGraph MCP Server
**Last Updated**: 2025-12-11
**Version**: 2.8
**Synced With**: design-architecture-overview.md, design-core-engine.md, design-mcp-interface.md, design-storage.md, pyproject.toml (v0.8.0)

---

## Architecture Pattern

**주요 패턴**: Library-First 아키텍처를 적용한 MCP Native Server (ADR-001)

CodeGraph MCP Server는 Microsoft GraphRAG의 컨셉을 참고하여 소스코드 분석에 최적화된 MCP 서버이다. 외부 데이터베이스가 필요 없는 자기완결형 아키텍처를 채택하며, 단일 바이너리 또는 pip install로 즉시 사용할 수 있다.

---

## Directory Organization

### Root Structure

```
codegraph-mcp/
├── pyproject.toml           # Project configuration
├── README.md                # Project documentation
├── LICENSE                  # License file
├── src/
│   └── codegraph_mcp/       # Main package
│       ├── __init__.py
│       ├── __main__.py      # CLI entry point (REQ-CLI-001~004)
│       ├── server.py        # MCP Server main (REQ-TRP-001~005)
│       ├── config.py        # Configuration management
│       │
│       ├── core/            # Core engine (Library-First)
│       │   ├── __init__.py
│       │   ├── parser.py    # Tree-sitter AST parser (REQ-AST-001~005)
│       │   ├── graph.py     # Graph engine (REQ-GRF-001~006)
│       │   ├── indexer.py   # Index management (REQ-IDX-001~004)
│       │   ├── community.py # Community detection (REQ-SEM-003~004)
│       │   └── semantic.py  # Semantic analysis (REQ-SEM-001~002)
│       │
│       ├── storage/         # Storage layer
│       │   ├── __init__.py
│       │   ├── sqlite.py    # SQLite storage (REQ-STR-001)
│       │   ├── cache.py     # File cache (REQ-STR-002)
│       │   └── vectors.py   # Vector store (REQ-STR-003)
│       │
│       ├── mcp/             # MCP interface layer
│       │   ├── __init__.py
│       │   ├── tools.py     # MCP Tools - 14 tools (REQ-TLS-001~014)
│       │   ├── resources.py # MCP Resources - 4 types (REQ-RSC-001~004)
│       │   └── prompts.py   # MCP Prompts - 6 prompts (REQ-PRM-001~006)
│       │
│       ├── languages/       # Language support
│       │   ├── __init__.py
│       │   ├── config.py    # Language configurations
│       │   ├── python.py    # Python parser
│       │   ├── typescript.py # TypeScript parser
│       │   └── rust.py      # Rust parser
│       │
│       └── utils/           # Utilities
│           ├── __init__.py
│           ├── git.py       # Git operations (REQ-STR-004)
│           └── logging.py   # Logging utilities
│
├── tests/                   # Test suites
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests (Article IX)
│   ├── e2e/                 # End-to-end tests
│   └── fixtures/            # Test fixtures
│
├── docs/                    # Documentation
│   └── Blog/               # Blog articles
│       ├── claude-code-linux-kernel-analysis.md
│       └── linux-kernel-analysis-with-codegraph-mcp.md
│
├── examples/                # Example configurations
│   ├── claude_desktop_config.json
│   └── sample_queries.md
│
├── README.md                # English documentation (default)
├── README.ko.md             # Korean documentation
├── RELEASE_NOTES.md         # English release notes
├── RELEASE_NOTES.ko.md      # Korean release notes
├── CHANGELOG.md             # English changelog
├── CHANGELOG.ko.md          # Korean changelog
│
├── steering/                # Project memory (ITDA SDD)
│   ├── structure.md         # This file
│   ├── tech.md              # Technology stack
│   ├── product.md           # Product context
│   └── rules/               # Constitutional governance
│
├── storage/                 # SDD artifacts
│   ├── specs/               # Requirements, design, tasks
│   ├── changes/             # Delta specifications
│   └── features/            # Feature tracking
│
└── templates/               # Document templates
```

---

## Library-First Pattern (Article I)

### Core Libraries

모든 기능은 `src/codegraph_mcp/core/`에 독립 라이브러리로 구현된다.

#### 1. AST Parser Library (`core/parser.py`)

```python
# REQ-AST-001 ~ REQ-AST-005 구현
class ASTParser:
    """Tree-sitter 기반 AST 분석 라이브러리"""
    
    def parse_file(self, file_path: str, language: str) -> ParseResult:
        """파일을 분석해 AST 정보를 추출"""
        
    def extract_entities(self, ast: Tree) -> list[Entity]:
        """AST에서 엔티티(함수, 클래스 등) 추출"""
```

#### 2. Graph Engine Library (`core/graph.py`)

```python
# REQ-GRF-001 ~ REQ-GRF-006 を実装
class GraphEngine:
    """SQLite 기반 그래프 엔진 라이브러리"""
    
    def add_entity(self, entity: Entity) -> str:
        """엔티티를 그래프에 추가"""
        
    def add_relation(self, source_id: str, target_id: str, type: str) -> int:
        """관계를 그래프에 추가"""
        
    def query(self, query: GraphQuery) -> QueryResult:
        """그래프 쿼리 실행"""
```

#### 3. Semantic Analyzer Library (`core/semantic.py`)

```python
# REQ-SEM-001 ~ REQ-SEM-004 구현
class SemanticAnalyzer:
    """LLM 기반 시맨틱 분석 라이브러리"""
    
    async def generate_description(self, entity: Entity) -> str:
        """엔티티 자연어 설명 생성"""
        
    async def generate_community_summary(self, community: Community) -> str:
        """커뮤니티 요약 생성"""
```

#### 4. Indexer Library (`core/indexer.py`)

```python
# REQ-IDX-001 ~ REQ-IDX-004 구현
class Indexer:
    """리포지토리 인덱스 관리 라이브러리"""
    
    def index_repository(self, path: str, incremental: bool = True) -> IndexResult:
        """리포지토리 인덱싱"""
        
    def get_changed_files(self, path: str) -> list[str]:
        """Git diff로 변경 파일 조회"""
```

### Library Guidelines

- **독립성(Independence)**: 라이브러리는 애플리케이션 코드에 의존하지 않는다
- **Public API**: 모든 export는 `__init__.py`를 통해 제공한다
- **테스트(Testing)**: 독립된 테스트 스위트를 유지한다
- **CLI**: 각 라이브러리는 CLI 인터페이스를 공개한다(Article II)

---

## CLI Interface (Article II)

### CLI Entry Point (`__main__.py`)

```bash
# 서버 기동
codegraph-mcp serve --repo /path/to/project

# 인덱스 생성
codegraph-mcp index /path/to/project

# 쿼리 실행(디버그용)
codegraph-mcp query "find all functions that call authenticate"

# 도움말 표시
codegraph-mcp --help
```

### CLI Commands

| 명령      | 설명         | 요구사항 ID     |
| ------- | ---------- | ----------- |
| `serve` | MCP 서버를 기동 | REQ-CLI-001 |
| `index` | 리포지토리를 인덱싱 | REQ-IDX-001 |
| `query` | 그래프 쿼리를 실행 | REQ-TLS-001 |
| `stats` | 통계 정보를 표시  | REQ-RSC-004 |

---

## MCP Interface Organization

### Tools (`mcp/tools.py`)

14개 툴을 아래 카테고리로 정리:

```python
# 그래프 쿼리 툴 (REQ-TLS-001 ~ REQ-TLS-006)
- query_codebase
- find_dependencies
- find_callers
- find_callees
- find_implementations
- analyze_module_structure

# 코드 조회 툴 (REQ-TLS-007 ~ REQ-TLS-009)
- get_code_snippet
- read_file_content
- get_file_structure

# GraphRAG 툴 (REQ-TLS-010 ~ REQ-TLS-011)
- global_search
- local_search

# 편집·관리 툴 (REQ-TLS-012 ~ REQ-TLS-014)
- suggest_refactoring
- reindex_repository
- execute_shell_command
```

### Resources (`mcp/resources.py`)

4개 리소스 타입:

```python
# REQ-RSC-001 ~ REQ-RSC-004
- codegraph://entities/{entity_id}
- codegraph://files/{file_path}
- codegraph://communities/{community_id}
- codegraph://stats
```

### Prompts (`mcp/prompts.py`)

6개 프롬프트 템플릿:

```python
# REQ-PRM-001 ~ REQ-PRM-006
- code_review
- explain_codebase
- implement_feature
- debug_issue
- refactor_guidance
- test_generation
```

---

## Storage Layer Organization

### SQLite Schema (`storage/sqlite.py`)

```sql
-- 엔티티 테이블 (REQ-GRF-003)
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    qualified_name TEXT,
    file_path TEXT,
    start_line INTEGER,
    end_line INTEGER,
    signature TEXT,
    docstring TEXT,
    source_code TEXT,
    embedding BLOB,
    community_id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 관계 테이블 (REQ-GRF-004)
CREATE TABLE relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    metadata TEXT,
    FOREIGN KEY (source_id) REFERENCES entities(id),
    FOREIGN KEY (target_id) REFERENCES entities(id)
);

-- 커뮤니티 테이블 (REQ-SEM-003)
CREATE TABLE communities (
    id INTEGER PRIMARY KEY,
    level INTEGER NOT NULL,
    name TEXT,
    summary TEXT,
    member_count INTEGER,
    created_at TIMESTAMP
);

-- 인덱스 (REQ-GRF-006)
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_file ON entities(file_path);
CREATE INDEX idx_entities_community ON entities(community_id);
CREATE INDEX idx_relations_source ON relations(source_id);
CREATE INDEX idx_relations_target ON relations(target_id);
CREATE INDEX idx_relations_type ON relations(type);
```

---

## Test Organization

### Test Structure

```
tests/
├── unit/                    # 유닛 테스트
│   ├── test_parser.py       # AST 파서 테스트
│   ├── test_graph.py        # 그래프 엔진 테스트
│   └── test_semantic.py     # 시맨틱 분석 테스트
├── integration/             # 통합 테스트 (Article IX)
│   ├── test_indexer.py      # 인덱서 통합 테스트
│   ├── test_tools.py        # MCP 툴 통합 테스트
│   └── test_mcp_server.py   # MCP 서버 통합 테스트
├── e2e/                     # E2E 테스트
│   └── test_client_workflow.py
└── fixtures/
    ├── sample_repos/        # 테스트용 샘플 리포지토리
    │   ├── python_project/
    │   └── typescript_project/
    └── expected_outputs/    # 기대 출력
```

### Test Guidelines (Article III, IX)

- **Test-First**: 테스트는 구현 전에 작성
- **Real Services**: 통합 테스트는 실제 SQLite를 사용
- **Coverage**: 최소 80% 커버리지
- **Naming**: `test_*.py` 또는 `*_test.py`

---

## Requirements Traceability

### Component → Requirements Mapping

| 컴포넌트                 | 요구사항 ID                   | 설명          |
| -------------------- | ------------------------- | ----------- |
| `core/parser.py`     | REQ-AST-001 ~ REQ-AST-005 | AST 파서      |
| `core/graph.py`      | REQ-GRF-001 ~ REQ-GRF-006 | 그래프 엔진      |
| `core/semantic.py`   | REQ-SEM-001 ~ REQ-SEM-004 | 시맨틱 분석      |
| `core/indexer.py`    | REQ-IDX-001 ~ REQ-IDX-004 | 인덱스 관리      |
| `storage/sqlite.py`  | REQ-STR-001, REQ-GRF-005  | SQLite 스토리지 |
| `storage/cache.py`   | REQ-STR-002               | 파일 캐시       |
| `storage/vectors.py` | REQ-STR-003               | 벡터 스토어      |
| `mcp/tools.py`       | REQ-TLS-001 ~ REQ-TLS-014 | MCP 툴       |
| `mcp/resources.py`   | REQ-RSC-001 ~ REQ-RSC-004 | MCP 리소스     |
| `mcp/prompts.py`     | REQ-PRM-001 ~ REQ-PRM-006 | MCP 프롬프트    |
| `server.py`          | REQ-TRP-001 ~ REQ-TRP-005 | MCP 서버      |
| `__main__.py`        | REQ-CLI-001 ~ REQ-CLI-004 | CLI         |

---

## Deployment Structure

### Deployment Units

**Projects** (independently deployable):

1. **codegraph-mcp** - Main MCP server package (pip installable)

> ✅ **Simplicity Gate (Article VII)**: 1 project - compliant

### Distribution

- **PyPI**: `pip install codegraph-mcp`
- **GitHub Releases**: Pre-built binaries (optional)

---

## Naming Conventions

### File Naming

- **Python Modules**: `snake_case.py` (e.g., `ast_parser.py`)
- **Classes**: `PascalCase` (e.g., `GraphEngine`)
- **Functions/Methods**: `snake_case` (e.g., `find_callers`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `MAX_DEPTH`)
- **Tests**: `test_*.py` (e.g., `test_parser.py`)

### Variable Naming

- **Variables**: `snake_case`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Types**: `PascalCase`
- **Private members**: `_leading_underscore`

---

## Version Control

### Branch Organization

- `main` - Production branch
- `develop` - Development branch
- `feature/*` - Feature branches
- `hotfix/*` - Hotfix branches

### Commit Message Convention

```
<type>(<scope>): <subject>

<body>

Refs: <REQ-ID>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Example**:
```
feat(parser): implement Python AST parsing

Add Tree-sitter based Python parsing with function,
class, and import extraction.

Refs: REQ-AST-001
```

---

## Constitutional Compliance

This structure enforces:

- **Article I**: Library-first pattern in `core/`
- **Article II**: CLI interfaces via `__main__.py`
- **Article III**: Test structure supports Test-First
- **Article VI**: Steering files maintain project memory
- **Article VII**: Single project - compliant
- **Article VIII**: Direct framework usage (no abstraction layers)
- **Article IX**: Integration tests use real SQLite

---

## Implementation Status (Phase 4 Complete)

### Core Modules ✅

| 파일 | 라인 수 | 상태 | 설명 |
|------|--------|------|------|
| `core/parser.py` | ~400 | ✅ Complete | Tree-sitter AST 분석 |
| `core/graph.py` | ~500 | ✅ Complete | NetworkX 그래프 엔진 |
| `core/indexer.py` | ~350 | ✅ Complete | 리포지토리 인덱서 |
| `core/community.py` | ~200 | ✅ Complete | Louvain 커뮤니티 탐지 |
| `core/semantic.py` | ~300 | ✅ Complete | 시맨틱 분석 |
| `core/llm.py` | ~350 | ✅ Complete | 멀티 프로바이더 LLM 통합 |
| `core/graphrag.py` | ~300 | ✅ Complete | GraphRAG 검색 |

### Language Modules ✅ (v0.3.0+ 기준 11개 언어)

| 파일 | 라인 수 | 상태 | 설명 |
|------|--------|------|------|
| `languages/python.py` | ~200 | ✅ Complete | Python AST 추출기 |
| `languages/typescript.py` | ~250 | ✅ Complete | TypeScript AST 추출기 |
| `languages/javascript.py` | ~100 | ✅ Complete | JavaScript AST 추출기 |
| `languages/rust.py` | ~300 | ✅ Complete | Rust AST 추출기 |
| `languages/go.py` | ~250 | ✅ v0.2.0 | Go AST 추출기 |
| `languages/java.py` | ~280 | ✅ v0.2.0 | Java AST 추출기 |
| `languages/php.py` | ~250 | ✅ v0.3.0 | PHP AST 추출기 |
| `languages/csharp.py` | ~280 | ✅ v0.3.0 | C# AST 추출기 |
| `languages/cpp.py` | ~300 | ✅ v0.3.0 | C++ AST 추출기 |
| `languages/hcl.py` | ~200 | ✅ v0.3.0 | HCL(Terraform) AST 추출기 |
| `languages/ruby.py` | ~250 | ✅ v0.3.0 | Ruby AST 추출기 |

### MCP Modules ✅

| 파일 | 라인 수 | 상태 | 설명 |
|------|--------|------|------|
| `mcp/tools.py` | ~600 | ✅ Complete | 14개 MCP 툴 |
| `mcp/resources.py` | ~200 | ✅ Complete | 4개 MCP 리소스 |
| `mcp/prompts.py` | ~300 | ✅ Complete | 6개 MCP 프롬프트 |

### Storage Modules ✅

| 파일 | 라인 수 | 상태 | 설명 |
|------|--------|------|------|
| `storage/sqlite.py` | ~400 | ✅ Complete | SQLite 스토리지 |
| `storage/cache.py` | ~150 | ✅ Complete | 파일 캐시 |
| `storage/vectors.py` | ~250 | ✅ Complete | 벡터 스토어 |

### Documentation ✅

| 파일 | 상태 | 설명 |
|------|------|------|
| `docs/api.md` | ✅ Complete | API 레퍼런스 |
| `docs/configuration.md` | ✅ Complete | 설정 가이드 |
| `docs/examples.md` | ✅ Complete | 사용 예시 |
| `CHANGELOG.md` | ✅ Complete | 변경 이력 |
| `RELEASE_NOTES.md` | ✅ Complete | 릴리스 노트 |

### Test Coverage (v0.7.0)

| Directory | Tests | Status |
|-----------|-------|--------|
| `tests/unit/` | 220+ | ✅ All Pass |
| `tests/integration/` | 50+ | ✅ All Pass |
| `tests/e2e/` | 10+ | ✅ All Pass |
| **Total** | **309** | **308 passed, 1 skipped** |

### Release Artifacts (v0.7.0)

| File | Size | Status |
|------|------|--------|
| `codegraph_mcp_server-0.7.0-py3-none-any.whl` | ~115KB | ⏳ Pending |
| `codegraph_mcp_server-0.7.0.tar.gz` | ~120KB | ⏳ Pending |

### Release History

| Version | Date | Highlights |
|---------|------|------------|
| v0.1.0 | 2025-11-26 | Initial: Python, TS, JS, Rust |
| v0.2.0 | 2025-11-27 | +Go, Java |
| v0.3.0 | 2025-11-27 | +PHP, C#, C++, HCL, Ruby (11 languages) |
| v0.4.0 | 2025-11-27 | CLI Progress Display |
| v0.5.0 | 2025-11-27 | 47x Performance (Batch DB) |
| v0.6.0 | 2025-11-27 | Background Server Management |
| v0.6.1 | 2025-11-27 | SSE/Unicode Fixes |
| v0.6.2 | 2025-11-27 | Partial ID, Auto Community, Large Repo Support |
| **v0.7.0** | **2025-11-27** | **File Watch, GitHub Actions CI/CD** |

---

## Changelog

### Version 2.5 (2025-11-27)

- v0.7.0 릴리스:
  - `watch` 명령: 파일 감시 및 자동 재인덱싱
  - GitHub Actions CI/CD 워크플로우 추가
  - 대규모 리포지토리 대응 (230K+ 엔티티)
  - 커뮤니티 탐지 최적화 (배치 처리, 샘플링)
  - Rust 컴파일러 리포지토리에서 검증 완료
- 테스트 카운트: 309 (308 passed, 1 skipped)

### Version 2.3 (2025-11-27)

- v0.5.0 릴리스에 따른 업데이트
- 11개 언어 파서 모듈 추가
- 테스트 카운트: 286 (285 passed, 1 skipped)
- 성능 개선: 47배 고속화 (배치 DB 쓰기)
- Release History 추가

### Version 2.1 (2025-11-26)

- Phase 4 완료 반영
- Language Modules 추가 (javascript.py)
- Documentation 추가 (docs/)
- Release Artifacts 추가
- 전체 모듈 구현 현황 기록
- 테스트 커버리지 정보 추가
- 설계 문서 (design-*.md)와 동기화
- ADR-001 참조 추가
- 설계 문서로의 트레이서빌리티 추가
- 테스트 수: 173 → 182

### Version 1.0 (2025-11-26)

- 초기 구조 작성

---

**최종 업데이트**: 2025-11-27
**관리 주체**: ITDA SDD
