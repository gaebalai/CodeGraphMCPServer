# CodeGraph MCP Server 설계서

## 1. 경영 요약 (Executive Summary)

### 1.1 프로젝트 개요

**CodeGraph MCP Server**는 Microsoft GraphRAG의 개념과 code-graph-rag의 구현을 참고하여,
소스 코드 분석에 최적화된 MCP(Model Context Protocol) 서버입니다.
GitHub Copilot, Claude Code, 기타 MCP 대응 AI 도구로부터 코드베이스에 대한 구조적 이해와 **효율적인 코드 보완(자동 완성)**을 실현합니다.

### 1.2 code-graph-rag와의 차별화

| 관점          | code-graph-rag   | CodeGraph MCP Server      |
| ----------- | ---------------- | ------------------------- |
| 아키텍처        | CLI + 인터랙티브 모드   | MCP 네이티브 서버               |
| 그래프 DB      | Memgraph (외부 의존) | **SQLite + 내장 그래프 엔진**    |
| 배포          | Docker 필수        | **단일 바이너리 / pip install** |
| 기동 시간       | 무거움 (DB 기동 포함)   | **경량 (초 단위)**             |
| MCP 통합      | 사후 대응            | **네이티브 설계**               |
| 스코프         | 단일 리포지토리         | **멀티 리포지토리 지원**           |
| 인덱스 업데이트    | 수동 / 파일 감시       | **Git 차분 기반 증분 업데이트**     |
| GraphRAG 기능 | 없음               | **커뮤니티 요약 · 글로벌 쿼리**      |

### 1.3 주요 설계 목표

1. **제로 구성 기동**: `pip install codegraph-mcp && codegraph-mcp serve`만으로 즉시 사용 가능
2. **경량·고속**: 외부 DB 없이 10만 라인 규모 코드베이스를 10초 이내로 인덱싱
3. **MCP First**: Tools, Resources, Prompts를 모두 활용하는 포괄적인 MCP 구현
4. **증분 업데이트**: Git 차분을 활용하여 변경된 파일만 재인덱싱
5. **GraphRAG 통합**: LLM을 활용한 코드 시맨틱 이해 및 커뮤니티 요약 제공

---

## 2. 시스템 아키텍처

### 2.1 전체 구성

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MCP Clients                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │GitHub Copilot│  │ Claude Code │  │   Cursor    │  │   Windsurf  │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
└─────────┼────────────────┼────────────────┼────────────────┼───────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CodeGraph MCP Server                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      MCP Protocol Layer                          │   │
│  │  • stdio / SSE / Streamable HTTP Transport                       │   │
│  │  • JSON-RPC 2.0 Message Handling                                 │   │
│  │  • OAuth 2.1 Authentication (optional)                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                     │
│  ┌────────────────┬───────────────┼───────────────┬────────────────┐   │
│  │    Tools       │   Resources   │    Prompts    │   Sampling     │   │
│  │  (14 tools)    │ (4 resource   │  (6 prompts)  │  (LLM calls)   │   │
│  │                │   types)      │               │                │   │
│  └───────┬────────┴───────┬───────┴───────┬───────┴────────┬───────┘   │
│          │                │               │                │           │
│  ┌───────┴────────────────┴───────────────┴────────────────┴───────┐   │
│  │                      Core Engine                                 │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │   │
│  │  │  AST Parser  │  │ Graph Engine │  │   Semantic Analyzer  │   │   │
│  │  │ (Tree-sitter)│  │  (In-memory  │  │   (LLM-powered)      │   │   │
│  │  │              │  │   + SQLite)  │  │                      │   │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │   │
│  │         │                 │                     │               │   │
│  │  ┌──────┴─────────────────┴─────────────────────┴───────────┐   │   │
│  │  │                   Knowledge Graph                         │   │   │
│  │  │  • Entities: File, Module, Class, Function, Method       │   │   │
│  │  │  • Relations: CALLS, IMPORTS, INHERITS, CONTAINS         │   │   │
│  │  │  • Communities: Module clusters with summaries           │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Storage Layer                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │   SQLite    │  │  File Cache │  │   Vector Store          │  │   │
│  │  │ (Graph DB)  │  │  (AST cache)│  │   (Embeddings)          │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 컴포넌트 상세

#### 2.2.1 AST 파서 (Tree-sitter 기반)

```python
# 지원 언어 및 추출 대상
LANGUAGE_CONFIG = {
    "python": {
        "extensions": [".py"],
        "function_nodes": ["function_definition"],
        "class_nodes": ["class_definition"],
        "import_nodes": ["import_statement", "import_from_statement"],
        "call_nodes": ["call"],
    },
    "typescript": {
        "extensions": [".ts", ".tsx"],
        "function_nodes": ["function_declaration", "arrow_function", "method_definition"],
        "class_nodes": ["class_declaration", "interface_declaration"],
        "import_nodes": ["import_statement"],
        "call_nodes": ["call_expression"],
    },
    "rust": {
        "extensions": [".rs"],
        "function_nodes": ["function_item"],
        "class_nodes": ["struct_item", "enum_item", "impl_item"],
        "import_nodes": ["use_declaration"],
        "call_nodes": ["call_expression"],
    },
    # ... 기타 언어
}
```

#### 2.2.2 Graph Engine

**스키마 설계:**

```sql
-- Nodes
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,  -- 'file', 'module', 'class', 'function', 'method'
    name TEXT NOT NULL,
    qualified_name TEXT,
    file_path TEXT,
    start_line INTEGER,
    end_line INTEGER,
    signature TEXT,
    docstring TEXT,
    source_code TEXT,
    embedding BLOB,      -- Vector embedding for semantic search
    community_id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Edges
CREATE TABLE relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'CALLS', 'IMPORTS', 'INHERITS', 'CONTAINS', 'IMPLEMENTS'
    weight REAL DEFAULT 1.0,
    metadata TEXT,       -- JSON for additional properties
    FOREIGN KEY (source_id) REFERENCES entities(id),
    FOREIGN KEY (target_id) REFERENCES entities(id)
);

-- Community summaries (GraphRAG feature)
CREATE TABLE communities (
    id INTEGER PRIMARY KEY,
    level INTEGER NOT NULL,  -- Hierarchy level (0=fine, 1=coarse, ...)
    name TEXT,
    summary TEXT,            -- LLM-generated summary
    member_count INTEGER,
    created_at TIMESTAMP
);

-- Indexes for fast queries
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_file ON entities(file_path);
CREATE INDEX idx_entities_community ON entities(community_id);
CREATE INDEX idx_relations_source ON relations(source_id);
CREATE INDEX idx_relations_target ON relations(target_id);
CREATE INDEX idx_relations_type ON relations(type);
```

#### 2.2.3 시맨틱 분석기 (Semantic Analyzer, GraphRAG 기능)

```python
class SemanticAnalyzer:
    """LLM을 사용한 코드 시맨틱 분석"""
    
    async def generate_entity_description(self, entity: Entity) -> str:
        """엔티티의 자연어 설명을 생성"""
        prompt = f"""
        아래 코드 엔티티에 대해, 그 목적과 기능을 1~2문장으로 설명해 주세요.
        
        Type: {entity.type}
        Name: {entity.name}
        Signature: {entity.signature}
        Docstring: {entity.docstring}
        Code:
        ```
        {entity.source_code[:500]}
        ```
        """
        return await self.llm.complete(prompt)
    
    async def generate_community_summary(self, community: Community) -> str:
        """모듈 커뮤니티의 요약을 생성"""
        members = self.graph.get_community_members(community.id)
        prompt = f"""
        아래 코드 모듈 그룹은 서로 관련된 컴포넌트의 클러스터입니다.
        이 클러스터의 주요 책임과 기능을 요약해 주세요.
        
        구성원:
        {self._format_members(members)}
        
        관계:
        {self._format_relations(members)}
        """
        return await self.llm.complete(prompt)
```

---

## 3. MCP 인터페이스 설계

### 3.1 Tools (총 14개)

#### 3.1.1 그래프 쿼리 도구

```python
@mcp.tool()
async def query_codebase(
    query: str,
    scope: Literal["all", "functions", "classes", "files"] = "all",
    limit: int = 10
) -> list[CodeEntity]:
    """
    자연어로 코드베이스를 검색합니다.
    
    Examples:
    - "사용자 인증과 관련된 클래스를 찾아줘"
    - "데이터베이스 연결을 수행하는 함수"
    - "API 엔드포인트 정의"
    """

@mcp.tool()
async def find_dependencies(
    entity_name: str,
    direction: Literal["upstream", "downstream", "both"] = "both",
    depth: int = 2
) -> DependencyGraph:
    """
    지정한 엔티티의 의존 관계를 조회합니다.
    
    - upstream: 이 엔티티가 의존하는 대상
    - downstream: 이 엔티티에 의존하는 대상
    """

@mcp.tool()
async def find_callers(function_name: str, max_depth: int = 3) -> list[CallPath]:
    """지정한 함수를 호출하는 모든 함수를 조회"""

@mcp.tool()
async def find_callees(function_name: str, max_depth: int = 3) -> list[CallPath]:
    """지정한 함수가 호출하는 모든 함수를 조회"""

@mcp.tool()
async def find_implementations(interface_name: str) -> list[CodeEntity]:
    """인터페이스/추상 클래스의 구현체를 검색"""

@mcp.tool()
async def analyze_module_structure(module_path: str) -> ModuleAnalysis:
    """모듈 구조 분석 (클래스, 함수, 의존 관계 개요)"""
```

#### 3.1.2 코드 조회 도구

```python
@mcp.tool()
async def get_code_snippet(
    entity_name: str,
    include_context: bool = True,
    context_lines: int = 5
) -> CodeSnippet:
    """
    엔티티의 소스 코드를 조회합니다.
    include_context=True 인 경우, 앞뒤 문맥도 함께 포함합니다.
    """

@mcp.tool()
async def read_file_content(
    file_path: str,
    start_line: int | None = None,
    end_line: int | None = None
) -> FileContent:
    """파일 내용을 읽어옵니다"""

@mcp.tool()
async def get_file_structure(file_path: str) -> FileStructure:
    """파일 내부의 클래스·함수 구조를 조회"""
```

#### 3.1.3 GraphRAG 도구

```python
@mcp.tool()
async def global_search(
    query: str,
    community_level: int = 1
) -> GlobalSearchResult:
    """
    코드베이스 전체에 대한 글로벌 질문에 답변합니다.
    커뮤니티 요약을 활용하여 매크로 레벨의 이해를 제공합니다.
    
    Examples:
    - "이 프로젝트의 주요 아키텍처 컴포넌트는?"
    - "인증 시스템의 전체적인 설계는?"
    - "어떤 주요 디자인 패턴이 사용되고 있나?"
    """

@mcp.tool()
async def local_search(
    query: str,
    context_entities: list[str] | None = None
) -> LocalSearchResult:
    """
    특정 엔티티에 대한 상세 질문에 답변합니다.
    그래프 구조와 엔티티 정보를 결합하여 응답합니다.
    
    Examples:
    - "UserService 클래스의 주요 책임은?"
    - "이 함수는 어떤 입력을 받는가?"
    """
```

#### 3.1.4 편집·관리 도구

```python
@mcp.tool()
async def suggest_refactoring(
    entity_name: str,
    refactoring_type: Literal["extract_method", "rename", "move", "inline"]
) -> RefactoringSuggestion:
    """리팩터링 제안 및 영향 범위 분석"""

@mcp.tool()
async def reindex_repository(
    path: str | None = None,
    incremental: bool = True
) -> IndexingResult:
    """리포지토리를 재인덱싱 (증분 또는 전체)"""

@mcp.tool()
async def execute_shell_command(
    command: str,
    working_directory: str | None = None,
    timeout: int = 30
) -> CommandResult:
    """셸 명령을 실행 (테스트 실행, 빌드 등)"""
```

### 3.2 Resources (4가지 타입)

```python
@mcp.resource("codegraph://entities/{entity_id}")
async def get_entity_resource(entity_id: str) -> Resource:
    """코드 엔티티의 상세 정보"""
    entity = await graph.get_entity(entity_id)
    return Resource(
        uri=f"codegraph://entities/{entity_id}",
        name=entity.qualified_name,
        mimeType="application/json",
        description=entity.docstring or f"{entity.type}: {entity.name}",
        contents=entity.to_json()
    )

@mcp.resource("codegraph://files/{file_path}")
async def get_file_resource(file_path: str) -> Resource:
    """파일 리소스(구조 정보 포함)"""

@mcp.resource("codegraph://communities/{community_id}")
async def get_community_resource(community_id: int) -> Resource:
    """커뮤니티(모듈 클러스터) 요약"""

@mcp.resource("codegraph://stats")
async def get_stats_resource() -> Resource:
    """코드베이스 통계 정보"""
    return Resource(
        uri="codegraph://stats",
        name="Codebase Statistics",
        mimeType="application/json",
        contents={
            "total_files": stats.file_count,
            "total_functions": stats.function_count,
            "total_classes": stats.class_count,
            "languages": stats.language_breakdown,
            "last_indexed": stats.last_indexed.isoformat(),
        }
    )
```

### 3.3 Prompts (6개 프롬프트)

```python
@mcp.prompt()
def code_review_prompt(file_path: str) -> Prompt:
    """코드 리뷰를 수행하기 위한 프롬프트 템플릿"""
    return Prompt(
        name="code_review",
        description="지정 파일의 코드 리뷰를 수행",
        arguments=[
            PromptArgument(name="file_path", description="리뷰 대상 파일", required=True),
            PromptArgument(name="focus_areas", description="중점 영역(security, performance, readability)", required=False),
        ],
        messages=[
            PromptMessage(
                role="user",
                content=f"""
아래 파일에 대해 코드 리뷰를 수행해 주세요.

파일: {{file_path}}
중점 영역: {{focus_areas}}

먼저 get_file_structure 도구로 파일 구조를 확인하고,
다음으로 get_code_snippet 으로 실제 코드를 가져와서 리뷰해 주세요.
의존 관계는 find_dependencies 로 확인할 수 있습니다.
"""
            )
        ]
    )

@mcp.prompt()
def explain_codebase_prompt() -> Prompt:
    """코드베이스 전체 설명을 생성"""
    return Prompt(
        name="explain_codebase",
        description="코드베이스의 전체상을 설명",
        messages=[
            PromptMessage(
                role="user",
                content="""
이 코드베이스의 전체상을 설명해 주세요.

1. 먼저 global_search 도구로 주요 아키텍처를 파악
2. codegraph://stats 리소스로 통계 정보를 확인
3. 주요 모듈과 그 책임을 설명
4. 중요한 설계 패턴을 식별
"""
            )
        ]
    )

@mcp.prompt()
def implement_feature_prompt(feature_description: str) -> Prompt:
    """신규 기능 구현 가이던스"""

@mcp.prompt()
def debug_issue_prompt(error_message: str) -> Prompt:
    """디버깅 지원 프롬프트"""

@mcp.prompt()
def refactor_guidance_prompt(target_entity: str) -> Prompt:
    """리팩터링 가이던스"""

@mcp.prompt()
def test_generation_prompt(function_name: str) -> Prompt:
    """테스트 코드 생성 지원"""
```

---

## 4. 구현 계획

### 4.1 디렉터리 구조

```
codegraph-mcp/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── codegraph_mcp/
│       ├── __init__.py
│       ├── __main__.py           # CLI 엔트리 포인트
│       ├── server.py             # MCP Server 메인
│       ├── config.py             # 설정 관리
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── parser.py         # Tree-sitter AST 파서
│       │   ├── graph.py          # 그래프 엔진
│       │   ├── indexer.py        # 인덱스 관리
│       │   ├── community.py      # 커뮤니티 탐지
│       │   └── semantic.py       # 시맨틱 분석 (LLM)
│       │
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── sqlite.py         # SQLite 스토리지
│       │   ├── cache.py          # 파일 캐시
│       │   └── vectors.py        # 벡터 스토어
│       │
│       ├── mcp/
│       │   ├── __init__.py
│       │   ├── tools.py          # MCP Tools 정의
│       │   ├── resources.py      # MCP Resources 정의
│       │   └── prompts.py        # MCP Prompts 정의
│       │
│       ├── languages/
│       │   ├── __init__.py
│       │   ├── config.py         # 언어 설정
│       │   ├── python.py
│       │   ├── typescript.py
│       │   ├── rust.py
│       │   └── ...
│       │
│       └── utils/
│           ├── __init__.py
│           ├── git.py            # Git 조작
│           └── logging.py
│
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_graph.py
│   ├── test_tools.py
│   └── fixtures/
│
└── examples/
    ├── claude_desktop_config.json
    └── sample_queries.md
```

### 4.2 의존성

```toml
[project]
name = "codegraph-mcp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.0.0",                    # MCP SDK
    "tree-sitter>=0.21.0",           # AST 파싱
    "tree-sitter-python>=0.21.0",
    "tree-sitter-javascript>=0.21.0",
    "tree-sitter-typescript>=0.21.0",
    "tree-sitter-rust>=0.21.0",
    "aiosqlite>=0.19.0",             # 비동기 SQLite
    "pydantic>=2.0.0",               # 데이터 검증
    "networkx>=3.0",                 # 그래프 알고리즘
    "numpy>=1.24.0",                 # 벡터 연산
    "tiktoken>=0.5.0",               # 토큰 계산
    "watchfiles>=0.21.0",            # 파일 감시
    "gitpython>=3.1.0",              # Git 조작
    "rich>=13.0.0",                  # CLI 포맷팅
    "typer>=0.9.0",                  # CLI 프레임워크
]

[project.optional-dependencies]
embeddings = [
    "sentence-transformers>=2.2.0",  # 로컬 임베딩
]
openai = [
    "openai>=1.0.0",                 # OpenAI API
]
```

### 4.3 개발 페이즈

#### Phase 1: Core Foundation (Week 1-2)
- [ ]  프로젝트 구조 세팅
- [ ] Tree-sitter 파서 구현 (Python, TypeScript)
- [ ] SQLite 그래프 스토리지
- [ ] 기본 인덱스 생성

#### Phase 2: MCP Integration (Week 3-4)
- [ ] MCP Server 기반
- [ ] 기본 Tools 구현 (query, get_code, find_dependencies)
- [ ] Resources 구현
- [ ] stdio 트랜스포트

#### Phase 3: GraphRAG Features (Week 5-6)
- [ ] 커뮤니티 탐지 알고리즘
- [ ] LLM 통합 (요약 생성)
- [ ] Global/Local Search 구현
- [ ] Prompts 구현

#### Phase 4: Polish & Extensions (Week 7-8)
- [ ]  증분 인덱스 업데이트
- [ ] 벡터 검색
- [ ] 추가 언어 지원
- [ ] 성능 최적화
- [ ] 문서 정비

---

## 5. 사용 예시

### 5.1 Claude Desktop 설정

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "/path/to/your/project"],
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

### 5.2 사용 시나리오

#### 시나리오 1: 코드베이스 이해
```
User: 이 프로젝트의 주요 컴포넌트를 설명해 줘

Claude: [global_search 도구를 사용]
이 프로젝트는 아래 주요 컴포넌트로 구성되어 있습니다:

1. **인증 모듈** (src/auth/)
   - 사용자 인증과 세션 관리를 담당
   - JWT 토큰 기반 인증을 구현

2. **API 레이어** (src/api/)
   - RESTful API 엔드포인트를 정의
   - 요청 검증 및 응답 포맷팅

3. **데이터 접근 계층** (src/repositories/)
   - 데이터베이스 조작을 추상화
   - Repository 패턴을 채택
...
```

#### 시나리오 2: 영향 범위 분석
```
User: UserService.authenticate 메서드를 변경하면 영향 범위가 어떻게 돼?

Claude: [find_callers 도구를 사용]
UserService.authenticate 를 호출하는 지점을 분석했습니다:

직접 호출처 (5건):
- api/routes/auth.py:login_handler (L45)
- api/routes/auth.py:refresh_token (L78)
- middleware/auth.py:authenticate_request (L23)
- tests/test_auth.py:test_authenticate (L34)
- scripts/admin.py:verify_admin (L56)

간접 영향 (3건):
- api/routes/users.py (authenticate_request middleware 경유)
- api/routes/admin.py (authenticate_request middleware 경유)
...
```

#### 시나리오 3: 기능 구현 지원
```
User: 비밀번호 재설정 기능을 추가하고 싶어

Claude: [query_codebase + analyze_module_structure 를 사용]
기존 인증 시스템을 분석했습니다. 아래 접근을 제안합니다:

1. **신규 파일 생성**: src/auth/password_reset.py
   - 기존 UserService 패턴을 따름
   - EmailService (src/services/email.py) 를 재사용

2. **필요 변경 사항**:
   - src/api/routes/auth.py 에 새 엔드포인트 추가
   - src/models/user.py 에 reset_token 필드 추가
   - src/repositories/user.py 에 find_by_reset_token 메서드 추가

3. **관련 기존 코드**:
   [get_code_snippet: UserService.change_password]
   이 메서드의 패턴을 참고해 구현할 수 있습니다...
```

---

## 6. 성능 목표

| 지표              | 목표값                |
| --------------- | ------------------ |
| 초기 인덱스 (10만 라인) | < 30초              |
| 증분 인덱스          | < 2초               |
| 쿼리 응답           | < 500ms            |
| 메모리 사용량         | < 500MB            |
| 디스크 사용량         | < 10만 라인당 100MB 미만 |
| 기동 시간           | < 2초               |

---

## 7. 향후 확장 계획

1. **VS Code Extension**: 직접 통합
2. **Web UI**: 그래프 시각화 대시보드
3. **멀티 리포지토리**: 모노레포/멀티레포 대응
4. **실시간 업데이트**: LSP 통합
5. **코드 생성**: 템플릿 기반 코드 생성 지원

---

## 8. 참고 자료

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [code-graph-rag](https://github.com/vitali87/code-graph-rag)
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)