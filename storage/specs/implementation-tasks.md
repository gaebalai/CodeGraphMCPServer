# 구현 태스크 명세서

**Project**: CodeGraph MCP Server
**Version**: 1.0.0
**Created**: 2025-11-26
**Status**: Ready for Implementation
**Based On**: project-plan.md, design-*.md, requirements-specification.md

---

## 개요

이 문서는 CodeGraph MCP Server의 구현 태스크를 상세히 정의한다.  
각 태스크는 요구사항 ID, 설계 컴포넌트, 수용 기준을 명확히 하며  
Article V(트레이서빌리티)를 준수한다.

---

## Phase 1: Core Foundation (Week 1–2)

### Sprint 1.1: 프로젝트 기반 & AST 파서 (Week 1)

### TASK-001: 프로젝트 구조 셋업

| 항목 | 내용 |
|------|------|
| **예상 소요** | 4h |
| **우선순위** | P0 (Blocker) |
| **의존성** | 없음 |
| **담당** | Dev |

**설명**  
`steering/structure.md`에 정의된 규칙에 따라 프로젝트 디렉터리 구조를 생성한다.

**산출물**
```
src/codegraph_mcp/
├── __init__.py
├── __main__.py
├── server.py
├── config.py
├── core/
│   ├── __init__.py
│   ├── parser.py
│   ├── graph.py
│   ├── indexer.py
│   ├── community.py
│   └── semantic.py
├── storage/
│   ├── __init__.py
│   ├── sqlite.py
│   ├── cache.py
│   └── vectors.py
├── mcp/
│   ├── __init__.py
│   ├── tools.py
│   ├── resources.py
│   └── prompts.py
├── languages/
│   ├── __init__.py
│   ├── config.py
│   ├── python.py
│   ├── typescript.py
│   └── rust.py
└── utils/
    ├── __init__.py
    ├── git.py
    └── logging.py
tests/
├── unit/
├── integration/
├── e2e/
└── fixtures/
```

**수용 기준**
- [ ] 디렉터리 구조가 `steering/structure.md`와 일치
- [ ] 모든 `__init__.py`가 명확한 export 정의
- [ ] Article I (Library-First) 준수

---

### TASK-002: pyproject.toml 설정

| 항목 | 내용 |
|------|------|
| **예상 소요** | 2h |
| **우선순위** | P0 |
| **의존성** | TASK-001 |
| **요구사항 ID** | REQ-CLI-004 |

**설명**  
`steering/tech.md`에 정의된 기술 스택을 반영하여 `pyproject.toml`을 작성한다.

**산출물**
- `pyproject.toml` (의존성, 스크립트, 빌드 설정 포함)

**수용 기준**
- [ ] `pip install -e .` 성공
- [ ] `codegraph-mcp --help` 정상 동작
- [ ] 의존성이 `steering/tech.md`와 일치

---

### TASK-003: CI/CD 파이프라인 설정

| 항목 | 내용 |
|------|------|
| **예상 소요** | 4h |
| **우선순위** | P1 |
| **의존성** | TASK-002 |

**설명**  
GitHub Actions를 사용해 테스트, 린트, 타입 체크를 자동 실행한다.

**산출물**
- `.github/workflows/ci.yml`

**수용 기준**
- [ ] PR 시 자동 테스트 실행
- [ ] ruff lint 통과
- [ ] mypy 타입 체크 통과
- [ ] 커버리지 리포트 생성

---

### TASK-004: Python AST 파서 구현

| 항목 | 내용 |
|------|------|
| **예상 소요** | 8h |
| **우선순위** | P0 |
| **의존성** | TASK-001 |
| **요구사항 ID** | REQ-AST-001, REQ-AST-004 |
| **설계 참조** | design-core-engine.md §2.1 |

**설명**  
Tree-sitter를 사용하여 Python 파일을 분석하고,  
엔티티(함수, 클래스, 임포트)와 관계(호출, 임포트, 상속)를 추출한다.

**인터페이스**
```python
class ASTParser:
    def parse_file(self, file_path: Path) -> ParseResult:
        """파일을 파싱하여 엔티티와 관계를 추출"""
        
    def detect_language(self, file_path: Path) -> str | None:
        """확장자를 기반으로 언어 자동 감지"""

@dataclass
class ParseResult:
    entities: list[Entity]
    relations: list[Relation]
    errors: list[ParseError]
```

**추출 대상 (Python)**:
| Tree-sitter 노드        | 엔티티 타입   |
| --------------------- | -------- |
| function_definition   | FUNCTION |
| class_definition      | CLASS    |
| import_statement      | - (관계만)  |
| import_from_statement | - (관계만)  |
| call                  | - (관계만)  |

**수용 기준**:
- [ ] Python 함수 정의 추출
- [ ] Python 클래스 정의 추출
- [ ] import 관계 추출
- [ ] 함수 호출 관계 추출
- [ ] 상속 관계 추출
- [ ] 테스트 커버리지 80% 이상

---

#### TASK-005: TypeScript AST 파서 구현

| 항목          | 내용                         |
| ----------- | -------------------------- |
| **예상 소요**   | 8h                         |
| **우선순위**    | P0                         |
| **의존성**     | TASK-004                   |
| **요구사항 ID** | REQ-AST-002, REQ-AST-004   |
| **설계 참조**   | design-core-engine.md §2.1 |

**설명**:
Tree-sitter를 사용하여 TypeScript 파일을 분석한다.

**추출 대상 (TypeScript)**:
| Tree-sitter 노드        | 엔티티 타입    |
| --------------------- | --------- |
| function_declaration  | FUNCTION  |
| arrow_function        | FUNCTION  |
| method_definition     | METHOD    |
| class_declaration     | CLASS     |
| interface_declaration | INTERFACE |
| import_statement      | - (관계만)   |
| call_expression       | - (관계만)   |

**수용 기준**:
- [ ] TypeScript 함수 선언 / 화살표 함수 추출
- [ ] 클래스 / 인터페이스 선언 추출
- [ ] import 관계 추출
- [ ] 호출 관계 추출
- [ ] implements 관계 추출
- [ ] .ts, .tsx 모두 지원

---

#### TASK-006: 파서 유닛 테스트

| 항목          | 내용                 |
| ----------- | ------------------ |
| **예상 소요**   | 4h                 |
| **우선순위**    | P0                 |
| **의존성**     | TASK-004, TASK-005 |
| **요구사항 ID** | REQ-AST-005        |
| **Article** | III (Test-First)   |

## 설명
파서의 유닛 테스트를 작성한다. 구문 오류를 포함한 파일 처리도 검증한다.

## 테스트 케이스
1. 정상적인 Python 파일 파싱  
2. 정상적인 TypeScript 파일 파싱  
3. 구문 오류를 포함한 파일(부분 파싱 검증)  
4. 빈 파일  
5. 중첩된 클래스 및 함수  
6. 데코레이터가 적용된 함수  

## 수용 기준
- [ ] 모든 테스트 케이스 통과
- [ ] 구문 오류 발생 시 로그 기록
- [ ] 부분 파싱이 정상 동작
- [ ] 테스트 커버리지 80% 이상

---

## Sprint 1.2: 그래프 엔진 & 스토리지 (Week 2)

### TASK-007: SQLite 스키마 설계 및 구현

| 항목 | 내용 |
|------|------|
| **예상 소요** | 6h |
| **우선순위** | P0 |
| **의존성** | TASK-001 |
| **요구사항 ID** | REQ-GRF-005, REQ-GRF-006, REQ-STR-001 |
| **설계 참조** | design-storage.md §2 |

**설명**  
`design-storage.md`에 정의된 스키마를 구현한다.

**산출물**
```python
class SQLiteStorage:
    async def initialize(self) -> None:
        """스키마 생성 및 마이그레이션"""
        
    async def close(self) -> None:
        """연결 종료"""
```

**스키마**:
```sql
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    metadata TEXT,
    FOREIGN KEY (source_id) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE TABLE communities (
    id INTEGER PRIMARY KEY,
    level INTEGER NOT NULL,
    name TEXT,
    summary TEXT,
    member_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_file ON entities(file_path);
CREATE INDEX idx_entities_community ON entities(community_id);
CREATE INDEX idx_relations_source ON relations(source_id);
CREATE INDEX idx_relations_target ON relations(target_id);
CREATE INDEX idx_relations_type ON relations(type);
```

**수용 기준**:
- [ ] 스키마 생성 성공
- [ ] 인덱스 생성 성공
- [ ] 비동기 I/O 지원(aiosqlite)
- [ ] 마이그레이션 지원

---

#### TASK-008: 엔티티 CRUD 구현

| 항목          | 내용                       |
| ----------- | ------------------------ |
| **예상 소요**   | 4h                       |
| **우선순위**    | P0                       |
| **의존성**     | TASK-007                 |
| **요구사항 ID** | REQ-GRF-001, REQ-GRF-003 |

**인터페이스**:
```python
class SQLiteStorage:
    async def add_entity(self, entity: Entity) -> str:
        """엔티티 추가 후 ID 반환"""
        
    async def get_entity(self, entity_id: str) -> Entity | None:
        """ID로 엔티티 조회"""
        
    async def update_entity(self, entity: Entity) -> bool:
        """엔티티 수정"""
        
    async def delete_entity(self, entity_id: str) -> bool:
        """엔티티 삭제(카스케이드)"""
        
    async def find_entities(
        self,
        type: EntityType | None = None,
        file_path: str | None = None,
        name_pattern: str | None = None,
    ) -> list[Entity]:
        """조건 기반 검색"""
```

**수용 기준**:
- [ ] CRUD 동작 확인
- [ ] 배치 삽입 지원(1000건/배치)
- [ ] 검색 쿼리 정상 동작

---

#### TASK-009: 관계 CRUD 구현

| 항목          | 내용                       |
| ----------- | ------------------------ |
| **예상 소요**   | 4h                       |
| **우선순위**    | P0                       |
| **의존성**     | TASK-008                 |
| **요구사항 ID** | REQ-GRF-002, REQ-GRF-004 |

**인터페이스**:
```python
class SQLiteStorage:
    async def add_relation(self, relation: Relation) -> int:
        """관계 추가 후 ID 반환"""
        
    async def get_relations(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
        type: RelationType | None = None,
    ) -> list[Relation]:
        """조건 기반 검색"""
        
    async def delete_relations(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
    ) -> int:
        """관계 삭제 후 삭제 건수 반환"""
```

**수용 기준**:
- [ ] 관계 추가/조회/삭제 정상 동작
- [ ] 엔티티 삭제 시 카스케이드 삭제 확인

---

#### TASK-010: 그래프 쿼리 구현

| 항목          | 내용                         |
| ----------- | -------------------------- |
| **예상 소요**   | 6h                         |
| **우선순위**    | P0                         |
| **의존성**     | TASK-009                   |
| **요구사항 ID** | REQ-GRF-006                |
| **설계 참조**   | design-core-engine.md §2.2 |

**설명**:
NetworkX를 사용해 그래프 연산을 구현한다.

**인터페이스**:
```python
class GraphEngine:
    def __init__(self, storage: SQLiteStorage):
        self._storage = storage
        self._graph: nx.DiGraph | None = None
        
    async def load_graph(self) -> None:
        """DB에서 그래프를 메모리로 로드"""
        
    def find_callers(
        self,
        entity_id: str,
        max_depth: int = 3,
    ) -> list[CallPath]:
        """호출자 탐색"""
        
    def find_callees(
        self,
        entity_id: str,
        max_depth: int = 3,
    ) -> list[CallPath]:
        """피호출자 탐색"""
        
    def find_dependencies(
        self,
        entity_id: str,
        direction: Literal["upstream", "downstream", "both"],
        depth: int = 3,
    ) -> DependencyGraph:
        """의존성 그래프 조회"""
        
    def get_shortest_path(
        self,
        source_id: str,
        target_id: str,
    ) -> list[str] | None:
        """최단 경로 조회"""
```

**수용 기준**:
- [ ] 호출자/피호출자 탐색 정상 동작
- [ ] 의존성 그래프 조회 가능
- [ ] 깊이 제한 적용
- [ ] 순환 참조 처리

---

#### TASK-011: 파일 캐시 구현

| 항목          | 내용                   |
| ----------- | -------------------- |
| **예상 소요**   | 4h                   |
| **우선순위**    | P1                   |
| **의존성**     | TASK-007             |
| **요구사항 ID** | REQ-STR-002          |
| **설계 참조**   | design-storage.md §3 |

**설명**:
AST 파싱 결과를 캐시하고, 파일 변경 시에만 재파싱한다.

**인터페이스**:
```python
class CacheManager:
    def __init__(self, max_size: int = 500):
        self._ast_cache: dict[str, ParseResult] = {}
        
    def get_cached_ast(self, file_path: Path) -> ParseResult | None:
        """파일 해시 검증 후 캐시된 AST 반환"""
        
    def cache_ast(self, file_path: Path, result: ParseResult) -> None:
        """AST 캐시 저장"""
        
    def invalidate(self, file_path: Path) -> None:
        """캐시 무효화"""
        
    def clear(self) -> None:
        """전체 캐시 초기화"""
```

**수용 기준**:
- [ ] 파일 해시 기반 캐시 검증
- [ ] LRU 제거 정책(최대 500건)
- [ ] 캐시 히트 시 재파싱 방지

---

#### TASK-012: 인덱서 기반 구현

| 항목          | 내용                           |
| ----------- | ---------------------------- |
| **예상 소요**   | 6h                           |
| **우선순위**    | P0                           |
| **의존성**     | TASK-004, TASK-010, TASK-011 |
| **요구사항 ID** | REQ-IDX-001, REQ-IDX-004     |
| **설계 참조**   | design-core-engine.md §2.3   |

**설명**:
리포지토리 전체를 스캔하여 인덱스를 구축한다.

**인터페이스**:
```python
class Indexer:
    def __init__(
        self,
        parser: ASTParser,
        storage: SQLiteStorage,
        graph: GraphEngine,
        cache: CacheManager,
    ):
        ...
        
    async def index_repository(
        self,
        repo_path: Path,
        incremental: bool = True,
    ) -> IndexResult:
        """리포지토리 인덱싱"""
        
    def list_indexable_files(self, repo_path: Path) -> list[Path]:
        """.gitignore 규칙을 적용해 파일 목록 생성"""

@dataclass
class IndexResult:
    total_files: int
    indexed_files: int
    skipped_files: int
    entities_count: int
    relations_count: int
    errors: list[IndexError]
    duration_seconds: float
```

**수용 기준**:
- [ ] 전체 리포지토리 인덱싱 동작
- [ ] .gitignore 규칙 준수
- [ ] 진행 상황 로그 출력
- [ ] 오류 발생 시에도 처리 지속

---

#### TASK-013: 증분 인덱싱 구현

| 항목          | 내용                       |
| ----------- | ------------------------ |
| **예상 소요**   | 6h                       |
| **우선순위**    | P0                       |
| **의존성**     | TASK-012                 |
| **요구사항 ID** | REQ-IDX-002, REQ-STR-004 |

**설명**:
Git 차이를 이용해 변경된 파일만 재인덱싱한다.

**인터페이스**:
```python
class Indexer:
    async def get_changed_files(self, repo_path: Path) -> list[Path]:
        """Git diff 기반 변경 파일 조회"""
        
    async def index_incremental(self, repo_path: Path) -> IndexResult:
        """증분 인덱싱"""
```

**수용 기준**:
- [ ] Git 변경 파일 감지
- [ ] 변경 파일만 재인덱싱
- [ ] 삭제 파일에 대한 엔티티 제거
- [ ] 목표 2초 이내 완료

---

#### TASK-014: 그래프 엔진 테스트

| 항목          | 내용                 |
| ----------- | ------------------ |
| **예상 소요**   | 4h                 |
| **우선순위**    | P0                 |
| **의존성**     | TASK-010, TASK-013 |
| **Article** | III, IX            |

**설명**:
그래프 엔진과 스토리지 통합 테스트. 실제 SQLite 사용(Article IX 준수)

**테스트 케이스**:
1. 엔티티 CRUD
2. 관계 CRUD
3. 호출자/피호출자 탐색
4. 의존성 그래프
5. 증분 인덱싱
6. 성능 테스트(엔티티 1000개)

**수용 기준**:
- [ ] 모든 테스트 통과
- [ ] 실제 DB 사용(모킹 없음)
- [ ] 커버리지 80% 이상

---

## Phase 2: MCP 통합 (Week 3–4)

### Sprint 2.1: MCP 서버 기반 & 기본 툴 (Week 3)

#### TASK-015: MCP 서버 기반 구현

| 항목          | 내용                         |
| ----------- | -------------------------- |
| **예상 소요**   | 8h                         |
| **우선순위**    | P0                         |
| **의존성**     | TASK-012                   |
| **요구사항 ID** | REQ-TRP-001, REQ-TRP-004   |
| **설계 참조**   | design-mcp-interface.md §1 |

**설명**:
MCP SDK를 사용해 서버 기반을 구현한다.

**인터페이스**:
```python
class CodeGraphServer:
    def __init__(self, config: ServerConfig):
        self._server = Server("codegraph")
        self._indexer: Indexer | None = None
        self._graph: GraphEngine | None = None
        
    async def initialize(self, repo_path: Path) -> None:
        """서버 초기화 및 인덱스 로딩"""
        
    async def run(self) -> None:
        """서버 실행"""
```

**수용 기준**:
- [ ] stdio 트랜스포트 동작
- [ ] 초기화 시 인덱스 로딩
- [ ] 정상 종료 처리

---

#### TASK-016 ~ 021: 그래프 쿼리 툴 구현

각 툴의 상세는 `design-mcp-interface.md §2.1` 참조.

| 태스크 ID   | 툴 이름                     | 요구사항 ID     | 예상 |
| -------- | ------------------------ | ----------- | -- |
| TASK-016 | query_codebase           | REQ-TLS-001 | 4h |
| TASK-017 | find_dependencies        | REQ-TLS-002 | 4h |
| TASK-018 | find_callers             | REQ-TLS-003 | 4h |
| TASK-019 | find_callees             | REQ-TLS-004 | 4h |
| TASK-020 | find_implementations     | REQ-TLS-005 | 4h |
| TASK-021 | analyze_module_structure | REQ-TLS-006 | 4h |

**공통 수용 기준**:
- [ ] MCP Tool 사양 준수
- [ ] 에러 처리
- [ ] 유닛 테스트 포함

---

#### TASK-022: 그래프 쿼리 툴 테스트

| 항목        | 내용             |
| --------- | -------------- |
| **예상 소요** | 4h             |
| **우선순위**  | P0             |
| **의존성**   | TASK-016 ~ 021 |

**수용 기준**:
- [ ] 모든 툴 동작 확인
- [ ] 엣지 케이스 처리(존재하지 않는 엔티티 등)
- [ ] 커버리지 80% 이상

---

### Sprint 2.2: 코드 조회 툴 & 리소스 & CLI (Week 4)

#### TASK-023 ~ 026: 추가 툴 구현

| 태스크 ID   | 툴 이름               | 요구사항 ID     | 예상 |
| -------- | ------------------ | ----------- | -- |
| TASK-023 | get_code_snippet   | REQ-TLS-007 | 3h |
| TASK-024 | read_file_content  | REQ-TLS-008 | 2h |
| TASK-025 | get_file_structure | REQ-TLS-009 | 3h |
| TASK-026 | reindex_repository | REQ-TLS-013 | 3h |

---

#### TASK-027 ~ 029: 리소스 구현

| 태스크 ID   | 리소스                       | 요구사항 ID     | 예상 |
| -------- | ------------------------- | ----------- | -- |
| TASK-027 | codegraph://entities/{id} | REQ-RSC-001 | 2h |
| TASK-028 | codegraph://files/{path}  | REQ-RSC-002 | 2h |
| TASK-029 | codegraph://stats         | REQ-RSC-004 | 2h |

---

#### TASK-030: CLI serve 명령

| 항목          | 내용                       |
| ----------- | ------------------------ |
| **예상 소요**   | 4h                       |
| **우선순위**    | P0                       |
| **의존성**     | TASK-015                 |
| **요구사항 ID** | REQ-CLI-001, REQ-CLI-002 |

**명령 사양**:
```bash
codegraph-mcp serve [OPTIONS]

Options:
  --repo PATH      리포지토리 경로(기본값: 현재 디렉터리)
  --port INT       포트 번호(SSE용, 기본값: 3000)
  --transport STR  트랜스포트(stdio|sse, 기본값: stdio)
  --verbose        상세 로그 출력
```

**수용 기준**:
- [ ] `codegraph-mcp serve` 실행 가능
- [ ] `--repo` 옵션 동작
- [ ] Ctrl+C로 정상 종료

---

#### TASK-031: CLI help 명령

| 항목          | 내용          |
| ----------- | ----------- |
| **예상 소요**   | 2h          |
| **요구사항 ID** | REQ-CLI-003 |

**수용 기준**:
- [ ] `codegraph-mcp --help`로 사용법 표시
- [ ] 각 명령의 `--help` 지원

---

#### TASK-032: 패키징 설정

| 항목          | 내용          |
| ----------- | ----------- |
| **예상 소요**   | 2h          |
| **요구사항 ID** | REQ-CLI-004 |

**수용 기준**:
- [ ] `pip install codegraph-mcp` 정상 동작
- [ ] 필수 의존성 포함
- [ ] 엔트리 포인트 설정 정확

---

#### TASK-033: E2E 테스트(Claude Desktop)

| 항목          | 내용          |
| ----------- | ----------- |
| **예상 소요**   | 4h          |
| **의존성**     | TASK-030    |
| **요구사항 ID** | REQ-NFR-011 |

**테스트 내용**:
1. Claude Desktop설정 파일 생성
2. 서버 기동 확인
3. 툴 호출 확인
4. 리소스 접근 확인

**受け수용 기준入れ基準**:
- [ ] Claude Desktop에서 동작 확인
- [ ] 설정 예제 문서 작성

---

#### TASK-034: 성능 테스트

| 항목          | 내용                |
| ----------- | ----------------- |
| **예상 소요**   | 4h                |
| **의존성**     | TASK-032          |
| **요구사항 ID** | REQ-NFR-001 ~ 004 |

**테스트 대상**:
| 메트릭    | 목표            | 테스트 방법   |
| ------ | ------------- | -------- |
| 초기 인덱싱 | <30초 / 10만 라인 | 샘플 리포지토리 |
| 증분 인덱싱 | <2초           | 파일 1개 변경 |
| 쿼리 응답  | <500ms        | 각 툴      |
| 기동 시간  | <2초           | 서버 시작    |

**수용 기준**:
- [ ] 모든 성능 목표 달성
- [ ] 벤치마크 결과 기록

---

## Phase 3: GraphRAG 기능 (Week 5-6)

### Sprint 3.1: 커뮤니티 탐지 & 시맨틱 분석 (Week 5)

#### TASK-035: 커뮤니티 탐지 알고리즘

| 항목 | 내용 |
|------|------|
| **예상 소요** | 8h |
| **우선순위** | P1 |
| **요구사항 ID** | REQ-SEM-003, REQ-SEM-004 |
| **설계 참조** | design-core-engine.md §2.4 |

**설명**:  
NetworkX의 Louvain 알고리즘으로 커뮤니티 탐지를 구현한다.

**인터페이스**:
```python
class CommunityDetector:
    def detect_communities(
        self,
        graph: nx.DiGraph,
        resolution: float = 1.0,
    ) -> dict[int, list[str]]:
        """커뮤니티 탐지 후 {community_id: [entity_ids]} 반환"""
        
    def build_hierarchy(
        self,
        communities: dict[int, list[str]],
        levels: int = 2,
    ) -> list[Community]:
        """계층형 커뮤니티 구성"""
```

**수용 기준**:
- [ ] Louvain 방식으로 커뮤니티 탐지
- [ ] 계층 레벨 지원(0=세밀, 1=거침)
- [ ] 커뮤니티 ID를 엔티티에 할당

---

#### TASK-036~038: LLM 통합 & 요약 생성

| 태스크 ID   | 내용         | 요구사항 ID     | 예상 소요 |
| -------- | ---------- | ----------- | ----- |
| TASK-036 | LLM 통합 기반  | REQ-SEM-001 | 6h    |
| TASK-037 | 엔티티 설명 생성  | REQ-SEM-001 | 4h    |
| TASK-038 | 커뮤니티 요약 생성 | REQ-SEM-002 | 4h    |

---

#### TASK-039: 벡터 스토어 구현

| 항목          | 내용                   |
| ----------- | -------------------- |
| **예상 소요**   | 6h                   |
| **요구사항 ID** | REQ-STR-003          |
| **설계 참조**   | design-storage.md §4 |

**수용 기준**:
- [ ] 임베딩 저장
- [ ] 코사인 유사도 검색
- [ ] numpy 사용(외부 DB 불필요)

---

### Sprint 3.2: GraphRAG 툴 & 프롬프트 (Week 6)

#### TASK-042〜043: GraphRAG 툴

| 태스크 ID   | 툴             | 요구사항 ID     | 예상 소요 |
| -------- | ------------- | ----------- | ----- |
| TASK-042 | global_search | REQ-TLS-010 | 6h    |
| TASK-043 | local_search  | REQ-TLS-011 | 6h    |

---

#### TASK-045〜049: 프롬프트 템플릿

| 태스크 ID   | 프롬프트              | 요구사항 ID     | 예상 소요 |
| -------- | ----------------- | ----------- | ----- |
| TASK-045 | code_review       | REQ-PRM-001 | 2h    |
| TASK-046 | explain_codebase  | REQ-PRM-002 | 2h    |
| TASK-047 | implement_feature | REQ-PRM-003 | 2h    |
| TASK-048 | debug_issue       | REQ-PRM-004 | 2h    |
| TASK-049 | test_generation   | REQ-PRM-006 | 2h    |

---

## Phase 4: 마감 품질 개선 & 확장 (Week 7-8)

### Sprint 4.1: 추가 언어 & 확장 기능 (Week 7)

| 태스크 ID   | 내용                  | 요구사항 ID     | 예상 소요 |
| -------- | ------------------- | ----------- | ----- |
| TASK-051 | Rust AST 파서         | REQ-AST-003 | 8h    |
| TASK-052 | JavaScript AST 파서   | -           | 6h    |
| TASK-053 | SSE 트랜스포트           | REQ-TRP-002 | 6h    |
| TASK-054 | suggest_refactoring | REQ-TLS-012 | 6h    |

### Sprint 4.2: 문서화 & 릴리스 (Week 8)

| 태스크 ID   | 내용                   | 예상 소요 |
| -------- | -------------------- | ----- |
| TASK-057 | README.md            | 4h    |
| TASK-058 | API 문서               | 4h    |
| TASK-059 | 사용 예제 문서             | 4h    |
| TASK-060 | Claude Desktop 설정 예시 | 2h    |
| TASK-061 | 성능 최적화               | 8h    |
| TASK-062 | 최종 통합 테스트            | 4h    |
| TASK-063 | PyPI 릴리스 준비          | 4h    |
| TASK-064 | 릴리스 노트               | 2h    |

---

## 태스크 의존성 다이어그램

```
TASK-001 ─┬─ TASK-002 ─ TASK-003
          │
          ├─ TASK-004 ─┬─ TASK-005 ─ TASK-006
          │            │
          │            └─ TASK-012 ─ TASK-013 ─ TASK-014
          │                   │
          └─ TASK-007 ─ TASK-008 ─ TASK-009 ─ TASK-010 ─┘
                                                          │
                                                          └─ TASK-015 ─┬─ TASK-016~021 ─ TASK-022
                                                                       │
                                                                       ├─ TASK-023~029
                                                                       │
                                                                       └─ TASK-030~034 (MVP)
                                                                                │
                                                                                └─ TASK-035~050 (GraphRAG)
                                                                                        │
                                                                                        └─ TASK-051~064 (Polish)
```

---

## 추적성 매트릭스

| 태스크 ID   | 요구사항 ID                   | 설계 참조                     | 테스트      |
| -------- | ------------------------- | ------------------------- | -------- |
| TASK-004 | REQ-AST-001, 004          | design-core-engine §2.1   | TASK-006 |
| TASK-005 | REQ-AST-002, 004          | design-core-engine §2.1   | TASK-006 |
| TASK-007 | REQ-GRF-005, 006, STR-001 | design-storage §2         | TASK-014 |
| TASK-010 | REQ-GRF-006               | design-core-engine §2.2   | TASK-014 |
| TASK-012 | REQ-IDX-001, 004          | design-core-engine §2.3   | TASK-014 |
| TASK-015 | REQ-TRP-001, 004          | design-mcp-interface §1   | TASK-033 |
| TASK-016 | REQ-TLS-001               | design-mcp-interface §2.1 | TASK-022 |
| TASK-035 | REQ-SEM-003, 004          | design-core-engine §2.4   | TASK-041 |

---

## 변경 이력

| 버전    | 날짜         | 변경 내용 |
| ----- | ---------- | ----- |
| 1.0.0 | 2025-11-26 | 초판 작성 |

---

**문서 상태**: 구현 준비 완료(Ready for Implementation)
**헌법 준수 여부**: Article III (Test-First) ✓, Article V (Traceability) ✓
