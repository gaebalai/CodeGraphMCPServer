# CodeGraph MCP Server コアエンジン詳細設計書

**Project**: CodeGraph MCP Server  
**Version**: 1.0.0  
**Created**: 2025-11-26  
**Status**: Draft  
**Document Type**: C4 Model - Component Diagram (Level 3)

---

## 1. 문서 개요

### 1.1 목적

본 문서는 CodeGraph MCP Server의 **코어 엔진 계층**에 대한 상세 설계를 C4 컴포넌트 다이어그램 관점에서 기술한다.

### 1.2 범위

- AST 파서 설계
- 그래프 엔진 설계
- 시맨틱 분석기 설계
- 인덱서 설계

### 1.3 대상 요구사항

| 요구사항 그룹 | 요구사항 ID | 설명 |
|--------------|------------|------|
| AST 파서 | REQ-AST-001 ~ REQ-AST-005 | AST 분석 기능 |
| 그래프 엔진 | REQ-GRF-001 ~ REQ-GRF-006 | 그래프 관리 기능 |
| 시맨틱 | REQ-SEM-001 ~ REQ-SEM-004 | 의미 분석 기능 |
| 인덱서 | REQ-IDX-001 ~ REQ-IDX-004 | 인덱스 관리 |

---

## 2. 컴포넌트 다이어그램

### 2.1 코어 엔진 전체 구성

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Core Engine Container                               │
│                           src/codegraph_mcp/core/                            │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                              Indexer                                     │ │
│  │                           (indexer.py)                                   │ │
│  │                                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │ │
│  │  │ FileCollector│  │  GitDiffer   │  │ IndexManager │                  │ │
│  │  │              │  │              │  │              │                  │ │
│  │  │ REQ-IDX-001  │  │ REQ-IDX-002  │  │ REQ-IDX-003  │                  │ │
│  │  │ REQ-IDX-004  │  │ REQ-STR-004  │  │              │                  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │ │
│  │         │                 │                 │                           │ │
│  └─────────┼─────────────────┼─────────────────┼───────────────────────────┘ │
│            │                 │                 │                              │
│            ▼                 │                 │                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                            AST Parser                                    │ │
│  │                            (parser.py)                                   │ │
│  │                                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │ │
│  │  │ TreeSitter   │  │ EntityExtrac │  │LanguageConf │                  │ │
│  │  │    Core      │  │    tor       │  │    ig        │                  │ │
│  │  │              │  │              │  │              │                  │ │
│  │  │ REQ-AST-001  │  │ REQ-AST-001  │  │ REQ-AST-004  │                  │ │
│  │  │ REQ-AST-002  │  │ REQ-AST-002  │  │              │                  │ │
│  │  │ REQ-AST-003  │  │ REQ-AST-003  │  │              │                  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────┘                  │ │
│  │         │                 │                                             │ │
│  └─────────┼─────────────────┼─────────────────────────────────────────────┘ │
│            │                 │                                               │
│            ▼                 ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                           Graph Engine                                   │ │
│  │                            (graph.py)                                    │ │
│  │                                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │ │
│  │  │ EntityStore  │  │RelationStore │  │ QueryEngine  │                  │ │
│  │  │              │  │              │  │              │                  │ │
│  │  │ REQ-GRF-001  │  │ REQ-GRF-002  │  │ REQ-GRF-006  │                  │ │
│  │  │ REQ-GRF-003  │  │ REQ-GRF-004  │  │              │                  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │ │
│  │         │                 │                 │                           │ │
│  │         └─────────────────┼─────────────────┘                           │ │
│  │                           │                                             │ │
│  └───────────────────────────┼─────────────────────────────────────────────┘ │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        Semantic Analyzer                                 │ │
│  │                         (semantic.py)                                    │ │
│  │                                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐                                    │ │
│  │  │ Description  │  │ Community    │                                    │ │
│  │  │ Generator    │  │ Detector     │                                    │ │
│  │  │              │  │              │                                    │ │
│  │  │ REQ-SEM-001  │  │ REQ-SEM-003  │                                    │ │
│  │  │ REQ-SEM-002  │  │ REQ-SEM-004  │                                    │ │
│  │  └──────────────┘  └──────────────┘                                    │ │
│  │                                                                          │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. AST 파서 상세 설계

### 3.1 클래스 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                         ASTParser                                │
├─────────────────────────────────────────────────────────────────┤
│ - _parsers: dict[str, Parser]                                   │
│ - _language_configs: dict[str, LanguageConfig]                  │
├─────────────────────────────────────────────────────────────────┤
│ + parse_file(path: str, lang: str) -> ParseResult              │
│ + extract_entities(tree: Tree) -> list[Entity]                 │
│ + extract_relations(tree: Tree, entities: list) -> list[Rel]   │
│ + detect_language(path: str) -> str | None                     │
│ - _get_parser(lang: str) -> Parser                             │
│ - _extract_functions(node: Node) -> list[Entity]               │
│ - _extract_classes(node: Node) -> list[Entity]                 │
│ - _extract_imports(node: Node) -> list[Entity]                 │
│ - _extract_calls(node: Node) -> list[Relation]                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LanguageConfig                              │
├─────────────────────────────────────────────────────────────────┤
│ + name: str                                                      │
│ + extensions: list[str]                                          │
│ + parser_name: str                                               │
│ + node_types: NodeTypeConfig                                     │
├─────────────────────────────────────────────────────────────────┤
│ + get_function_nodes() -> list[str]                             │
│ + get_class_nodes() -> list[str]                                │
│ + get_import_nodes() -> list[str]                               │
│ + get_call_nodes() -> list[str]                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 데이터 모델

```python
# models.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class EntityType(Enum):
    FILE = "file"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    INTERFACE = "interface"
    IMPORT = "import"

class RelationType(Enum):
    CALLS = "calls"
    IMPORTS = "imports"
    INHERITS = "inherits"
    CONTAINS = "contains"
    IMPLEMENTS = "implements"

@dataclass
class Entity:
    """코드 엔티티 (REQ-GRF-001, REQ-GRF-003)"""
    id: str                           # UUID
    type: EntityType                  # 엔티티 타입
    name: str                         # 이름
    qualified_name: str               # 완전 수식명
    file_path: str                    # 파일 경로
    start_line: int                   # 시작 라인
    end_line: int                     # 종료 라인
    signature: Optional[str]          # 시그니처
    docstring: Optional[str]          # 도큐먼트 문자열
    source_code: Optional[str]        # 소스 코드
    embedding: Optional[bytes]        # 벡터 임베딩
    community_id: Optional[int]       # 커뮤니티 ID
    
@dataclass
class Relation:
    """엔티티 간 관계 (REQ-GRF-002, REQ-GRF-004)"""
    id: int                           # 자동 증가 ID
    source_id: str                    # 소스 엔티티 ID
    target_id: str                    # 타깃 엔티티 ID
    type: RelationType                # 관계 타입
    weight: float = 1.0               # 가중치
    metadata: Optional[dict] = None   # 메타데이터

@dataclass
class ParseResult:
    """파싱 결과"""
    file_path: str
    language: str
    entities: list[Entity]
    relations: list[Relation]
    errors: list[str]
    parse_time_ms: float
```

### 3.3 言語設定

```python
# languages/config.py

LANGUAGE_CONFIGS = {
    # Python (REQ-AST-001)
    "python": {
        "extensions": [".py"],
        "parser": "tree-sitter-python",
        "node_types": {
            "function": ["function_definition"],
            "class": ["class_definition"],
            "import": ["import_statement", "import_from_statement"],
            "call": ["call"],
            "decorator": ["decorator"],
        },
        "name_field": "name",
        "body_field": "body",
    },
    
    # TypeScript (REQ-AST-002)
    "typescript": {
        "extensions": [".ts", ".tsx"],
        "parser": "tree-sitter-typescript",
        "node_types": {
            "function": ["function_declaration", "arrow_function", "method_definition"],
            "class": ["class_declaration"],
            "interface": ["interface_declaration"],
            "import": ["import_statement"],
            "call": ["call_expression"],
        },
        "name_field": "name",
        "body_field": "body",
    },
    
    # Rust (REQ-AST-003) - Phase 2
    "rust": {
        "extensions": [".rs"],
        "parser": "tree-sitter-rust",
        "node_types": {
            "function": ["function_item"],
            "struct": ["struct_item"],
            "enum": ["enum_item"],
            "impl": ["impl_item"],
            "use": ["use_declaration"],
            "call": ["call_expression"],
        },
        "name_field": "name",
        "body_field": "body",
    },
}
```

### 3.4 파싱 처리 시퀀스

```
┌────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
│Indexer │     │ASTParser │     │TreeSitter │     │LangConfig│
└───┬────┘     └────┬─────┘     └─────┬─────┘     └────┬─────┘
    │               │                 │                │
    │ parse_file()  │                 │                │
    │──────────────▶│                 │                │
    │               │ detect_language()                │
    │               │─────────────────────────────────▶│
    │               │◀─────────────────────────────────│
    │               │                 │                │
    │               │ get_parser()    │                │
    │               │────────────────▶│                │
    │               │◀────────────────│                │
    │               │                 │                │
    │               │ parse(source)   │                │
    │               │────────────────▶│                │
    │               │◀────────────────│ Tree          │
    │               │                 │                │
    │               │ extract_entities()               │
    │               │──────────────┐  │                │
    │               │◀─────────────┘  │                │
    │               │                 │                │
    │               │ extract_relations()              │
    │               │──────────────┐  │                │
    │               │◀─────────────┘  │                │
    │               │                 │                │
    │◀──────────────│ ParseResult     │                │
    │               │                 │                │
```

### 3.5 에러 핸들링

```python
# parser.py - REQ-AST-005

class ParseError(Exception):
     """파싱 에러"""
    def __init__(self, file_path: str, line: int, message: str):
        self.file_path = file_path
        self.line = line
        self.message = message

class ASTParser:
    def parse_file(self, file_path: str, language: str) -> ParseResult:
        errors = []
        entities = []
        relations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = self._get_parser(language).parse(source.encode())
            
            # 문법 에러가 있어도 분석 가능한 부분은 처리
            if tree.root_node.has_error:
                errors.append(f"Syntax errors detected in {file_path}")
                # 에러 노드 수집
                for node in self._find_error_nodes(tree.root_node):
                    errors.append(f"  Line {node.start_point[0]}: {node.type}")
            
            # 분석 가능한 부분을 처리
            entities = self.extract_entities(tree)
            relations = self.extract_relations(tree, entities)
            
        except Exception as e:
            errors.append(f"Failed to parse {file_path}: {str(e)}")
        
        return ParseResult(
            file_path=file_path,
            language=language,
            entities=entities,
            relations=relations,
            errors=errors,
            parse_time_ms=...
        )
```

---

## 4. 그래프 엔진 상세 설계

### 4.1 클래스 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                        GraphEngine                               │
├─────────────────────────────────────────────────────────────────┤
│ - _db: aiosqlite.Connection                                      │
│ - _entity_store: EntityStore                                     │
│ - _relation_store: RelationStore                                 │
│ - _query_engine: QueryEngine                                     │
├─────────────────────────────────────────────────────────────────┤
│ + async connect(db_path: str) -> None                           │
│ + async close() -> None                                          │
│ + async add_entity(entity: Entity) -> str                       │
│ + async add_relation(relation: Relation) -> int                 │
│ + async get_entity(id: str) -> Entity | None                    │
│ + async query(query: GraphQuery) -> QueryResult                 │
│ + async find_callers(func: str, depth: int) -> list[CallPath]   │
│ + async find_callees(func: str, depth: int) -> list[CallPath]   │
│ + async find_dependencies(name: str, dir: str) -> list[Dep]     │
│ + async get_stats() -> GraphStats                               │
└─────────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   EntityStore   │  │  RelationStore  │  │   QueryEngine   │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ + add()         │  │ + add()         │  │ + execute()     │
│ + get()         │  │ + get()         │  │ + traverse()    │
│ + update()      │  │ + find_by_src() │  │ + search()      │
│ + delete()      │  │ + find_by_tgt() │  │ + aggregate()   │
│ + search()      │  │ + find_by_type()│  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 4.2 SQLite 스키마

```sql
-- storage/schema.sql (REQ-STR-001, REQ-GRF-003~006)

-- 엔티티 테이블
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    qualified_name TEXT,
    file_path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    signature TEXT,
    docstring TEXT,
    source_code TEXT,
    embedding BLOB,
    community_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 관계 테이블
CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    metadata TEXT,  -- JSON형식
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES entities(id) ON DELETE CASCADE
);

-- 커뮤니티 테이블 (REQ-SEM-003)
CREATE TABLE IF NOT EXISTS communities (
    id INTEGER PRIMARY KEY,
    level INTEGER NOT NULL DEFAULT 0,
    name TEXT,
    summary TEXT,
    member_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 정보 테이블
CREATE TABLE IF NOT EXISTS index_info (
    id INTEGER PRIMARY KEY,
    repo_path TEXT NOT NULL,
    last_commit TEXT,
    last_indexed_at TIMESTAMP,
    total_files INTEGER DEFAULT 0,
    total_entities INTEGER DEFAULT 0
);

-- 성능 인덱스 (REQ-GRF-006)
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_file ON entities(file_path);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_entities_qualified ON entities(qualified_name);
CREATE INDEX IF NOT EXISTS idx_entities_community ON entities(community_id);

CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id);
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(type);

-- 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_relations_src_type ON relations(source_id, type);
CREATE INDEX IF NOT EXISTS idx_relations_tgt_type ON relations(target_id, type);
```

### 4.3 그래프 쿼리 API

```python
# graph.py

@dataclass
class GraphQuery:
    """그래프 쿼리 정의"""
    type: str                         # query_type: search, traverse, aggregate
    entity_types: list[str] = None    # 필터 대상 엔티티 타입
    relation_types: list[str] = None  # 필터 대상 관계 타입
    start_entity: str = None          # 시작 엔티티
    direction: str = "both"           # upstream, downstream, both
    max_depth: int = 3                # 최대 깊이
    limit: int = 100                  # 결과 제한 수
    search_text: str = None           # 텍스트 검색
    file_pattern: str = None          # 파일 패턴

@dataclass
class QueryResult:
    """쿼리 결과"""
    entities: list[Entity]
    relations: list[Relation]
    paths: list[list[str]] = None     # 경로 정보 (traverse 시)
    stats: dict = None                # 통계 정보
    query_time_ms: float = 0

class GraphEngine:
    async def query(self, query: GraphQuery) -> QueryResult:
        """범용 그래프 쿼리 실행"""
        if query.type == "search":
            return await self._execute_search(query)
        elif query.type == "traverse":
            return await self._execute_traverse(query)
        elif query.type == "aggregate":
            return await self._execute_aggregate(query)
        else:
            raise ValueError(f"Unknown query type: {query.type}")
    
    async def find_callers(
        self, 
        function_name: str, 
        max_depth: int = 3
    ) -> list[CallPath]:
        """함수의 호출자를 검색 (REQ-TLS-003)"""
        query = GraphQuery(
            type="traverse",
            start_entity=function_name,
            relation_types=["calls"],
            direction="upstream",
            max_depth=max_depth
        )
        result = await self.query(query)
        return self._build_call_paths(result)
    
    async def find_callees(
        self, 
        function_name: str, 
        max_depth: int = 3
    ) -> list[CallPath]:
        """함수의 호출 대상을 검색 (REQ-TLS-004)"""
        query = GraphQuery(
            type="traverse",
            start_entity=function_name,
            relation_types=["calls"],
            direction="downstream",
            max_depth=max_depth
        )
        result = await self.query(query)
        return self._build_call_paths(result)
```

### 4.4 그래프 순회 알고리즘

```python
# graph.py - BFS/DFS순회

class QueryEngine:
    async def traverse_bfs(
        self,
        start_id: str,
        direction: str,
        relation_types: list[str],
        max_depth: int
    ) -> TraverseResult:
        """너비 우선 탐색(BFS)을 통한 그래프 순회"""
        visited = set()
        paths = []
        queue = deque([(start_id, [start_id], 0)])
        
        while queue:
            current_id, path, depth = queue.popleft()
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            if depth > 0:  # 시작 노드가 아닌 경우 경로에 추가
                paths.append(path)
            
            if depth >= max_depth:
                continue
            
            # 인접 노드 조회
            neighbors = await self._get_neighbors(
                current_id, direction, relation_types
            )
            
            for neighbor_id in neighbors:
                if neighbor_id not in visited:
                    queue.append((
                        neighbor_id, 
                        path + [neighbor_id], 
                        depth + 1
                    ))
        
        return TraverseResult(visited=visited, paths=paths)
    
    async def _get_neighbors(
        self,
        entity_id: str,
        direction: str,
        relation_types: list[str]
    ) -> list[str]:
        """인접 노드 조회"""
        if direction == "downstream":
            sql = """
                SELECT target_id FROM relations 
                WHERE source_id = ? AND type IN ({})
            """.format(','.join('?' * len(relation_types)))
            params = [entity_id] + relation_types
        elif direction == "upstream":
            sql = """
                SELECT source_id FROM relations 
                WHERE target_id = ? AND type IN ({})
            """.format(','.join('?' * len(relation_types)))
            params = [entity_id] + relation_types
        else:  # both
            sql = """
                SELECT target_id FROM relations 
                WHERE source_id = ? AND type IN ({})
                UNION
                SELECT source_id FROM relations 
                WHERE target_id = ? AND type IN ({})
            """.format(
                ','.join('?' * len(relation_types)),
                ','.join('?' * len(relation_types))
            )
            params = [entity_id] + relation_types + [entity_id] + relation_types
        
        async with self._db.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
```

---

## 5. 세맨틱 분석기 상세 설계

### 5.1 클래스 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                     SemanticAnalyzer                             │
├─────────────────────────────────────────────────────────────────┤
│ - _llm_client: LLMClient | None                                  │
│ - _community_detector: CommunityDetector                         │
│ - _graph_engine: GraphEngine                                     │
├─────────────────────────────────────────────────────────────────┤
│ + async generate_description(entity: Entity) -> str             │
│ + async generate_community_summary(comm: Community) -> str      │
│ + async detect_communities(level: int) -> list[Community]       │
│ + async assign_communities() -> None                             │
│ + async get_community_hierarchy() -> CommunityHierarchy         │
└─────────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   LLMClient     │  │CommunityDetector│  │DescriptionGen  │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ + generate()    │  │ + detect()      │  │ + generate()    │
│ + embed()       │  │ + hierarchical()│  │ + batch()       │
│                 │  │ + modularity()  │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 5.2 커뮤니티 검출

```python
# semantic.py - REQ-SEM-003, REQ-SEM-004
import networkx as nx
from networkx.algorithms import community as nx_community

class CommunityDetector:
    """커뮤니티 검출기 (Louvain 알고리즘 사용)"""
    
    def __init__(self, graph_engine: GraphEngine):
        self._graph_engine = graph_engine
    
    async def detect_communities(
        self, 
        level: int = 0
    ) -> list[Community]:
        """커뮤니티를 검출"""
        # 그래프를 NetworkX 형식으로 변환
        nx_graph = await self._build_networkx_graph()
        
        # Louvain 알고리즘으로 커뮤니티 검출
        communities = nx_community.louvain_communities(
            nx_graph,
            resolution=1.0 + level * 0.5  # 레벨에 따라 해상도 조정
        )
        
        result = []
        for i, members in enumerate(communities):
            community = Community(
                id=i,
                level=level,
                member_ids=list(members),
                member_count=len(members)
            )
            result.append(community)
        
        return result
    
    async def detect_hierarchical(
        self, 
        max_level: int = 2
    ) -> CommunityHierarchy:
        """계층적 커뮤니티 검출"""
        hierarchy = CommunityHierarchy()
        
        for level in range(max_level + 1):
            communities = await self.detect_communities(level)
            hierarchy.add_level(level, communities)
        
        return hierarchy
    
    async def _build_networkx_graph(self) -> nx.Graph:
        """SQLite에서 NetworkX 그래프를 구성"""
        G = nx.Graph()
        
        # 엔티티를 노드로 추가
        entities = await self._graph_engine.get_all_entities()
        for entity in entities:
            G.add_node(entity.id, **entity.__dict__)
        
        # 관계를 엣지로 추가
        relations = await self._graph_engine.get_all_relations()
        for rel in relations:
            G.add_edge(
                rel.source_id, 
                rel.target_id, 
                type=rel.type,
                weight=rel.weight
            )
        
        return G
```

### 5.3 説明生成

```python
# semantic.py - REQ-SEM-001, REQ-SEM-002

class DescriptionGenerator:
    """LLM을 사용한 설명 생성기"""
    
    ENTITY_PROMPT = """
다음 코드 엔티티에 대해 간결한 설명을 생성해 주세요.

타입: {type}
이름: {name}
시그니처: {signature}
소스 코드:
```
{source_code}
```

説明（1-2文で）:
"""

    COMMUNITY_PROMPT = """
다음 코드 모듈/컴포넌트에 대해 간결한 요약을 생성해 주세요.

구성 함수/클래스:
{members}

관계:
{relations}

이 컴포넌트의 목적과 책임을 한 단락으로 설명해 주세요:
"""

    async def generate_entity_description(
        self, 
        entity: Entity,
        llm_client: LLMClient
    ) -> str:
        """엔티티 설명 생성 (REQ-SEM-001)"""
        prompt = self.ENTITY_PROMPT.format(
            type=entity.type.value,
            name=entity.name,
            signature=entity.signature or "N/A",
            source_code=entity.source_code[:1000] if entity.source_code else "N/A"
        )
        
        return await llm_client.generate(prompt, max_tokens=100)
    
    async def generate_community_summary(
        self, 
        community: Community,
        entities: list[Entity],
        relations: list[Relation],
        llm_client: LLMClient
    ) -> str:
        """커뮤니티 요약 생성 (REQ-SEM-002)"""
        members_text = "\n".join([
            f"- {e.type.value}: {e.name}" for e in entities[:20]
        ])
        relations_text = "\n".join([
            f"- {r.source_id} --{r.type}--> {r.target_id}" 
            for r in relations[:20]
        ])
        
        prompt = self.COMMUNITY_PROMPT.format(
            members=members_text,
            relations=relations_text
        )
        
        return await llm_client.generate(prompt, max_tokens=200)
```

---

## 6. 인덱서 상세 설계

### 6.1 클래스 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                          Indexer                                 │
├─────────────────────────────────────────────────────────────────┤
│ - _parser: ASTParser                                             │
│ - _graph_engine: GraphEngine                                     │
│ - _git_differ: GitDiffer                                         │
│ - _file_collector: FileCollector                                 │
├─────────────────────────────────────────────────────────────────┤
│ + async index_repository(path: str, incr: bool) -> IndexResult  │
│ + async reindex_file(path: str) -> IndexResult                  │
│ + async get_index_status(path: str) -> IndexStatus              │
│ + async clear_index(path: str) -> None                          │
└─────────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  FileCollector  │  │   GitDiffer     │  │  IndexManager   │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ + collect()     │  │ + get_changed() │  │ + save_status() │
│ + filter()      │  │ + get_commit()  │  │ + load_status() │
│ + get_lang()    │  │ + is_git_repo() │  │ + update()      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 6.2 인덱스 처리 플로우

```python
# indexer.py - REQ-IDX-001~004

@dataclass
class IndexResult:
    """インデックス結果"""
    repo_path: str
    total_files: int
    indexed_files: int
    skipped_files: int
    total_entities: int
    total_relations: int
    errors: list[str]
    duration_ms: float
    incremental: bool

class Indexer:
    async def index_repository(
        self, 
        repo_path: str, 
        incremental: bool = True
    ) -> IndexResult:
        """리포지토리를 인덱싱 (REQ-IDX-001)"""
        start_time = time.time()
        errors = []
        
        # 파일 수집
        if incremental and self._git_differ.is_git_repo(repo_path):
            # Git 차이 기반으로 변경 파일 획득 (REQ-IDX-002)
            files = await self._git_differ.get_changed_files(repo_path)
        else:
            # 전체 파일 수집 (REQ-IDX-003)
            files = await self._file_collector.collect(repo_path)
        
        # .gitignore 필터링 (REQ-IDX-004)
        files = await self._file_collector.filter_gitignore(files, repo_path)
        
        indexed_count = 0
        skipped_count = 0
        total_entities = 0
        total_relations = 0
        
        for file_path in files:
            try:
                # 언어 감지
                language = self._parser.detect_language(file_path)
                if language is None:
                    skipped_count += 1
                    continue
                
                # 파싱
                result = await self._parser.parse_file(file_path, language)
                
                if result.errors:
                    errors.extend(result.errors)
                
                # 그래프에 추가
                for entity in result.entities:
                    await self._graph_engine.add_entity(entity)
                    total_entities += 1
                
                for relation in result.relations:
                    await self._graph_engine.add_relation(relation)
                    total_relations += 1
                
                indexed_count += 1
                
            except Exception as e:
                errors.append(f"Error indexing {file_path}: {str(e)}")
                skipped_count += 1
        
        # 인덱스 상태 저장
        await self._save_index_status(repo_path)
        
        duration = (time.time() - start_time) * 1000
        
        return IndexResult(
            repo_path=repo_path,
            total_files=len(files),
            indexed_files=indexed_count,
            skipped_files=skipped_count,
            total_entities=total_entities,
            total_relations=total_relations,
            errors=errors,
            duration_ms=duration,
            incremental=incremental
        )
```

### 6.3 Git 차이 검출

```python
# utils/git.py - REQ-STR-004

import subprocess
from pathlib import Path

class GitDiffer:
    """Git 변경 사항 검출기"""
    
    def is_git_repo(self, path: str) -> bool:
        """Git 리포지토리 여부 판별"""
        git_dir = Path(path) / ".git"
        return git_dir.exists()
    
    async def get_current_commit(self, repo_path: str) -> str:
        """현재 커밋 해시 획득"""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    async def get_changed_files(
        self, 
        repo_path: str,
        since_commit: str = None
    ) -> list[str]:
        """변경된 파일 목록 획득 (REQ-IDX-002)"""
        if since_commit:
            # 특정 커밋 이후 변경 사항
            cmd = ["git", "diff", "--name-only", since_commit, "HEAD"]
        else:
            # 직전 커밋 대비 변경 사항
            cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
        
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        files = result.stdout.strip().split('\n')
        return [
            str(Path(repo_path) / f) 
            for f in files if f
        ]
    
    async def get_staged_files(self, repo_path: str) -> list[str]:
        """스테이징된 파일 목록 획득"""
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        files = result.stdout.strip().split('\n')
        return [
            str(Path(repo_path) / f) 
            for f in files if f
        ]
```

### 6.4 파일 컬렉터

```python
# indexer.py

class FileCollector:
    """파일 수집기"""
    
    SUPPORTED_EXTENSIONS = {
        ".py", ".ts", ".tsx", ".js", ".jsx",  # Phase 1
        ".rs",  # Phase 2
        ".go", ".java", ".cs"  # Phase 3
    }
    
    async def collect(
        self, 
        repo_path: str,
        extensions: set[str] = None
    ) -> list[str]:
        """대상 파일 수집"""
        extensions = extensions or self.SUPPORTED_EXTENSIONS
        files = []
        
        for path in Path(repo_path).rglob("*"):
            if path.is_file() and path.suffix in extensions:
                files.append(str(path))
        
        return files
    
    async def filter_gitignore(
        self, 
        files: list[str],
        repo_path: str
    ) -> list[str]:
        """gitignore 패턴 기반 필터링 (REQ-IDX-004)"""
        gitignore_path = Path(repo_path) / ".gitignore"
        
        if not gitignore_path.exists():
            return files
        
        # gitignore 패턴 로드
        patterns = self._parse_gitignore(gitignore_path)
        
        # 필터링 적용
        return [
            f for f in files 
            if not self._matches_gitignore(f, patterns, repo_path)
        ]
```

---

## 7. 요구사항 트레이서빌리티

### 7.1 컴포넌트 → 요구사항 매핑

| 컴포넌트 | 클래스 | 요구사항 ID | 구현 상태 |
|---------------|--------|--------|---------|
| AST Parser | ASTParser | REQ-AST-001~005 | Phase 1 |
| AST Parser | LanguageConfig | REQ-AST-004 | Phase 1 |
| Graph Engine | GraphEngine | REQ-GRF-001~006 | Phase 1 |
| Graph Engine | EntityStore | REQ-GRF-001, 003 | Phase 1 |
| Graph Engine | RelationStore | REQ-GRF-002, 004 | Phase 1 |
| Graph Engine | QueryEngine | REQ-GRF-006 | Phase 1 |
| Semantic | SemanticAnalyzer | REQ-SEM-001~004 | Phase 2 |
| Semantic | CommunityDetector | REQ-SEM-003, 004 | Phase 2 |
| Semantic | DescriptionGenerator | REQ-SEM-001, 002 | Phase 2 |
| Indexer | Indexer | REQ-IDX-001~004 | Phase 1 |
| Indexer | GitDiffer | REQ-IDX-002, REQ-STR-004 | Phase 1 |
| Indexer | FileCollector | REQ-IDX-004 | Phase 1 |

---

## 8. 성능 설계

### 8.1 성능 목표

| 메트릭 | 목표값 | 측정 방법 | 요구사항 ID |
|-------|--------|-----------|-------------|
| 인덱싱 속도 | 10만 라인 / 30초 | 벤치마크 | REQ-NFR-001 |
| 증분 인덱싱 | 2초 이내 | 벤치마크 | REQ-NFR-002 |
| 쿼리 응답 시간 | 500ms 이내 | 응답 시간 측정 | REQ-NFR-003 |

### 8.2 최적화 전략

| 전략 | 설명 | 대상 |
|-----|------|------|
| 배치 처리 | 엔티티/관계 일괄 삽입 | DB 쓰기 |
| 커넥션 풀 | SQLite 연결 재사용 | DB 연결 |
| 인덱스 | 고속 검색용 인덱스 | 쿼리 |
| 캐시 | 파싱 결과 캐시 | AST 분석 |
| 병렬 처리 | 파일 단위 병렬 파싱 | 인덱싱 |

### 8.3 벤치마크 계획

```python
# tests/benchmarks/test_performance.py

import pytest
import time

@pytest.mark.benchmark
async def test_index_100k_lines(indexer, sample_repo_100k):
    """10만 라인 인덱싱 벤치마크 (REQ-NFR-001)"""
    start = time.time()
    result = await indexer.index_repository(sample_repo_100k)
    duration = time.time() - start
    
    assert duration < 30, f"Indexing took {duration}s, expected < 30s"
    assert result.errors == []

@pytest.mark.benchmark
async def test_incremental_index(indexer, sample_repo):
    """증분 인덱싱 벤치마크 (REQ-NFR-002)"""
    # 최초 인덱싱
    await indexer.index_repository(sample_repo)
    
    # 파일 변경 시뮬레이션
    modify_single_file(sample_repo)
    
    # 증분 인덱싱
    start = time.time()
    result = await indexer.index_repository(sample_repo, incremental=True)
    duration = time.time() - start
    
    assert duration < 2, f"Incremental indexing took {duration}s, expected < 2s"

@pytest.mark.benchmark
async def test_query_response_time(graph_engine, indexed_repo):
    """쿼리 응답 시간 벤치마크 (REQ-NFR-003)"""
    start = time.time()
    result = await graph_engine.find_callers("main", max_depth=3)
    duration = (time.time() - start) * 1000
    
    assert duration < 500, f"Query took {duration}ms, expected < 500ms"
```

---

## 9. 변경 이력

| 버전    | 날짜         | 변경 내용 | 작성자    |
| ----- | ---------- | ----- | ------ |
| 1.0.0 | 2025-11-26 | 초판 작성 | System |

---

**문서 상태**: Draft  
**헌법 준수 여부**: Article I (Library-First), Article III (Test-First) ✓
