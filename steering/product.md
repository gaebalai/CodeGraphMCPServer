# Product Context

**Project**: CodeGraph MCP Server
**Last Updated**: 2025-12-11
**Version**: 2.9
**Synced With**: requirements-specification.md, design-*.md, CHANGELOG.md (v0.8.0)

---

## Product Vision

**Vision Statement**: 

Microsoft GraphRAG의 컨셉과 code-graph-rag의 구현을 참고하여, 제로 설정으로 기동 가능한 경량·고속 소스코드 분석 MCP 서버를 제공하고, AI 지원 개발의 생산성을 비약적으로 향상시킨다.

**Mission**: 

외부 데이터베이스가 필요 없는 자기완결형 아키텍처를 통해, MCP 대응 AI 도구(GitHub Copilot, Claude Code, Cursor 등)에서 코드베이스의 구조적 이해와 효율적인 코드 보완을 실현한다.

---

## Product Overview

### CodeGraph MCP Server란?

CodeGraph MCP Server는 소스코드 분석에 최적화된 MCP(Model Context Protocol) 서버이다. Tree-sitter 기반 AST 분석과 GraphRAG 기술을 결합하여, 코드베이스의 구조적 이해를 AI 어시스턴트에 제공한다.

기존 code-graph-rag와 달리, 외부 그래프 데이터베이스(Memgraph 등)를 필요로 하지 않으며, SQLite 기반의 내장 그래프 엔진으로 동작한다. 이를 통해  
`pip install codegraph-mcp && codegraph-mcp serve`  
라는 단일 명령으로 즉시 사용을 시작할 수 있다.

### Problem Statement

**문제점**:

현재의 AI 코딩 어시스턴트는 대규모 코드베이스의 전체 구조를 파악하는 데 한계가 있다. 파일 단위 이해에 머무르며, 모듈 간 의존성, 호출 그래프, 아키텍처 패턴을 인식하지 못한다. 또한 기존 code-graph-rag 솔루션은 외부 데이터베이스 설정이 필요해 도입 장벽이 높다.

### Solution

**해결 방안**:

CodeGraph MCP Server는 다음 접근을 통해 문제를 해결한다.

1. **제로 설정 기동**: 외부 의존성 없이 즉시 사용 가능  
2. **그래프 기반 이해**: 코드 엔티티와 관계를 그래프로 관리  
3. **GraphRAG 통합**: 커뮤니티 탐지와 LLM 요약을 통한 매크로 수준 이해  
4. **MCP Native**: Tools, Resources, Prompts를 활용한 포괄적 MCP 구현  
5. **증분 업데이트**: Git diff 기반의 효율적인 인덱스 갱신  

---

## Target Users

### Primary Users

#### 사용자 페르소나 1: AI 어시스턴트를 활용하는 개발자

**기본 정보**:

- **역할**: 소프트웨어 개발자  
- **조직 규모**: 소규모 ~ 대규모  
- **기술 수준**: 중급 ~ 고급  

**목표**:

- AI 지원을 통해 코딩 효율을 높이고 싶다  
- 대규모 코드베이스를 빠르게 이해하고 싶다  
- 기존 코드 변경 시 영향 범위를 정확히 파악하고 싶다  

**페인 포인트**:

- AI 어시스턴트가 코드베이스 전체를 이해하지 못함  
- 함수 호출 관계(Caller/Callee) 추적이 번거로움  
- 외부 도구 설정이 복잡해 도입을 포기하게 됨  

**사용 시나리오**:

- 코드베이스 전체 아키텍처 이해 (REQ-TLS-010)  
- 함수 변경 시 영향 범위 분석 (REQ-TLS-002, REQ-TLS-003)  
- 신규 기능 구현 전 기존 코드 조사 (REQ-TLS-001)  
---

#### 사용자 페르소나 2: 팀 리드 · 아키텍트

**기본 정보**:

- **역할**: 테크 리드 / 소프트웨어 아키텍트  
- **조직 규모**: 중규모 ~ 대규모  
- **기술 수준**: 고급  

**목표**:

- 코드베이스 품질을 유지·개선하고 싶다  
- 신규 멤버 온보딩을 효율화하고 싶다  
- 기술 부채를 가시화하고 관리하고 싶다  

**페인 포인트**:

- 코드베이스 전체 구조를 설명하는 데 많은 시간이 소요됨  
- 리팩터링 시 영향 범위 파악이 어렵고 느림  
- 모듈 간 의존성이 점점 복잡해짐  

**사용 시나리오**:

- 코드베이스 설명 자동 생성 (REQ-PRM-002)  
- 리팩터링 영향 분석 (REQ-TLS-012)  
- 모듈 구조 분석 (REQ-TLS-006)  

---

### Secondary Users

- **QA 엔지니어**: 테스트 대상 식별, 영향 범위 파악  
- **신규 합류 멤버**: 코드베이스 학습, 네비게이션  

---

## Competitive Landscape

### code-graph-rag 대비 차별점

| 관점 | code-graph-rag | CodeGraph MCP Server |
|------|----------------|---------------------|
| 아키텍처 | CLI + 인터랙티브 모드 | MCP Native Server |
| 그래프 DB | Memgraph(외부 의존) | SQLite + 내장 그래프 엔진 |
| 배포 | Docker 필수 | 단일 바이너리 / pip install |
| 기동 시간 | 무거움(DB 기동 포함) | 경량(초 단위) |
| MCP 통합 | 사후 대응 | 네이티브 설계 |
| 스코프 | 단일 리포지토리 | 멀티 리포지토리 지원 |
| 인덱스 업데이트 | 수동 / 파일 감시 | Git diff 기반 증분 업데이트 |
| GraphRAG 기능 | 없음 | 커뮤니티 요약 · 글로벌 쿼리 |

---

## Core Product Capabilities

### Must-Have Features (MVP - Phase 1)

1. **AST 분석 (Python, TypeScript)**  
   - **설명**: Tree-sitter 기반 AST 분석  
   - **사용자 가치**: 코드 구조의 정확한 추출  
   - **우선순위**: P0 (Critical)  
   - **요구사항**: REQ-AST-001, REQ-AST-002  

2. **그래프 쿼리 툴**  
   - **설명**: 6종의 그래프 쿼리 툴  
   - **사용자 가치**: 의존 관계·호출 관계 탐색  
   - **우선순위**: P0 (Critical)  
   - **요구사항**: REQ-TLS-001 ~ REQ-TLS-006  

3. **코드 조회 툴**  
   - **설명**: 3종의 코드 조회 툴  
   - **사용자 가치**: 소스코드의 효율적 조회  
   - **우선순위**: P0 (Critical)  
   - **요구사항**: REQ-TLS-007 ~ REQ-TLS-009  

4. **MCP 리소스**  
   - **설명**: 4종의 리소스 타입  
   - **사용자 가치**: 코드베이스 정보 접근  
   - **우선순위**: P0 (Critical)  
   - **요구사항**: REQ-RSC-001 ~ REQ-RSC-004  

5. **CLI 인터페이스**  
   - **설명**: serve, index 명령  
   - **사용자 가치**: 간단한 기동 및 인덱싱  
   - **우선순위**: P0 (Critical)  
   - **요구사항**: REQ-CLI-001 ~ REQ-CLI-004

### High-Priority Features (Phase 2)

6. **GraphRAG 기능**  
   - **설명**: global_search, local_search 툴  
   - **사용자 가치**: 매크로 수준의 코드베이스 이해  
   - **우선순위**: P1 (High)  
   - **요구사항**: REQ-TLS-010, REQ-TLS-011  

7. **커뮤니티 탐지**  
   - **설명**: 모듈 클러스터링 및 요약  
   - **사용자 가치**: 아키텍처 자동 이해  
   - **우선순위**: P1 (High)  
   - **요구사항**: REQ-SEM-001 ~ REQ-SEM-004  

8. **프롬프트 템플릿**  
   - **설명**: 6종 프롬프트  
   - **사용자 가치**: AI 어시스턴트와의 효율적 상호작용  
   - **우선순위**: P1 (High)  
   - **요구사항**: REQ-PRM-001 ~ REQ-PRM-006  

9. **Rust 언어 지원**  
   - **설명**: Rust AST 분석  
   - **사용자 가치**: Rust 프로젝트 대응  
   - **우선순위**: P1 (High)  
   - **요구사항**: REQ-AST-003  

### Future Features (Phase 3)

10. **추가 언어 지원**  
    - **설명**: Go, Java, C#  
    - **사용자 가치**: 더 많은 프로젝트 대응  
    - **우선순위**: P2 (Medium)  

11. **리팩터링 제안**  
    - **설명**: suggest_refactoring 툴  
    - **사용자 가치**: 코드 품질 향상 지원  
    - **우선순위**: P2 (Medium)  
    - **요구사항**: REQ-TLS-012  

12. **벡터 검색**  
    - **설명**: 시맨틱 검색  
    - **사용자 가치**: 고급 검색 기능  
    - **우선순위**: P2 (Medium)  
    - **요구사항**: REQ-STR-003  

---

## Product Principles


### 디자인 원칙

1. **제로 구성 기동**
   - 외부 의존성을 최소화하여, 설치 직후 바로 사용 가능해야 한다

2. **경량·고속**
   - 외부 DB 없이 동작하며, 기동 2초 이내, 10만 라인 기준 30초 이내 인덱싱을 목표로 한다

3. **MCP First**
   - Tools, Resources, Prompts를 적극 활용한 포괄적인 MCP 네이티브 구현을 지향한다

4. **증분 업데이트**
   - Git diff를 활용하여 변경된 파일만 재인덱싱한다

---

## Success Metrics

### 핵심 성과 지표(KPIs)

#### 기술 지표 (Technical Metrics)

| 지표 | 목표 | 실제(v0.5.0) | 요구사항 |
|------|------|--------------|----------|
| 최초 인덱싱 (10만 라인) | < 30초 | **0.63초** (67 files) | REQ-NFR-001 |
| 증분 인덱싱 | < 2초 | < 0.5초 | REQ-NFR-002 |
| 쿼리 응답 시간 | < 500ms | < 2ms | REQ-NFR-003 |
| 기동 시간 | < 2초 | < 1초 | REQ-NFR-004 |
| 메모리 사용량 | < 500MB | ~200MB | REQ-NFR-005 |
| 엔티티/초 처리량 | - | **1,495** (47배 개선) | - |

#### 제품 지표 (향후)

| 지표 | 목표 |
|------|------|
| PyPI 다운로드 수 | 월 1,000+ |
| GitHub Stars | 500+ |
| 활성 사용자 수(추정) | 100+ |

---

## Product Roadmap

### Phase 1: MVP (Week 1-4)

**목표**: 기본 기능 릴리스

**기능**:

- Python / TypeScript AST 분석
- 기본 툴(query, dependencies, callers, callees, code_snippet, file_content)
- SQLite 스토리지
- CLI 인터페이스
- stdio 트랜스포트

**성공 기준**:

- `pip install codegraph-mcp`로 설치 가능
- Claude Desktop / GitHub Copilot에서 동작 확인
- 10만 라인 규모 코드베이스를 30초 이내에 인덱싱 완료

---

### Phase 2: GraphRAG (Week 5-6) ✅ COMPLETED

**목표**: GraphRAG 기능 구현

**기능**:

- ✅ 커뮤니티 탐지 (`core/community.py`)
- ✅ LLM 통합(요약 생성) (`core/llm.py`, `core/semantic.py`)
- ✅ global_search, local_search (`core/graphrag.py`)
- ✅ 6종 Prompts (`mcp/prompts.py`)
- ⏳ Rust 언어 지원 (Phase 3로 이동)

**구현 상태**:

| 컴포넌트 | 파일 | 테스트 |
|----------|------|--------|
| LLM 통합 | `core/llm.py` | `test_llm.py` (11 tests) |
| GraphRAG 검색 | `core/graphrag.py` | `test_graphrag.py` (14 tests) |
| 커뮤니티 탐지 | `core/community.py` | `test_community.py` |
| 시맨틱 분석 | `core/semantic.py` | `test_semantic.py` |
| 통합 테스트 | - | `test_graphrag_integration.py` (13 tests) |

**총 테스트 수**: 173개 (172 passed, 1 skipped)

**성공 기준**:

- ✅ 코드베이스 전체 설명 생성 가능
- ✅ 커뮤니티 요약 정상 동작

---

### Phase 3: Polish & Extensions (Week 7-8) ✅ COMPLETED

**목표**: 품질 향상 및 확장

**기능**:

- ✅ Rust 언어 지원 (`languages/rust.py`)
- ✅ JavaScript 언어 지원 (`languages/javascript.py`)
- ✅ SSE 트랜스포트 (`server.py`)
- ✅ 리팩터링 제안 (`mcp/tools.py`)
- ✅ 문서 정비 (`docs/`)
- ✅ PyPI 릴리스 준비

**구현 상태**:

| 컴포넌트 | 파일 | 상태 |
|----------|------|------|
| Rust 파서 | `languages/rust.py` | ✅ Complete |
| JavaScript 파서 | `languages/javascript.py` | ✅ Complete |
| SSE 트랜스포트 | `server.py` | ✅ Complete |
| API 문서 | `docs/api.md` | ✅ Complete |
| 설정 가이드 | `docs/configuration.md` | ✅ Complete |
| 예제 | `docs/examples.md` | ✅ Complete |
| CHANGELOG | `CHANGELOG.md` | ✅ Complete |
| Release Notes | `RELEASE_NOTES.md` | ✅ Complete |

**총 테스트 수**: 182개 (182 passed, 1 skipped)

**성능**:
- 인덱싱: 696 엔티티 / 21초
- 쿼리: 평균 < 2ms

**성공 기준**:

- ✅ 추가 언어 AST 분석 정상 동작
- ✅ 문서 완비
- ✅ PyPI 패키지 빌드 성공

---

### Phase 4: Future (Planned)

**목표**: 추가 확장

**예정 기능**:

- 추가 언어 지원 (Go, Java, C#)
- 벡터 검색 최적화
- MkDocs 기반 문서 사이트
- GitHub Actions CI/CD
- 10만 라인 이상 리포지토리 최적화


---

## User Workflows

### 주요 워크플로우 1: 코드베이스 이해

**사용자 목표**: 새로운 코드베이스의 전체 구조를 이해한다

**단계**:

1. 사용자: `codegraph-mcp serve --repo /path/to/project` 실행
2. 시스템: 인덱스 생성 후 MCP 서버 기동
3. 사용자: AI 어시스턴트에 “이 프로젝트의 주요 컴포넌트를 설명해줘” 질문
4. 시스템: global_search 툴로 커뮤니티 요약 조회
5. 시스템: 주요 모듈과 책임을 설명
6. 사용자: 프로젝트 전체 구조를 이해

**성공 기준**:

- 전체 워크플로우 완료까지 < 2분
- 주요 컴포넌트가 정확히 식별됨

---

### 주요 워크플로우 2: 영향 범위 분석

**사용자 목표**: 함수 변경 시 영향 범위를 파악한다

**단계**:

1. 사용자: “UserService.authenticate 메서드를 변경하면 영향 범위는?” 질문
2. 시스템: find_callers 툴로 호출자 검색
3. 시스템: 직접·간접 영향 범위 목록 표시
4. 사용자: 영향 범위를 확인하고 테스트 계획 수립

**성공 기준**:

- 호출자가 정확히 식별됨
- 간접 의존성까지 표시됨

---

## Domain Concepts

### 핵심 개념

1. **Entity(엔티티)**: 코드 그래프의 노드  
   - File, Module, Class, Function, Method

2. **Relation(관계)**: 코드 그래프의 엣지  
   - CALLS, IMPORTS, INHERITS, CONTAINS, IMPLEMENTS

3. **Community(커뮤니티)**: 연관된 엔티티의 클러스터  
   - 계층 레벨(0=세밀, 1=거침 등)

4. **MCP(Model Context Protocol)**: AI 모델이 외부 툴·리소스에 접근하기 위한 프로토콜

5. **GraphRAG**: 그래프 구조를 활용한 RAG(Retrieval Augmented Generation)

---

## Constraints & Requirements

### 기술적 제약

- **Python 3.11+**: REQ-NFR-009
- **MCP Specification 1.0**: REQ-NFR-010
- **외부 DB 불필요**: 자기완결형 아키텍처

### 비기능 요구사항

- **성능**: REQ-NFR-001 ~ REQ-NFR-004
- **리소스**: REQ-NFR-005 ~ REQ-NFR-006
- **보안**: REQ-NFR-012 ~ REQ-NFR-013
- **호환성**: REQ-NFR-009 ~ REQ-NFR-011

---

## Future Extensions

1. **VS Code Extension**: 직접 통합
2. **Web UI**: 그래프 시각화 대시보드
3. **멀티 리포지토리**: 모노레포/멀티레포 대응
4. **실시간 업데이트**: LSP 통합
5. **코드 생성**: 템플릿 기반 코드 생성 지원

---

## References

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [code-graph-rag](https://github.com/vitali87/code-graph-rag)
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

## Changelog

### Version 2.6 (2025-11-27)

- v0.7.0 릴리스
  - `watch` 명령: 파일 감시 및 자동 재인덱싱
    - `--debounce` 옵션(기본값: 1.0초)
    - `--community` 플래그로 재인덱싱 후 커뮤니티 탐지
  - GitHub Actions CI/CD
    - CI: Python 3.11/3.12 테스트, ruff lint, mypy 타입 체크, Codecov 커버리지
    - Release: 태그 푸시 시 자동 PyPI 릴리스
- 테스트: 308 passed, 1 skipped

### Version 2.5 (2025-11-27)

- v0.6.0 릴리스
  - 대규모 리포지토리 지원(230K+ 엔티티)
  - 커뮤니티 탐지 성능 개선(샘플링, 배치 처리)
  - Rust 컴파일러 리포지토리에서 검증
  - entity_id 부분 일치 검색
  - 자동 커뮤니티 탐지
  - query_codebase 개선
- 테스트: 300 passed

### Version 2.3 (2025-11-27)

- v0.5.0 릴리스(47배 성능 개선)
- 배치 DB 쓰기 구현
- 11개 언어 지원: Python, TypeScript, JavaScript, Rust, Go, Java, PHP, C#, C++, HCL, Ruby
- 테스트: 285 passed
- PyPI: codegraph-mcp-server v0.5.0

### Version 2.0 (2025-11-26)

- 설계 문서(design-*.md)와 동기화
- ADR-001~010 결정 사항 반영
- 요구사항 정의서와 정합성 확인
- Phase 2(GraphRAG) 완료 반영
- 구현 상태(173 테스트, 172 passed) 추가
- Rust 언어 지원을 Phase 3로 이동
- Phase 3(Polish & Extensions) 완료 반영
- 전체 태스크 완료(TASK-001~064)
- 테스트: 182 passed

### Version 1.0 (2025-11-26)

- 초기 제품 컨텍스트 작성

---

**Last Updated**: 2025-11-27
**Maintained By**: ITDA SDD
