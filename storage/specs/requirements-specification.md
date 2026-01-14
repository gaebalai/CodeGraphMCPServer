```markdown
# CodeGraph MCP Server 要件定義書

**Project**: CodeGraph MCP Server
**Version**: 1.0.0
**Created**: 2025-11-26
**Status**: Draft
**Based On**: References/system-design.md

---

## 1. 문서 개요

### 1.1 목적

본 문서는 CodeGraph MCP Server의 기능 요구사항 및 비기능 요구사항을 EARS(Easy Approach to Requirements Syntax) 형식으로 정의한다.

### 1.2 범위

- 소스코드 분석에 최적화된 MCP 서버 개발
- GitHub Copilot, Claude Code, Cursor 등 MCP 지원 AI 도구와의 통합
- GraphRAG 기능을 통한 코드베이스의 구조적 이해 구현

### 1.3 대상 독자

- 시스템 아키텍트
- 소프트웨어 개발자
- QA 엔지니어
- 프로덕트 오너

---

## 2. 제품 비전

### 2.1 비전 스테이트먼트

Microsoft GraphRAG의 컨셉과 code-graph-rag 구현을 참고하여, 제로 설정으로 기동 가능한 경량·고속 소스코드 분석 MCP 서버를 제공하고, AI 지원 개발의 생산성을 비약적으로 향상시킨다.

### 2.2 주요 차별화 요소

| 요소 | CodeGraph MCP Server |
|------|---------------------|
| 아키텍처 | MCP Native Server |
| 그래프 DB | SQLite + 내장 그래프 엔진 |
| 배포 | 단일 바이너리 / pip install |
| 기동 시간 | 경량(초 단위) |
| 스코프 | 멀티 리포지토리 지원 |
| 인덱스 업데이트 | Git diff 기반 증분 업데이트 |
| GraphRAG 기능 | 커뮤니티 요약 · 글로벌 쿼리 |

---

## 3. 기능 요구사항

### 3.1 코어 엔진 요구사항

#### 3.1.1 AST 파서 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-AST-001 | **WHEN** 사용자가 Python 파일을 인덱스 대상으로 지정한 경우, **THE SYSTEM SHALL** Tree-sitter를 사용해 AST 분석을 수행하고 함수 정의, 클래스 정의, import 문, 함수 호출을 추출한다 | Event-driven | P0 |
| REQ-AST-002 | **WHEN** 사용자가 TypeScript 파일을 인덱스 대상으로 지정한 경우, **THE SYSTEM SHALL** 함수 선언, 화살표 함수, 메서드 정의, 클래스 선언, 인터페이스 선언, import 문, 호출식을 추출한다 | Event-driven | P0 |
| REQ-AST-003 | **WHEN** 사용자가 Rust 파일을 인덱스 대상으로 지정한 경우, **THE SYSTEM SHALL** 함수 아이템, 구조체, 열거형, impl, use 선언, 호출식을 추출한다 | Event-driven | P1 |
| REQ-AST-004 | **THE SYSTEM SHALL** 지원 언어의 확장자를 자동 인식하고 적절한 파서를 선택한다 | Ubiquitous | P0 |
| REQ-AST-005 | **IF** 분석 대상 파일에서 구문 오류가 감지된 경우, **THEN THE SYSTEM SHALL** 오류를 로그에 기록하고 분석 가능한 부분만 처리한다 | Unwanted behavior | P1 |

#### 3.1.2 그래프 엔진 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-GRF-001 | **THE SYSTEM SHALL** 코드 엔티티(File, Module, Class, Function, Method)를 노드로 그래프에 저장한다 | Ubiquitous | P0 |
| REQ-GRF-002 | **THE SYSTEM SHALL** 엔티티 간 관계(CALLS, IMPORTS, INHERITS, CONTAINS, IMPLEMENTS)를 엣지로 그래프에 저장한다 | Ubiquitous | P0 |
| REQ-GRF-003 | **WHEN** 엔티티가 생성된 경우, **THE SYSTEM SHALL** ID, 타입, 이름, 정규화 이름(qualified name), 파일 경로, 시작 라인, 종료 라인, 시그니처, docstring, 소스코드, 임베딩 벡터, 커뮤니티 ID, 생성일시, 수정일시를 저장한다 | Event-driven | P0 |
| REQ-GRF-004 | **WHEN** 관계가 생성된 경우, **THE SYSTEM SHALL** 소스 ID, 타겟 ID, 관계 타입, 가중치, 메타데이터를 저장한다 | Event-driven | P0 |
| REQ-GRF-005 | **THE SYSTEM SHALL** SQLite를 사용해 그래프 데이터를 영속화한다 | Ubiquitous | P0 |
| REQ-GRF-006 | **THE SYSTEM SHALL** 엔티티 타입, 파일 경로, 커뮤니티 ID, 관계 소스, 관계 타겟, 관계 타입에 인덱스를 생성하여 고속 쿼리를 구현한다 | Ubiquitous | P0 |

#### 3.1.3 시맨틱 분석 요구사항(GraphRAG 기능)

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-SEM-001 | **WHEN** 엔티티가 신규 생성된 경우, **THE SYSTEM SHALL** LLM을 사용해 엔티티의 자연어 설명을 생성한다 | Event-driven | P1 |
| REQ-SEM-002 | **WHEN** 커뮤니티가 탐지된 경우, **THE SYSTEM SHALL** LLM을 사용해 모듈 커뮤니티 요약을 생성한다 | Event-driven | P1 |
| REQ-SEM-003 | **THE SYSTEM SHALL** 커뮤니티 탐지 알고리즘을 사용해 관련 코드 엔티티를 클러스터링한다 | Ubiquitous | P1 |
| REQ-SEM-004 | **THE SYSTEM SHALL** 계층 레벨(0=세밀, 1=거침 등) 기준으로 커뮤니티를 관리한다 | Ubiquitous | P1 |

---

### 3.2 MCP 프로토콜 요구사항

#### 3.2.1 트랜스포트 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-TRP-001 | **THE SYSTEM SHALL** stdio 트랜스포트를 지원한다 | Ubiquitous | P0 |
| REQ-TRP-002 | **THE SYSTEM SHALL** SSE(Server-Sent Events) 트랜스포트를 지원한다 | Ubiquitous | P1 |
| REQ-TRP-003 | **THE SYSTEM SHALL** Streamable HTTP 트랜스포트를 지원한다 | Ubiquitous | P2 |
| REQ-TRP-004 | **THE SYSTEM SHALL** JSON-RPC 2.0 메시지 핸들링을 구현한다 | Ubiquitous | P0 |
| REQ-TRP-005 | **WHERE** OAuth 2.1 인증이 활성화되어 있는 경우, **THE SYSTEM SHALL** 인증된 클라이언트만 접근을 허용한다 | Optional features | P2 |

#### 3.2.2 Tools 요구사항

##### 그래프 쿼리 툴

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-TLS-001 | **WHEN** `query_codebase` 툴이 자연어 쿼리와 스코프로 호출된 경우, **THE SYSTEM SHALL** 지정된 스코프(all, functions, classes, files) 내에서 매칭되는 코드 엔티티를 반환한다 | Event-driven | P0 |
| REQ-TLS-002 | **WHEN** `find_dependencies` 툴이 엔티티 이름, 방향, 깊이로 호출된 경우, **THE SYSTEM SHALL** 지정된 방향(upstream, downstream, both)과 깊이로 의존성 그래프를 반환한다 | Event-driven | P0 |
| REQ-TLS-003 | **WHEN** `find_callers` 툴이 함수 이름과 최대 깊이로 호출된 경우, **THE SYSTEM SHALL** 지정 함수를 호출하는 모든 함수의 호출 경로를 반환한다 | Event-driven | P0 |
| REQ-TLS-004 | **WHEN** `find_callees` 툴이 함수 이름과 최대 깊이로 호출된 경우, **THE SYSTEM SHALL** 지정 함수가 호출하는 모든 함수의 호출 경로를 반환한다 | Event-driven | P0 |
| REQ-TLS-005 | **WHEN** `find_implementations` 툴이 인터페이스 이름으로 호출된 경우, **THE SYSTEM SHALL** 해당 인터페이스/추상 클래스의 모든 구현을 반환한다 | Event-driven | P0 |
| REQ-TLS-006 | **WHEN** `analyze_module_structure` 툴이 모듈 경로로 호출된 경우, **THE SYSTEM SHALL** 모듈 구조 분석(클래스, 함수, 의존성 개요)을 반환한다 | Event-driven | P0 |

##### 코드 조회 툴

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-TLS-007 | **WHEN** `get_code_snippet` 툴이 엔티티 이름과 컨텍스트 플래그로 호출된 경우, **THE SYSTEM SHALL** 엔티티의 소스코드를 반환하고, 컨텍스트 플래그가 참이면 앞뒤 지정 라인 수도 포함한다 | Event-driven | P0 |
| REQ-TLS-008 | **WHEN** `read_file_content` 툴이 파일 경로와 라인 범위로 호출된 경우, **THE SYSTEM SHALL** 지정 파일의 내용을 반환한다 | Event-driven | P0 |
| REQ-TLS-009 | **WHEN** `get_file_structure` 툴이 파일 경로로 호출된 경우, **THE SYSTEM SHALL** 파일 내 클래스·함수 구조 정보를 반환한다 | Event-driven | P0 |

##### GraphRAG 툴

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-TLS-010 | **WHEN** `global_search` 툴이 쿼리와 커뮤니티 레벨로 호출된 경우, **THE SYSTEM SHALL** 커뮤니티 요약을 사용해 코드베이스 전체에 대한 매크로 레벨 답변을 반환한다 | Event-driven | P1 |
| REQ-TLS-011 | **WHEN** `local_search` 툴이 쿼리와 컨텍스트 엔티티로 호출된 경우, **THE SYSTEM SHALL** 그래프 구조와 엔티티 정보를 결합해 상세한 답변을 반환한다 | Event-driven | P1 |

##### 편집·관리 툴

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-TLS-012 | **WHEN** `suggest_refactoring` 툴이 엔티티 이름과 리팩터링 타입으로 호출된 경우, **THE SYSTEM SHALL** 리팩터링 제안과 영향 범위 분석을 반환한다 | Event-driven | P2 |
| REQ-TLS-013 | **WHEN** `reindex_repository` 툴이 경로와 증분 플래그로 호출된 경우, **THE SYSTEM SHALL** 지정 리포지토리를 인덱싱(증분 또는 전체)하고 결과를 반환한다 | Event-driven | P0 |
| REQ-TLS-014 | **WHEN** `execute_shell_command` 툴이 명령, 작업 디렉터리, 타임아웃으로 호출된 경우, **THE SYSTEM SHALL** 셸 명령을 실행하고 결과를 반환한다 | Event-driven | P1 |

#### 3.2.3 Resources 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-RSC-001 | **WHEN** `codegraph://entities/{entity_id}` 리소스가 요청된 경우, **THE SYSTEM SHALL** 코드 엔티티 상세 정보를 JSON으로 반환한다 | Event-driven | P0 |
| REQ-RSC-002 | **WHEN** `codegraph://files/{file_path}` 리소스가 요청된 경우, **THE SYSTEM SHALL** 파일 구조 정보가 포함된 리소스를 반환한다 | Event-driven | P0 |
| REQ-RSC-003 | **WHEN** `codegraph://communities/{community_id}` 리소스가 요청된 경우, **THE SYSTEM SHALL** 커뮤니티(모듈 클러스터) 요약을 반환한다 | Event-driven | P1 |
| REQ-RSC-004 | **WHEN** `codegraph://stats` 리소스가 요청된 경우, **THE SYSTEM SHALL** 코드베이스 통계(총 파일 수, 함수 수, 클래스 수, 언어 비율, 최종 인덱스 일시)를 반환한다 | Event-driven | P0 |

#### 3.2.4 Prompts 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-PRM-001 | **WHEN** `code_review` 프롬프트가 파일 경로와 중점 영역으로 호출된 경우, **THE SYSTEM SHALL** 코드 리뷰 수행을 위한 프롬프트 템플릿을 반환한다 | Event-driven | P1 |
| REQ-PRM-002 | **WHEN** `explain_codebase` 프롬프트가 호출된 경우, **THE SYSTEM SHALL** 코드베이스 전체 설명 생성을 위한 프롬프트 템플릿을 반환한다 | Event-driven | P1 |
| REQ-PRM-003 | **WHEN** `implement_feature` 프롬프트가 기능 설명으로 호출된 경우, **THE SYSTEM SHALL** 신규 기능 구현 가이드 프롬프트를 반환한다 | Event-driven | P1 |
| REQ-PRM-004 | **WHEN** `debug_issue` 프롬프트가 에러 메시지로 호출된 경우, **THE SYSTEM SHALL** 디버깅 지원 프롬프트를 반환한다 | Event-driven | P1 |
| REQ-PRM-005 | **WHEN** `refactor_guidance` 프롬프트가 타겟 엔티티로 호출된 경우, **THE SYSTEM SHALL** 리팩터링 가이드 프롬프트를 반환한다 | Event-driven | P2 |
| REQ-PRM-006 | **WHEN** `test_generation` 프롬프트가 함수 이름으로 호출된 경우, **THE SYSTEM SHALL** 테스트 코드 생성 지원 프롬프트를 반환한다 | Event-driven | P1 |

---

### 3.3 스토리지 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-STR-001 | **THE SYSTEM SHALL** SQLite를 사용해 그래프 DB를 관리한다 | Ubiquitous | P0 |
| REQ-STR-002 | **THE SYSTEM SHALL** AST 캐시를 파일 캐시로 관리한다 | Ubiquitous | P0 |
| REQ-STR-003 | **THE SYSTEM SHALL** 임베딩(벡터)을 벡터 스토어로 관리한다 | Ubiquitous | P1 |
| REQ-STR-004 | **WHEN** 파일이 변경된 경우, **THE SYSTEM SHALL** Git diff를 사용해 변경 파일만 재인덱싱한다 | Event-driven | P0 |

---

### 3.4 인덱스 관리 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-IDX-001 | **WHEN** 사용자가 `codegraph-mcp serve` 명령을 실행한 경우, **THE SYSTEM SHALL** 지정 리포지토리 인덱스를 생성하거나 로드한다 | Event-driven | P0 |
| REQ-IDX-002 | **WHEN** 증분 인덱싱이 요청된 경우, **THE SYSTEM SHALL** Git diff를 분석해 변경된 파일만 재처리한다 | Event-driven | P0 |
| REQ-IDX-003 | **WHEN** 전체 인덱싱이 요청된 경우, **THE SYSTEM SHALL** 모든 파일을 재분석해 인덱스를 재구축한다 | Event-driven | P0 |
| REQ-IDX-004 | **THE SYSTEM SHALL** .gitignore 패턴에 따라 파일을 필터링한다 | Ubiquitous | P0 |

---

### 3.5 CLI 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-CLI-001 | **WHEN** 사용자가 `codegraph-mcp serve` 명령을 실행한 경우, **THE SYSTEM SHALL** MCP 서버를 기동한다 | Event-driven | P0 |
| REQ-CLI-002 | **WHEN** 사용자가 `--repo` 옵션을 지정한 경우, **THE SYSTEM SHALL** 지정된 리포지토리 경로를 인덱스 대상으로 삼는다 | Event-driven | P0 |
| REQ-CLI-003 | **WHEN** 사용자가 `--help` 옵션을 지정한 경우, **THE SYSTEM SHALL** 사용 방법과 옵션 도움말 텍스트를 표시한다 | Event-driven | P0 |
| REQ-CLI-004 | **THE SYSTEM SHALL** `pip install codegraph-mcp`로 설치 가능한 패키지로 제공한다 | Ubiquitous | P0 |

---

## 4. 비기능 요구사항

### 4.1 성능 요구사항

| ID | 요구사항 | EARS 패턴 | 목표값 | 우선순위 |
|----|----------|-----------|--------|----------|
| REQ-NFR-001 | **THE SYSTEM SHALL** 10만 라인 규모의 코드베이스를 30초 이내에 인덱싱한다 | Ubiquitous | < 30초 | P0 |
| REQ-NFR-002 | **THE SYSTEM SHALL** 증분 인덱싱을 2초 이내에 완료한다 | Ubiquitous | < 2초 | P0 |
| REQ-NFR-003 | **THE SYSTEM SHALL** 쿼리에 500밀리초 이내로 응답한다 | Ubiquitous | < 500ms | P0 |
| REQ-NFR-004 | **THE SYSTEM SHALL** 기동을 2초 이내에 완료한다 | Ubiquitous | < 2초 | P0 |

### 4.2 리소스 요구사항

| ID | 요구사항 | EARS 패턴 | 목표값 | 우선순위 |
|----|----------|-----------|--------|----------|
| REQ-NFR-005 | **WHILE** 서버가 구동 중인 경우, **THE SYSTEM SHALL** 메모리 사용량을 500MB 이하로 유지한다 | State-driven | < 500MB | P0 |
| REQ-NFR-006 | **THE SYSTEM SHALL** 10만 라인당 디스크 사용량을 100MB 이하로 유지한다 | Ubiquitous | < 100MB/10만 라인 | P1 |

### 4.3 가용성 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-NFR-007 | **THE SYSTEM SHALL** 외부 DB 서비스 없이 동작한다(자급자족형/자체 완결형) | Ubiquitous | P0 |
| REQ-NFR-008 | **IF** 서버가 예기치 않게 크래시한 경우, **THEN THE SYSTEM SHALL** 다음 기동 시 기존 인덱스를 복구한다 | Unwanted behavior | P0 |

### 4.4 호환성 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-NFR-009 | **THE SYSTEM SHALL** Python 3.11 이상에서 동작한다 | Ubiquitous | P0 |
| REQ-NFR-010 | **THE SYSTEM SHALL** MCP Specification 1.0을 준수한다 | Ubiquitous | P0 |
| REQ-NFR-011 | **THE SYSTEM SHALL** GitHub Copilot, Claude Code, Cursor, Windsurf와 호환된다 | Ubiquitous | P0 |

### 4.5 보안 요구사항

| ID | 요구사항 | EARS 패턴 | 우선순위 |
|----|----------|-----------|----------|
| REQ-NFR-012 | **WHILE** 셸 명령 실행 툴이 사용되는 경우, **THE SYSTEM SHALL** 샌드박스 환경 또는 타임아웃 제한을 적용한다 | State-driven | P1 |
| REQ-NFR-013 | **THE SYSTEM SHALL** 로컬 파일시스템 접근을 지정된 리포지토리 경로로 제한한다 | Ubiquitous | P0 |

---

## 5. 지원 언어

### 5.1 Phase 1(P0 - MVP)

| 언어 | 확장자 | 지원 스코프 |
|------|--------|------------|
| Python | .py | 함수, 클래스, import, 호출 |
| TypeScript | .ts, .tsx | 함수, 클래스, 인터페이스, import, 호출 |

### 5.2 Phase 2(P1)

| 언어 | 확장자 | 지원 스코프 |
|------|--------|------------|
| Rust | .rs | 함수, 구조체, 열거형, impl, use, 호출 |
| JavaScript | .js, .jsx | 함수, 클래스, import, 호출 |

### 5.3 Phase 3(P2)

| 언어 | 확장자 |
|------|--------|
| Go | .go |
| Java | .java |
| C# | .cs |

---

## 6. 추적성 매트릭스

### 6.1 설계 컴포넌트 매핑

| 요구사항 ID | 설계 컴포넌트 | 소스 파일(예정) |
|------------|---------------|----------------|
| REQ-AST-* | AST Parser | src/codegraph_mcp/core/parser.py |
| REQ-GRF-* | Graph Engine | src/codegraph_mcp/core/graph.py |
| REQ-SEM-* | Semantic Analyzer | src/codegraph_mcp/core/semantic.py |
| REQ-TRP-* | MCP Protocol Layer | src/codegraph_mcp/server.py |
| REQ-TLS-* | MCP Tools | src/codegraph_mcp/mcp/tools.py |
| REQ-RSC-* | MCP Resources | src/codegraph_mcp/mcp/resources.py |
| REQ-PRM-* | MCP Prompts | src/codegraph_mcp/mcp/prompts.py |
| REQ-STR-* | Storage Layer | src/codegraph_mcp/storage/*.py |
| REQ-IDX-* | Indexer | src/codegraph_mcp/core/indexer.py |
| REQ-CLI-* | CLI | src/codegraph_mcp/__main__.py |
| REQ-NFR-* | 전체 컴포넌트 | - |

---

## 7. 수용 기준

### 7.1 MVP 수용 기준

- [ ] `pip install codegraph-mcp`로 설치 가능
- [ ] `codegraph-mcp serve --repo <path>`로 기동 가능
- [ ] Python/TypeScript AST 분석 정상 동작
- [ ] 기본 6개 툴(query_codebase, find_dependencies, find_callers, find_callees, get_code_snippet, read_file_content) 정상 동작
- [ ] 4개 리소스 타입 모두 접근 가능
- [ ] 10만 라인 규모 코드베이스에서 30초 이내 인덱싱 완료
- [ ] Claude Desktop / GitHub Copilot에서 동작 확인

### 7.2 Phase 2 수용 기준

- [ ] GraphRAG 기능(global_search, local_search) 정상 동작
- [ ] 커뮤니티 탐지 및 요약 생성 정상 동작
- [ ] 6개 Prompts 모두 사용 가능
- [ ] Rust 언어 지원

### 7.3 Phase 3 수용 기준

- [ ] 추가 언어 지원(Go, Java, C#)
- [ ] 벡터 검색 기반 시맨틱 검색
- [ ] 리팩터링 제안 툴

---

## 8. 용어집

| 용어 | 정의 |
|------|------|
| MCP | Model Context Protocol - AI 모델이 외부 툴/리소스에 접근하기 위한 프로토콜 |
| GraphRAG | Graph-based Retrieval Augmented Generation - 그래프 구조를 활용한 RAG |
| AST | Abstract Syntax Tree - 소스코드의 추상 구문 트리 |
| Tree-sitter | 고속 증분 파서 생성 라이브러리 |
| EARS | Easy Approach to Requirements Syntax - 요구사항 서술을 위한 구조화 형식 |
| 엔티티 | 코드 그래프의 노드(File, Module, Class, Function, Method) |
| 릴레이션 | 코드 그래프의 엣지(CALLS, IMPORTS, INHERITS, CONTAINS, IMPLEMENTS) |
| 커뮤니티 | 연관된 엔티티의 클러스터 |

---

## 9. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0.0 | 2025-11-26 | 초판 작성 | System |

---

## 10. 승인

| 역할 | 이름 | 서명 | 날짜 |
|------|------|------|------|
| 프로덕트 오너 | | | |
| 테크 리드 | | | |
| QA 리드 | | | |

---

**문서 상태**: Draft  
**헌법 준수 여부**: Article IV (EARS Format) ✓
```
