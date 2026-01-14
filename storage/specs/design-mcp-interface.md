# CodeGraph MCP Server MCP 인터페이스 설계서

**Project**: CodeGraph MCP Server  
**Version**: 1.0.0  
**Created**: 2025-11-26  
**Status**: Draft  
**Document Type**: C4 Model - Component Diagram (Level 3)

---

## 1. 문서 개요

### 1.1 목적

본 문서는 CodeGraph MCP Server의 MCP 인터페이스 계층에 대한 상세 설계를 기술합니다.

### 1.2 범위

- MCP Server 메인 설계
- Tools 설계 (14개 툴)
- Resources 설계 (4개 타입)
- Prompts 설계 (6개 프롬프트)
- 트랜스포트 설계

### 1.3 대상 요구사항

| 요구사항 그룹 | 요구사항 ID | 설명 |
|--------------|------------|------|
| 트랜스포트 | REQ-TRP-001 ~ REQ-TRP-005 | MCP 통신 |
| 툴 | REQ-TLS-001 ~ REQ-TLS-014 | MCP 툴 |
| 리소스 | REQ-RSC-001 ~ REQ-RSC-004 | MCP 리소스 |
| 프롬프트 | REQ-PRM-001 ~ REQ-PRM-006 | MCP 프롬프트 |

---

## 2. MCP 프로토콜 개요

### 2.1 MCP 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MCP Client                                     │
│                    (GitHub Copilot, Claude, Cursor)                     │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │
                          JSON-RPC 2.0 over Transport
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        CodeGraph MCP Server                              │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                      Transport Layer                               │ │
│  │                                                                    │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │ │
│  │  │   stdio     │  │    SSE      │  │   Streamable HTTP       │   │ │
│  │  │ REQ-TRP-001 │  │ REQ-TRP-002 │  │     REQ-TRP-003         │   │ │
│  │  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘   │ │
│  │         └────────────────┼─────────────────────┘                  │ │
│  │                          │                                        │ │
│  │                          ▼                                        │ │
│  │  ┌────────────────────────────────────────────────────────────┐  │ │
│  │  │              JSON-RPC 2.0 Handler (REQ-TRP-004)            │  │ │
│  │  └────────────────────────────────────────────────────────────┘  │ │
│  │                          │                                        │ │
│  └──────────────────────────┼────────────────────────────────────────┘ │
│                             │                                           │
│  ┌──────────────────────────▼────────────────────────────────────────┐ │
│  │                     MCP Interface Layer                            │ │
│  │                                                                    │ │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐  │ │
│  │  │      Tools       │ │    Resources     │ │     Prompts      │  │ │
│  │  │   (14 tools)     │ │   (4 types)      │ │   (6 prompts)    │  │ │
│  │  │  REQ-TLS-001~014 │ │  REQ-RSC-001~004 │ │  REQ-PRM-001~006 │  │ │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘  │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 MCP Specification 준수

| 기능 | MCP 사양 | 대응 버전 |
|------|---------|---------------|
| Transport | stdio, SSE, HTTP | MCP 1.0 |
| Protocol | JSON-RPC 2.0 | MCP 1.0 |
| Capabilities | tools, resources, prompts | MCP 1.0 |
| Authentication | OAuth 2.1 (optional) | MCP 1.0 |

---

## 3. 서버 메인 설계

### 3.1 서버 클래스 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                     CodeGraphServer                              │
├─────────────────────────────────────────────────────────────────┤
│ - _mcp_server: Server                                            │
│ - _graph_engine: GraphEngine                                     │
│ - _indexer: Indexer                                              │
│ - _semantic: SemanticAnalyzer                                    │
│ - _repo_path: str                                                │
│ - _config: ServerConfig                                          │
├─────────────────────────────────────────────────────────────────┤
│ + async start() -> None                                          │
│ + async stop() -> None                                           │
│ + async initialize(repo_path: str) -> None                      │
│ - _register_tools() -> None                                      │
│ - _register_resources() -> None                                  │
│ - _register_prompts() -> None                                    │
│ - _setup_handlers() -> None                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 서버 초기화 코드

```python
# server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, Prompt

class CodeGraphServer:
    """CodeGraph MCP 서버"""
    
    def __init__(self, config: ServerConfig):
        self._config = config
        self._mcp_server = Server("codegraph-mcp")
        self._graph_engine = None
        self._indexer = None
        self._semantic = None
        self._repo_path = None
    
    async def initialize(self, repo_path: str) -> None:
        """서버 초기화 (REQ-IDX-001)"""
        self._repo_path = repo_path
        
        # 코어 엔진 초기화
        self._graph_engine = GraphEngine()
        await self._graph_engine.connect(
            self._get_db_path(repo_path)
        )
        
        self._indexer = Indexer(
            graph_engine=self._graph_engine
        )
        
        self._semantic = SemanticAnalyzer(
            graph_engine=self._graph_engine
        )
        
        # 인덱스 생성 / 로드
        await self._indexer.index_repository(
            repo_path, 
            incremental=True
        )
        
        # MCP 핸들러 등록
        self._register_tools()
        self._register_resources()
        self._register_prompts()
    
    async def start(self) -> None:
        """서버 시작 (REQ-TRP-001)"""
        async with stdio_server() as (read_stream, write_stream):
            await self._mcp_server.run(
                read_stream,
                write_stream,
                self._mcp_server.create_initialization_options()
            )
    
    async def stop(self) -> None:
        """서버 종료"""
        if self._graph_engine:
            await self._graph_engine.close()
```

### 3.3 CLI 엔트리 포인트

```python
# __main__.py - REQ-CLI-001~004
import click
import asyncio

@click.group()
@click.version_option()
def cli():
    """CodeGraph MCP Server - 소스 코드 그래프 분석 MCP 서버"""
    pass

@cli.command()
@click.option('--repo', '-r', required=True, help='리포지토리 경로')
@click.option('--port', '-p', default=None, type=int, help='SSE 포트 (선택)')
@click.option('--verbose', '-v', is_flag=True, help='상세 로그 출력')
def serve(repo: str, port: int | None, verbose: bool):
    """MCP 서버 시작 (REQ-CLI-001, REQ-CLI-002)"""
    config = ServerConfig(
        repo_path=repo,
        sse_port=port,
        verbose=verbose
    )
    
    server = CodeGraphServer(config)
    
    async def main():
        await server.initialize(repo)
        await server.start()
    
    asyncio.run(main())

@cli.command()
@click.argument('repo_path')
@click.option('--full', is_flag=True, help='전체 재인덱싱')
def index(repo_path: str, full: bool):
    """리포지토리 인덱싱"""
    async def main():
        indexer = Indexer()
        result = await indexer.index_repository(
            repo_path, 
            incremental=not full
        )
        click.echo(f"Indexed {result.indexed_files} files")
        click.echo(f"Entities: {result.total_entities}")
        click.echo(f"Relations: {result.total_relations}")
    
    asyncio.run(main())

@cli.command()
def help():
    """도움말 표시 (REQ-CLI-003)"""
    click.echo(cli.get_help(click.Context(cli)))

if __name__ == "__main__":
    cli()
```

---

## 4. Tools 설계

### 4.1 툴 목록

| 카테고리     | 툴 이름                     | 요구사항 ID     | Phase |
| -------- | ------------------------ | ----------- | ----- |
| 그래프 쿼리   | query_codebase           | REQ-TLS-001 | P0    |
| 그래프 쿼리   | find_dependencies        | REQ-TLS-002 | P0    |
| 그래프 쿼리   | find_callers             | REQ-TLS-003 | P0    |
| 그래프 쿼리   | find_callees             | REQ-TLS-004 | P0    |
| 그래프 쿼리   | find_implementations     | REQ-TLS-005 | P0    |
| 그래프 쿼리   | analyze_module_structure | REQ-TLS-006 | P0    |
| 코드 조회    | get_code_snippet         | REQ-TLS-007 | P0    |
| 코드 조회    | read_file_content        | REQ-TLS-008 | P0    |
| 코드 조회    | get_file_structure       | REQ-TLS-009 | P0    |
| GraphRAG | global_search            | REQ-TLS-010 | P1    |
| GraphRAG | local_search             | REQ-TLS-011 | P1    |
| 편집/관리    | suggest_refactoring      | REQ-TLS-012 | P2    |
| 편집/관리    | reindex_repository       | REQ-TLS-013 | P0    |
| 편집/관리    | execute_shell_command    | REQ-TLS-014 | P1    |

### 4.2 툴 스키마 정의

```python
# mcp/tools.py

from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field
from typing import Literal, Optional

# ====== 입력 스키마 ======

class QueryCodebaseInput(BaseModel):
    """query_codebase 툴 입력 스키마 (REQ-TLS-001)"""
    query: str = Field(..., description="자연어 쿼리")
    scope: Literal["all", "functions", "classes", "files"] = Field(
        default="all", 
        description="검색 범위"
    )
    limit: int = Field(default=20, ge=1, le=100, description="결과 최대 개수")

class FindDependenciesInput(BaseModel):
    """find_dependencies 툴 입력 스키마 (REQ-TLS-002)"""
    entity_name: str = Field(..., description="엔티티 이름")
    direction: Literal["upstream", "downstream", "both"] = Field(
        default="both", 
        description="의존 방향"
    )
    depth: int = Field(default=3, ge=1, le=10, description="탐색 깊이")

class FindCallersInput(BaseModel):
    """find_callers 툴 입력 스키마 (REQ-TLS-003)"""
    function_name: str = Field(..., description="함수 이름")
    max_depth: int = Field(default=3, ge=1, le=10, description="최대 깊이")

class FindCalleesInput(BaseModel):
    """find_callees 툴 입력 스키마 (REQ-TLS-004)"""
    function_name: str = Field(..., description="함수 이름")
    max_depth: int = Field(default=3, ge=1, le=10, description="최대 깊이")

class FindImplementationsInput(BaseModel):
    """find_implementations 툴 입력 스키마 (REQ-TLS-005)"""
    interface_name: str = Field(..., description="인터페이스 / 추상 클래스 이름")

class AnalyzeModuleInput(BaseModel):
    """analyze_module_structure 툴 입력 스키마 (REQ-TLS-006)"""
    module_path: str = Field(..., description="모듈 경로")

class GetCodeSnippetInput(BaseModel):
    """get_code_snippet 툴 입력 스키마 (REQ-TLS-007)"""
    entity_name: str = Field(..., description="엔티티 이름")
    include_context: bool = Field(default=False, description="앞뒤 컨텍스트 포함 여부")
    context_lines: int = Field(default=5, ge=0, le=20, description="컨텍스트 라인 수")

class ReadFileContentInput(BaseModel):
    """read_file_content 툴 입력 스키마 (REQ-TLS-008)"""
    file_path: str = Field(..., description="파일 경로")
    start_line: Optional[int] = Field(None, ge=1, description="시작 라인")
    end_line: Optional[int] = Field(None, ge=1, description="종료 라인")

class GetFileStructureInput(BaseModel):
    """get_file_structure 툴 입력 스키마 (REQ-TLS-009)"""
    file_path: str = Field(..., description="파일 경로")

class GlobalSearchInput(BaseModel):
    """global_search 툴 입력 스키마 (REQ-TLS-010)"""
    query: str = Field(..., description="검색 쿼리")
    community_level: int = Field(default=0, ge=0, le=2, description="커뮤니티 레벨")

class LocalSearchInput(BaseModel):
    """local_search 툴 입력 스키마 (REQ-TLS-011)"""
    query: str = Field(..., description="검색 쿼리")
    context_entities: list[str] = Field(default=[], description="컨텍스트 엔티티")

class SuggestRefactoringInput(BaseModel):
    """suggest_refactoring 툴 입력 스키마 (REQ-TLS-012)"""
    entity_name: str = Field(..., description="대상 엔티티 이름")
    refactoring_type: Literal[
        "extract_method", "rename", "move", "inline", "general"
    ] = Field(default="general", description="리팩터링 타입")

class ReindexRepositoryInput(BaseModel):
    """reindex_repository 툴 입력 스키마 (REQ-TLS-013)"""
    path: Optional[str] = Field(None, description="리포지토리 경로 (생략 시 현재 리포지토리)")
    incremental: bool = Field(default=True, description="증분 인덱싱")

class ExecuteShellCommandInput(BaseModel):
    """execute_shell_command 툴 입력 스키마 (REQ-TLS-014)"""
    command: str = Field(..., description="실행 명령어")
    working_directory: Optional[str] = Field(None, description="작업 디렉터리")
    timeout: int = Field(default=30, ge=1, le=300, description="타임아웃(초)")
```

### 4.3 툴 구현

```python
# mcp/tools.py

class ToolHandlers:
    """MCP 툴 핸들러"""
    
    def __init__(
        self, 
        graph_engine: GraphEngine,
        indexer: Indexer,
        semantic: SemanticAnalyzer,
        repo_path: str
    ):
        self._graph = graph_engine
        self._indexer = indexer
        self._semantic = semantic
        self._repo_path = repo_path
    
    def register(self, server: Server) -> None:
        """툴 등록"""
        
        # ====== 그래프 쿼리 툴 ======
        
        @server.tool()
        async def query_codebase(
            query: str,
            scope: str = "all",
            limit: int = 20
        ) -> list[TextContent]:
            """
            코드베이스를 자연어로 질의 (REQ-TLS-001)
            
            Args:
                query: 검색 쿼리 (예: "인증을 처리하는 함수")
                scope: 검색 범위 (all, functions, classes, files)
                limit: 결과 개수 상한
            
            Returns:
                매칭된 코드 엔티티 목록
            """
            result = await self._graph.query(GraphQuery(
                type="search",
                search_text=query,
                entity_types=[scope] if scope != "all" else None,
                limit=limit
            ))
            
            return [TextContent(
                type="text",
                text=self._format_entities(result.entities)
            )]
        
        @server.tool()
        async def find_dependencies(
            entity_name: str,
            direction: str = "both",
            depth: int = 3
        ) -> list[TextContent]:
            """
            의존 관계 검색 (REQ-TLS-002)
            
            Args:
                entity_name: 엔티티 이름
                direction: 의존 방향 (upstream, downstream, both)
                depth: 탐색 깊이
            
            Returns:
                의존 관계 그래프
            """
            deps = await self._graph.find_dependencies(
                entity_name, direction, depth
            )
            
            return [TextContent(
                type="text",
                text=self._format_dependencies(deps)
            )]
        
        @server.tool()
        async def find_callers(
            function_name: str,
            max_depth: int = 3
        ) -> list[TextContent]:
            """
            함수 호출자 검색 (REQ-TLS-003)
            
            Args:
                function_name: 함수 이름
                max_depth: 최대 탐색 깊이
            
            Returns:
                호출자 함수 목록 및 호출 경로
            """
            callers = await self._graph.find_callers(
                function_name, max_depth
            )
            
            return [TextContent(
                type="text",
                text=self._format_call_paths(callers, "callers")
            )]
        
        @server.tool()
        async def find_callees(
            function_name: str,
            max_depth: int = 3
        ) -> list[TextContent]:
            """
            함수 피호출자 검색 (REQ-TLS-004)
            
            Args:
                function_name: 함수 이름
                max_depth: 최대 탐색 깊이
            
            Returns:
                피호출 함수 목록 및 호출 경로
            """
            callees = await self._graph.find_callees(
                function_name, max_depth
            )
            
            return [TextContent(
                type="text",
                text=self._format_call_paths(callees, "callees")
            )]
        
        @server.tool()
        async def find_implementations(
            interface_name: str
        ) -> list[TextContent]:
            """
            인터페이스 구현 검색 (REQ-TLS-005)
            
            Args:
                interface_name: 인터페이스 / 추상 클래스 이름
            
            Returns:
                구현 클래스 목록
            """
            impls = await self._graph.find_implementations(interface_name)
            
            return [TextContent(
                type="text",
                text=self._format_implementations(impls)
            )]
        
        @server.tool()
        async def analyze_module_structure(
            module_path: str
        ) -> list[TextContent]:
            """
            모듈 구조 분석 (REQ-TLS-006)
            
            Args:
                module_path: 모듈 경로
            
            Returns:
                모듈 구조 분석 결과
            """
            analysis = await self._graph.analyze_module(module_path)
            
            return [TextContent(
                type="text",
                text=self._format_module_analysis(analysis)
            )]
        
        # ====== 코드 조회 툴 ======
        
        @server.tool()
        async def get_code_snippet(
            entity_name: str,
            include_context: bool = False,
            context_lines: int = 5
        ) -> list[TextContent]:
            """
            코드 스니펫 조회 (REQ-TLS-007)
            
            Args:
                entity_name: 엔티티 이름
                include_context: 앞뒤 컨텍스트 포함 여부
                context_lines: 컨텍스트 라인 수
            
            Returns:
                소스 코드
            """
            entity = await self._graph.get_entity_by_name(entity_name)
            if not entity:
                return [TextContent(
                    type="text",
                    text=f"Entity not found: {entity_name}"
                )]
            
            code = entity.source_code
            if include_context:
                code = await self._get_code_with_context(
                    entity, context_lines
                )
            
            return [TextContent(
                type="text",
                text=f"```{self._detect_lang(entity.file_path)}\n{code}\n```"
            )]
        
        @server.tool()
        async def read_file_content(
            file_path: str,
            start_line: int | None = None,
            end_line: int | None = None
        ) -> list[TextContent]:
            """
            파일 내용 읽기 (REQ-TLS-008)
            
            Args:
                file_path: 파일 경로
                start_line: 시작 라인 (선택)
                end_line: 종료 라인 (선택)
            
            Returns:
                파일 내용
            """
            # 보안 체크 (REQ-NFR-013)
            if not self._is_allowed_path(file_path):
                return [TextContent(
                    type="text",
                    text=f"Access denied: {file_path}"
                )]
            
            content = await self._read_file(
                file_path, start_line, end_line
            )
            
            return [TextContent(
                type="text",
                text=content
            )]
        
        @server.tool()
        async def get_file_structure(
            file_path: str
        ) -> list[TextContent]:
            """
            파일 구조 조회 (REQ-TLS-009)
            
            Args:
                file_path: 파일 경로
            
            Returns:
                파일 내 클래스/함수 구조 정보
            """
            entities = await self._graph.get_entities_by_file(file_path)
            
            return [TextContent(
                type="text",
                text=self._format_file_structure(entities)
            )]
        
        # ====== GraphRAG 툴 (Phase 2) ======
        
        @server.tool()
        async def global_search(
            query: str,
            community_level: int = 0
        ) -> list[TextContent]:
            """
            글로벌 검색 (커뮤니티 요약 사용) (REQ-TLS-010)
            
            Args:
                query: 검색 쿼리
                community_level: 커뮤니티 레벨 (0=세밀, 1=거친)
            
            Returns:
                코드베이스 전체에 대한 매크로 수준 응답
            """
            result = await self._semantic.global_search(
                query, community_level
            )
            
            return [TextContent(
                type="text",
                text=result
            )]
        
        @server.tool()
        async def local_search(
            query: str,
            context_entities: list[str] = []
        ) -> list[TextContent]:
            """
            로컬 검색 (그래프 구조 사용) (REQ-TLS-011)
            
            Args:
                query: 검색 쿼리
                context_entities: 컨텍스트 엔티티 이름 목록
            
            Returns:
                상세 응답
            """
            result = await self._semantic.local_search(
                query, context_entities
            )
            
            return [TextContent(
                type="text",
                text=result
            )]
        
        # ====== 편집 / 관리 툴 ======
        
        @server.tool()
        async def suggest_refactoring(
            entity_name: str,
            refactoring_type: str = "general"
        ) -> list[TextContent]:
            """
            리팩터링 제안 (REQ-TLS-012)
            
            Args:
                entity_name: 대상 엔티티 이름
                refactoring_type: 리팩터링 유형
            
            Returns:
                리팩터링 제안 및 영향 범위 분석
            """
            suggestion = await self._semantic.suggest_refactoring(
                entity_name, refactoring_type
            )
            
            return [TextContent(
                type="text",
                text=suggestion
            )]
        
        @server.tool()
        async def reindex_repository(
            path: str | None = None,
            incremental: bool = True
        ) -> list[TextContent]:
            """
            리포지토리 재인덱싱 (REQ-TLS-013)
            
            Args:
                path: 리포지토리 경로 (생략 시 현재 리포지토리)
                incremental: 증분 인덱싱
            
            Returns:
                인덱싱 결과
            """
            repo_path = path or self._repo_path
            result = await self._indexer.index_repository(
                repo_path, incremental
            )
            
            return [TextContent(
                type="text",
                text=self._format_index_result(result)
            )]
        
        @server.tool()
        async def execute_shell_command(
            command: str,
            working_directory: str | None = None,
            timeout: int = 30
        ) -> list[TextContent]:
            """
            셸 명령 실행 (REQ-TLS-014)
            
            Args:
                command: 실행 명령
                working_directory: 작업 디렉터리
                timeout: 타임아웃(초)
            
            Returns:
                명령 실행 결과
            """
            # 보안 체크 (REQ-NFR-012)
            cwd = working_directory or self._repo_path
            if not self._is_allowed_path(cwd):
                return [TextContent(
                    type="text",
                    text=f"Access denied: {cwd}"
                )]
            
            try:
                result = await asyncio.wait_for(
                    self._execute_command(command, cwd),
                    timeout=timeout
                )
                return [TextContent(type="text", text=result)]
            except asyncio.TimeoutError:
                return [TextContent(
                    type="text",
                    text=f"Command timed out after {timeout}s"
                )]
```

---

## 5. Resources 설계

### 5.1 리소스 목록

| URI 패턴 | 요구사항 ID | 설명 | Phase |
|---------|-------------|------|-------|
| `codegraph://entities/{entity_id}` | REQ-RSC-001 | 엔티티 상세 정보 | P0 |
| `codegraph://files/{file_path}` | REQ-RSC-002 | 파일 정보 | P0 |
| `codegraph://communities/{community_id}` | REQ-RSC-003 | 커뮤니티 정보 | P1 |
| `codegraph://stats` | REQ-RSC-004 | 통계 정보 | P0 |

### 5.2 리소스 스키마

```python
# mcp/resources.py

from mcp.types import Resource, TextResourceContents
from typing import Optional

# ====== Response Schemas ======

class EntityResource(BaseModel):
    """엔티티 리소스 (REQ-RSC-001)"""
    id: str
    type: str
    name: str
    qualified_name: str
    file_path: str
    start_line: int
    end_line: int
    signature: Optional[str]
    docstring: Optional[str]
    source_code: Optional[str]
    community_id: Optional[int]
    relations: list[dict]  # {type, target_id, target_name}

class FileResource(BaseModel):
    """파일 리소스 (REQ-RSC-002)"""
    path: str
    language: str
    size_bytes: int
    line_count: int
    entities: list[dict]  # {type, name, start_line, end_line}
    imports: list[str]

class CommunityResource(BaseModel):
    """커뮤니티 리소스 (REQ-RSC-003)"""
    id: int
    level: int
    name: Optional[str]
    summary: Optional[str]
    member_count: int
    members: list[dict]  # {id, type, name}
    top_entities: list[dict]

class StatsResource(BaseModel):
    """통계 리소스 (REQ-RSC-004)"""
    total_files: int
    total_entities: int
    total_relations: int
    entity_breakdown: dict[str, int]  # {type: count}
    language_breakdown: dict[str, int]  # {lang: count}
    last_indexed_at: str
    index_duration_ms: float
```

### 5.3 리소스 구현

```python
# mcp/resources.py

class ResourceHandlers:
    """MCP 리소스 핸들러"""
    
    def __init__(
        self,
        graph_engine: GraphEngine,
        repo_path: str
    ):
        self._graph = graph_engine
        self._repo_path = repo_path
    
    def register(self, server: Server) -> None:
        """리소스 등록"""
        
        @server.list_resources()
        async def list_resources() -> list[Resource]:
            """사용 가능한 리소스 목록 반환"""
            return [
                Resource(
                    uri="codegraph://stats",
                    name="Codebase Statistics",
                    mimeType="application/json",
                    description="코드베이스 통계 정보"
                ),
                # 동적 리소스는 템플릿 형태로 제공
                Resource(
                    uri="codegraph://entities/{entity_id}",
                    name="Entity Details",
                    mimeType="application/json",
                    description="엔티티 상세 정보"
                ),
                Resource(
                    uri="codegraph://files/{file_path}",
                    name="File Information",
                    mimeType="application/json",
                    description="파일 구조 정보"
                ),
                Resource(
                    uri="codegraph://communities/{community_id}",
                    name="Community Summary",
                    mimeType="application/json",
                    description="커뮤니티 요약 정보"
                ),
            ]
        
        @server.read_resource()
        async def read_resource(uri: str) -> TextResourceContents:
            """리소스 읽기"""
            
            # codegraph://stats (REQ-RSC-004)
            if uri == "codegraph://stats":
                stats = await self._graph.get_stats()
                return TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=stats.model_dump_json(indent=2)
                )
            
            # codegraph://entities/{entity_id} (REQ-RSC-001)
            if uri.startswith("codegraph://entities/"):
                entity_id = uri.split("/")[-1]
                entity = await self._graph.get_entity(entity_id)
                if not entity:
                    raise ValueError(f"Entity not found: {entity_id}")
                
                relations = await self._graph.get_entity_relations(entity_id)
                resource = EntityResource(
                    **entity.__dict__,
                    relations=[r.__dict__ for r in relations]
                )
                return TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=resource.model_dump_json(indent=2)
                )
            
            # codegraph://files/{file_path} (REQ-RSC-002)
            if uri.startswith("codegraph://files/"):
                file_path = uri.replace("codegraph://files/", "")
                entities = await self._graph.get_entities_by_file(file_path)
                
                resource = FileResource(
                    path=file_path,
                    language=self._detect_language(file_path),
                    size_bytes=os.path.getsize(file_path),
                    line_count=self._count_lines(file_path),
                    entities=[{
                        "type": e.type.value,
                        "name": e.name,
                        "start_line": e.start_line,
                        "end_line": e.end_line
                    } for e in entities],
                    imports=self._extract_imports(entities)
                )
                return TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=resource.model_dump_json(indent=2)
                )
            
            # codegraph://communities/{community_id} (REQ-RSC-003)
            if uri.startswith("codegraph://communities/"):
                community_id = int(uri.split("/")[-1])
                community = await self._graph.get_community(community_id)
                if not community:
                    raise ValueError(f"Community not found: {community_id}")
                
                members = await self._graph.get_community_members(community_id)
                resource = CommunityResource(
                    **community.__dict__,
                    members=[{
                        "id": m.id,
                        "type": m.type.value,
                        "name": m.name
                    } for m in members],
                    top_entities=members[:10]
                )
                return TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=resource.model_dump_json(indent=2)
                )
            
            raise ValueError(f"Unknown resource: {uri}")
```

---

## 6. Prompts 설계

### 6.1 프롬프트 목록

| 프롬프트명 | 요구사항 ID | 설명 | Phase |
|-----------|------------|------|-------|
| `code_review` | REQ-PRM-001 | 코드 리뷰 지원 | P1 |
| `explain_codebase` | REQ-PRM-002 | 코드베이스 설명 | P1 |
| `implement_feature` | REQ-PRM-003 | 기능 구현 가이던스 | P1 |
| `debug_issue` | REQ-PRM-004 | 디버깅 지원 | P1 |
| `refactor_guidance` | REQ-PRM-005 | 리팩터링 가이던스 | P2 |
| `test_generation` | REQ-PRM-006 | 테스트 생성 지원 | P1 |

### 6.2 프롬프트 구현

```python
# mcp/prompts.py

from mcp.types import Prompt, PromptMessage, PromptArgument
from mcp.types import TextContent

class PromptHandlers:
    """MCP 프롬프트 핸들러"""
    
    def __init__(
        self,
        graph_engine: GraphEngine,
        repo_path: str
    ):
        self._graph = graph_engine
        self._repo_path = repo_path
    
    def register(self, server: Server) -> None:
        """프롬프트 등록"""
        
        @server.list_prompts()
        async def list_prompts() -> list[Prompt]:
            """사용 가능한 프롬프트 목록 반환"""
            return [
                Prompt(
                    name="code_review",
                    description="지정 파일에 대한 코드 리뷰 수행",
                    arguments=[
                        PromptArgument(
                            name="file_path",
                            description="리뷰 대상 파일 경로",
                            required=True
                        ),
                        PromptArgument(
                            name="focus_areas",
                            description="중점 영역 (security, performance, readability)",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="explain_codebase",
                    description="코드베이스 전체 설명 생성",
                    arguments=[]
                ),
                Prompt(
                    name="implement_feature",
                    description="신규 기능 구현 가이던스 제공",
                    arguments=[
                        PromptArgument(
                            name="feature_description",
                            description="구현하고 싶은 기능 설명",
                            required=True
                        )
                    ]
                ),
                Prompt(
                    name="debug_issue",
                    description="디버깅 지원 프롬프트",
                    arguments=[
                        PromptArgument(
                            name="error_message",
                            description="에러 메시지",
                            required=True
                        ),
                        PromptArgument(
                            name="context",
                            description="추가 컨텍스트",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="refactor_guidance",
                    description="리팩터링 가이던스",
                    arguments=[
                        PromptArgument(
                            name="target_entity",
                            description="리팩터링 대상",
                            required=True
                        )
                    ]
                ),
                Prompt(
                    name="test_generation",
                    description="테스트 코드 생성 지원",
                    arguments=[
                        PromptArgument(
                            name="function_name",
                            description="테스트 대상 함수명",
                            required=True
                        )
                    ]
                ),
            ]
        
        @server.get_prompt()
        async def get_prompt(
            name: str, 
            arguments: dict[str, str] | None = None
        ) -> list[PromptMessage]:
            """프롬프트 가져오기"""
            arguments = arguments or {}
            
            # code_review (REQ-PRM-001)
            if name == "code_review":
                return await self._get_code_review_prompt(
                    arguments.get("file_path", ""),
                    arguments.get("focus_areas", "")
                )
            
            # explain_codebase (REQ-PRM-002)
            elif name == "explain_codebase":
                return await self._get_explain_codebase_prompt()
            
            # implement_feature (REQ-PRM-003)
            elif name == "implement_feature":
                return await self._get_implement_feature_prompt(
                    arguments.get("feature_description", "")
                )
            
            # debug_issue (REQ-PRM-004)
            elif name == "debug_issue":
                return await self._get_debug_issue_prompt(
                    arguments.get("error_message", ""),
                    arguments.get("context", "")
                )
            
            # refactor_guidance (REQ-PRM-005)
            elif name == "refactor_guidance":
                return await self._get_refactor_guidance_prompt(
                    arguments.get("target_entity", "")
                )
            
            # test_generation (REQ-PRM-006)
            elif name == "test_generation":
                return await self._get_test_generation_prompt(
                    arguments.get("function_name", "")
                )
            
            else:
                raise ValueError(f"Unknown prompt: {name}")
    
    # ====== 프롬프트 템플릿 ======
    
    async def _get_code_review_prompt(
        self, 
        file_path: str,
        focus_areas: str
    ) -> list[PromptMessage]:
        """코드 리뷰 프롬프트 (REQ-PRM-001)"""
        # 파일 정보 가져오기
        entities = await self._graph.get_entities_by_file(file_path)
        file_content = self._read_file(file_path)
        
        structure_info = "\n".join([
            f"- {e.type.value}: {e.name} (lines {e.start_line}-{e.end_line})"
            for e in entities
        ])
        
        focus = focus_areas or "general quality, bugs, and improvements"
        
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""아래 파일에 대한 코드 리뷰를 수행해 주세요.

## 대상 파일
**경로**: {file_path}

## 파일 구조
{structure_info}

## 리뷰 중점 영역
{focus}

## 소스 코드
```
{file_content}
```

## 리뷰 관점
1. 버그 및 잠재적 문제
2. 코드 품질(가독성, 유지보수성)
3. 성능
4. 보안
5. 베스트 프랙티스

상세한 리뷰 코멘트를 제공해 주세요. 각 지적 사항에는 라인 번호와 개선 제안을 포함해 주세요.
"""
                )
            )
        ]
    
    async def _get_explain_codebase_prompt(self) -> list[PromptMessage]:
        """코드베이스 설명 프롬프트 (REQ-PRM-002)"""
        stats = await self._graph.get_stats()
        
        # 주요 컴포넌트 가져오기
        top_modules = await self._graph.get_top_modules(limit=10)
        module_info = "\n".join([
            f"- {m.name}: {m.description or 'No description'}"
            for m in top_modules
        ])
        
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""이 코드베이스에 대해 설명해 주세요.

## 통계 정보
- 총 파일 수: {stats.total_files}
- 총 엔티티 수: {stats.total_entities}
- 언어 구성: {stats.language_breakdown}

## 주요 모듈
{module_info}

## 설명해 줬으면 하는 내용
1. 이 프로젝트의 목적과 주요 기능
2. 아키텍처 개요
3. 주요 컴포넌트와 역할
4. 데이터 흐름 개요
5. 중요한 의존 관계

처음 보는 개발자도 이해할 수 있도록, 구조화된 설명을 제공해 주세요.
"""
                )
            )
        ]
    
    async def _get_implement_feature_prompt(
        self, 
        feature_description: str
    ) -> list[PromptMessage]:
        """기능 구현 가이던스 프롬프트 (REQ-PRM-003)"""
        # 관련 가능성이 있는 엔티티 검색
        related = await self._graph.query(GraphQuery(
            type="search",
            search_text=feature_description,
            limit=10
        ))
        
        related_info = "\n".join([
            f"- {e.type.value}: {e.qualified_name} ({e.file_path})"
            for e in related.entities
        ])
        
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""아래 기능을 구현하기 위한 가이던스를 제공해 주세요.

## 기능 설명
{feature_description}

## 관련된 기존 코드
{related_info}

## 제공해 줬으면 하는 정보
1. 구현 접근 방식 제안
2. 변경이 필요한 파일
3. 새로 만들어야 하는 파일
4. 영향을 받는 기존 기능
5. 테스트 전략
6. 구현 우선순위와 절차

코드베이스의 아키텍처에 맞는 구현 방법을 제안해 주세요.
"""
                )
            )
        ]
    
    async def _get_debug_issue_prompt(
        self, 
        error_message: str,
        context: str
    ) -> list[PromptMessage]:
        """디버깅 지원 프롬프트 (REQ-PRM-004)"""
        # 에러 메시지에서 관련 파일/함수 추출
        related = await self._extract_error_context(error_message)
        
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""아래 에러의 디버깅을 지원해 주세요.

## 에러 메시지
{error_message}

python
코드 복사

## 추가 컨텍스트
{context or "없음"}

## 관련 코드
{related}

## 지원해 줬으면 하는 내용
1. 에러 원인 분석
2. 조사해야 할 파일/함수
3. 디버깅 절차 제안
4. 수정안
5. 재발 방지책

스텝 바이 스텝으로 디버깅을 진행할 수 있도록 지원해 주세요.
"""
                )
            )
        ]
    
    async def _get_test_generation_prompt(
        self, 
        function_name: str
    ) -> list[PromptMessage]:
        """테스트 생성 지원 프롬프트 (REQ-PRM-006)"""
        # 함수 정보 가져오기
        entity = await self._graph.get_entity_by_name(function_name)
        if not entity:
            return [PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"Function not found: {function_name}"
                )
            )]
        
        # 의존 관계 가져오기
        deps = await self._graph.find_callees(function_name, max_depth=1)
        
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""아래 함수에 대한 테스트 코드를 생성해 주세요.

## 대상 함수
**이름**: {entity.name}
**파일**: {entity.file_path}
**시그니처**: {entity.signature or "N/A"}

## 소스 코드
```
{entity.source_code}
```

## 의존 관계(호출하고 있는 함수)
{self._format_deps(deps)}

## 생성해 줬으면 하는 테스트
1. 정상 케이스 테스트
2. 비정상 케이스 테스트(경계값, 에러 처리)
3. 목(mock)이 필요하다면 목 설정
4. 테스트 케이스 설명 주석

pytest 형식으로 테스트 코드를 생성해 주세요.
"""
                )
            )
        ]
```

---

## 7. 트랜스포트 설계

### 7.1 트랜스포트 구성

```python
# transports.py

class TransportConfig(BaseModel):
    """트랜스포트 설정"""
    type: Literal["stdio", "sse", "http"] = "stdio"
    host: str = "localhost"
    port: int = 8080
    ssl: bool = False

class TransportFactory:
    """트랜스포트 팩토리"""
    
    @staticmethod
    async def create(
        config: TransportConfig,
        server: Server
    ) -> AsyncContextManager:
        """트랜스포트 생성"""
        
        if config.type == "stdio":
            # stdio 트랜스포트 (REQ-TRP-001)
            return stdio_server()
        
        elif config.type == "sse":
            # SSE 트랜스포트 (REQ-TRP-002)
            return sse_server(
                host=config.host,
                port=config.port
            )
        
        elif config.type == "http":
            # Streamable HTTP 트랜스포트 (REQ-TRP-003)
            return http_server(
                host=config.host,
                port=config.port,
                ssl=config.ssl
            )
        
        else:
            raise ValueError(f"Unknown transport type: {config.type}")
```

### 7.2 JSON-RPC 2.0 처리

```python
# server.py - REQ-TRP-004

class JsonRpcHandler:
    """JSON-RPC 2.0 메시지 핸들러"""
    
    async def handle_message(
        self, 
        message: dict
    ) -> dict:
        """메시지 처리"""
        
        # 유효성 검증
        if "jsonrpc" not in message or message["jsonrpc"] != "2.0":
            return self._error_response(
                None, -32600, "Invalid Request"
            )
        
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        try:
            # 메서드 실행
            result = await self._dispatch(method, params)
            
            if msg_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": result
                }
            return None  # Notification
            
        except Exception as e:
            return self._error_response(
                msg_id, -32603, str(e)
            )
    
    def _error_response(
        self, 
        msg_id: int | None,
        code: int,
        message: str
    ) -> dict:
        """에러 응답 생성"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": code,
                "message": message
            }
        }
```

---

## 8. 에러 핸들링

### 8.1 에러 코드 정의

```python
# errors.py

from enum import IntEnum

class ErrorCode(IntEnum):
    """MCP 에러 코드"""
    # JSON-RPC 표준 에러
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # 커스텀 에러
    ENTITY_NOT_FOUND = -32001
    FILE_NOT_FOUND = -32002
    ACCESS_DENIED = -32003
    TIMEOUT = -32004
    INDEX_ERROR = -32005

class CodeGraphError(Exception):
    """CodeGraph 에러 기본 클래스"""
    def __init__(self, code: ErrorCode, message: str, data: dict = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

class EntityNotFoundError(CodeGraphError):
    def __init__(self, entity_name: str):
        super().__init__(
            ErrorCode.ENTITY_NOT_FOUND,
            f"Entity not found: {entity_name}",
            {"entity_name": entity_name}
        )

class AccessDeniedError(CodeGraphError):
    def __init__(self, path: str):
        super().__init__(
            ErrorCode.ACCESS_DENIED,
            f"Access denied: {path}",
            {"path": path}
        )
```

---

## 9. 요구사항 트레이서빌리티

### 9.1 컴포넌트 → 요구사항 매핑

| 컴포넌트 | 파일 | 요구사항 ID | Phase |
|---------|------|------------|-------|
| Server Main | server.py | REQ-TRP-001~005, REQ-CLI-001~004 | P0 |
| Tools: Graph Query | mcp/tools.py | REQ-TLS-001~006 | P0 |
| Tools: Code Fetch | mcp/tools.py | REQ-TLS-007~009 | P0 |
| Tools: GraphRAG | mcp/tools.py | REQ-TLS-010~011 | P1 |
| Tools: Management | mcp/tools.py | REQ-TLS-012~014 | P1 / P2 |
| Resources | mcp/resources.py | REQ-RSC-001~004 | P0 / P1 |
| Prompts | mcp/prompts.py | REQ-PRM-001~006 | P1 / P2 |

---

## 10. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0.0 | 2025-11-26 | 초판 작성 | System |

---

**문서 상태**: Draft  
**헌법 준수 여부**: Article II (CLI Interface), Article VIII (No Abstraction) ✓
