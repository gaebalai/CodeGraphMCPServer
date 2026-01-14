# 아키텍처 결정 기록(ADR)

## 개요

이 문서는 CodeGraph MCP Server의 설계에서 이루어진 중요한 아키텍처 결정을 기록합니다.  
각 ADR은 결정의 배경, 검토한 선택지, 결정 내용, 그리고 그 영향을 명확히 합니다.

**관련 요구사항**: 모든 요구사항에 횡단적으로 영향

---

## ADR-001: Library-First 아키텍처 패턴 채택

### 상태
**승인됨** (2024-01)

### 컨텍스트
CodeGraph MCP Server는 여러 MCP 클라이언트(Claude Desktop, GitHub Copilot, Cursor 등)에서 사용됩니다.  
아키텍처 패턴으로 다음과 같은 선택지가 존재했습니다.

1. **Monolithic Server**: 모든 기능을 단일 프로세스로 제공
2. **Microservices**: 기능별로 분산 서비스화
3. **Library-First**: 핵심 기능을 라이브러리로 설계하고, 얇은 MCP 계층을 통해 공개

### 결정
**Library-First 패턴**을 채택합니다.

```
┌─────────────────────────────────────────┐
│           MCP Server Layer              │  ← 얇은 래퍼
│  (Tools, Resources, Prompts정의)        │
├─────────────────────────────────────────┤
│           Core Library Layer            │  ← 비즈니스 로직
│  (ASTParser, GraphEngine, Indexer...)   │
├─────────────────────────────────────────┤
│           Storage Layer                 │  ← 데이터 영속화
│  (SQLite, Cache, Vector)                │
└─────────────────────────────────────────┘
```

### 근거
1. **테스트 용이성**: 라이브러리 계층은 MCP 프로토콜에 의존하지 않아 단위 테스트 가능
2. **재사용성**: CLI 도구, Web API 등으로의 확장이 용이
3. **관심사의 분리**: 프로토콜 처리와 비즈니스 로직을 명확히 분리
4. **단계적 개발**: 핵심 기능을 먼저 안정화하고, 인터페이스를 이후에 추가 가능

### 영향
- **긍정적 영향**:
  - 테스트 커버리지 향상(목표 80% 이상)
  - 향후 확장 용이
  - 코드 가독성 향상
- **부정적 영향**:
  - 계층 간 의존성 관리 필요
  - 초기 설계에 시간 소요

### 관련 요구사항
- REQ-NFR-001 (테스트 용이성)
- REQ-NFR-002 (확장성)

---

## ADR-002: SQLite 채택 (Neo4j / RedisGraph 미채택)

### 상태
**승인됨** (2024-01)

### 컨텍스트
코드 그래프 데이터의 영속화를 위해 사용할 데이터베이스를 선정해야 했습니다.  
검토한 선택지는 다음과 같습니다.

| 선택지 | 특징 |
|------|------|
| **Neo4j** | 본격적인 그래프 DB, Cypher 쿼리, 고기능 |
| **RedisGraph** | 인메모리 그래프 DB, 고속, Cypher 지원 |
| **SQLite** | 관계형 DB, 제로 설정, 임베디드 |
| **DuckDB** | 분석 특화, 컬럼 지향, 임베디드 |

### 결정
**SQLite**를 주요 스토리지로 채택합니다.

### 근거
1. **제로 설정**: 외부 프로세스 불필요, 파일 기반으로 즉시 사용 가능
2. **이식성**: 단일 파일로 프로젝트 간 이동이 용이
3. **충분한 성능**: 10만 엔티티 규모에서는 충분한 성능
4. **성숙도**: 안정성이 높고 신뢰성 있는 실적
5. **MCP 철학**: 로컬 퍼스트, 경량 설치

```python
# 그래프 연산은 애플리케이션 계층에서 구현
class GraphEngine:
    def __init__(self, db_path: Path):
        self._graph = nx.DiGraph()  # NetworkX로 그래프 연산
        self._storage = SQLiteStorage(db_path)  # SQLite로 영속화
```

### 영향
- **긍정적 영향**: 
  - 설치가 간단(pip install만으로 가능)
  - CI/CD 환경에서 테스트 용이
  - 오프라인 환경에서도 동작
- **부정적 영향**: 
  - 복잡한 그래프 쿼리는 애플리케이션 계층에서 구현 필요
  - 초대규모 리포지토리에서는 성능 한계 존재(10만 엔티티 초과)

### 검토 후 배제한 대안의 사유
- **Neo4j**: 외부 서버 필수, 설정 복잡, 라이선스 제약
- **RedisGraph**: Redis 서버 필수, 인메모리 특성으로 영속화에 한계
- **DuckDB**: 그래프 연산에 최적화되어 있지 않음

### 관련 요구사항
- REQ-STR-001(영속화)
- REQ-NFR-003(설치 용이성)

---

## ADR-003: Tree-sitter 기반 AST 분석

### 상태
**승인됨** (2024-01)

### 컨텍스트
여러 언어의 소스 코드를 분석하여 추상 구문 트리(AST)를 획득하는 방법을 선택해야 했습니다.

검토한 선택지는 다음과 같습니다.

| 선택지             | 특징                                    |
| --------------- | ------------------------------------- |
| **Tree-sitter** | 범용 파서, 증분 파싱, 다언어 지원                  |
| **언어별 파서**      | ast(Python), typescript-parser 등, 고정밀 |
| **정규식 기반**      | 경량, 단순, 정확도 낮음                        |
| **LSP 통합**      | 언어 서버 활용, 고정밀, 무거움                    |

### 결정
**Tree-sitter**를 채택합니다.

### 근거
1. **다언어 지원**: Python, TypeScript, JavaScript, Rust 등을 통합 API로 분석 가능
2. **증분 분석**: 부분 변경 시 재분석이 고속
3. **내결함성**: 문법 오류가 있어도 부분 파싱 가능
4. **커뮤니티**: GitHub 주도 개발, 광범위한 채택

```python
# 통합 API로 여러 언어를 분석
LANGUAGE_CONFIG = {
    "python": {
        "parser": "tree_sitter_python",
        "extensions": [".py"],
        "queries": {...}
    },
    "typescript": {
        "parser": "tree_sitter_typescript",
        "extensions": [".ts", ".tsx"],
        "queries": {...}
    }
}
```

### 영향
- **긍정적 영향**: 
  - 설정만으로 신규 언어 추가 가능
  - 문법 오류에 강인
  - 고속 증분 업데이트
- **ネガテ부정적 영향ィブ**: 
  - 타입 정보 획득에 한계(정적 분석 수준)
  - 쿼리 패턴을 언어별로 정의해야 함

### 관련 요구사항
- REQ-AST-001~005(AST 분석 관련)
- REQ-NFR-004(다언어 지원)

---

## ADR-004: MCP SDK (Python) 채택

### 상태
**승인됨** (2024-01)

### 컨텍스트
MCP 프로토콜을 구현하는 방법을 선택해야 했습니다.

검토한 선택지는 다음과 같습니다.

| 선택지                      | 특징                         |
| ------------------------ | -------------------------- |
| **MCP SDK (Python)**     | Anthropic 공식, 타입 안전, 문서 충실 |
| **MCP SDK (TypeScript)** | Anthropic 공식, Node.js 환경   |
| **자체 구현**                | JSON-RPC 2.0 직접 구현, 유연성 높음 |

### 결정
**MCP SDK (Python)**를 채택합니다.

### 근거
1. **공식 지원**: Anthropic 제공, 사양 변경에 대한 추적 용이
2. **Python 생태계**: Tree-sitter, NetworkX 등과의 높은 궁합
3. **타입 안전성**: Pydantic 기반 타입 체크 및 자동 검증
4. **비동기 지원**: asyncio 네이티브, 높은 동시성

```python
from mcp.server import Server
from mcp.types import Tool, Resource, Prompt

server = Server("codegraph")

@server.tool()
async def query_codebase(query: str) -> list[dict]:
    """타입 안전한 도구 정의"""
    return await core.query(query)
```

### 영향
- **긍정적 영향**: 
  - 개발 속도 향상
  - 프로토콜 준수 보장
  - 에러 핸들링 단순화
- **부정적 영향**: 
  - SDK 버전 업데이트에 대한 지속적인 추적 필요
  - SDK 제약 범위 내에서의 구현 필요

### 관련 요구사항
- REQ-TLS-001~014(도구 정의)
- REQ-RSC-001~004(리소스 정의)
- REQ-PRM-001~006(프롬프트 정의)

---

## ADR-005: NetworkX를 활용한 그래프 연산

### 상태
**승인됨** (2024-01)

### 컨텍스트
메모리 상에서 그래프를 처리하기 위한 라이브러리를 선정해야 했습니다.

검토한 선택지는 다음과 같습니다.

| 선택지            | 특징                       |
| -------------- | ------------------------ |
| **NetworkX**   | 범용적, 풍부한 알고리즘, 성숙        |
| **igraph**     | 고속, C 기반 구현, 대규모 그래프에 적합 |
| **graph-tool** | 고성능, C++ 기반, 설치 복잡       |
| **자체 구현**      | 경량, 최적화 가능               |

### 결정
**NetworkX**를 채택합니다.

### 근거
1. **풍부한 알고리즘**: 커뮤니티 탐지, 최단 경로, 중심성 계산 등 기본 제공
2. **낮은 학습 비용**: 문서가 충실하고 널리 사용됨
3. **Python 네이티브**: 추가 의존성이 적음
4. **충분한 성능**: 목표 규모(약 10만 노드)에서는 충분

```python
import networkx as nx

# 커뮤니티 탐지
communities = nx.community.louvain_communities(graph)

# 최단 경로
path = nx.shortest_path(graph, source, target)

# 중심성 계산
centrality = nx.pagerank(graph)
```

### 영향
- **긍정적 영향**: 
  - 다양한 그래프 알고리즘을 즉시 활용 가능
  - 디버깅 및 시각화 도구와의 연계 용이
- **부정적 영향**: 
  - 초대규모 그래프(100만 노드 이상)에서는 성능 한계
  - 메모리 사용량이 큼

### 관련 요구사항
- REQ-GRF-001~006(그래프 구축 관련)
- REQ-SEM-001~004(시맨틱 분석)

---

## ADR-006: Pydantic을 이용한 데이터 모델링

### 상태
**승인됨** (2024-01)

### 컨텍스트
도메인 객체의 데이터 모델링 방식을 선정해야 했습니다.

검토한 선택지는 다음과 같습니다.

| 선택지             | 특징                  |
| --------------- | ------------------- |
| **Pydantic**    | 타입 검증, 직렬화, 고기능     |
| **dataclasses** | 표준 라이브러리, 경량, 단순    |
| **attrs**       | 고성능, 유연성, 슬롯 지원     |
| **TypedDict**   | 타입 힌트 전용, 런타임 검증 없음 |

### 결정
**Pydantic v2**를 채택합니다.

### 근거
1. **MCP SDK와의 통합**: MCP SDK가 Pydantic 기반
2. **자동 검증**: 입력 데이터 검증을 선언적으로 정의 가능
3. **직렬화 지원**: JSON 변환 자동화
4. **IDE 지원**: 강력한 타입 추론

```python
from pydantic import BaseModel, Field

class Entity(BaseModel):
    """타입 안전한 엔티티 모델"""
    id: str = Field(..., description="고유 식별자")
    name: str = Field(..., description="엔티티 이름")
    type: EntityType = Field(..., description="엔티티 유형")
    file_path: Path = Field(..., description="파일 경로")
    
    model_config = {"frozen": True}  # 불변 객체
```

### 영향
- **긍정적 영향**: 
  - 데이터 무결성 보장
  - API 문서 자동 생성에 활용 가능
  - 직렬화/역직렬화 방식 통일
- **부정적 영향**: 
  - dataclasses 대비 약간의 오버헤드
  - Pydantic v1 → v2 마이그레이션 시 주의 필요

### 관련 요구사항
- REQ-AST-001(파싱 결과 모델링)
- REQ-NFR-001(타입 안전성)

---

## ADR-007: 비동기 I/O(asyncio) 전면 채택

### 상태
**승인됨** (2024-01)

### 컨텍스트
I/O 처리의 구현 방식을 선정합니다.

검토한 선택지:

| 선택지 | 특징 |
|------|------|
| **asyncio** | Python 표준, 비동기 I/O, 높은 동시성 |
| **threading** | 스레드 기반, GIL 제약 |
| **multiprocessing** | 프로세스 기반, 무거움 |
| **동기 처리** | 단순함, 블로킹 |

### 결정
**asyncio 기반 비동기 I/O**를 전면 채택합니다.

### 근거
1. **MCP SDK 요구사항**: MCP SDK가 asyncio 기반
2. **높은 동시성**: 여러 클라이언트의 동시 요청 대응
3. **I/O 바운드 최적화**: 파일 읽기, DB 접근이 주요 처리
4. **리소스 효율**: 스레드보다 경량

```python
import asyncio
import aiosqlite

async def index_repository(path: Path) -> None:
    """비동기로 리포지토리를 인덱싱"""
    async with aiosqlite.connect(db_path) as db:
        for file in await asyncio.to_thread(list_files, path):
            ast = await asyncio.to_thread(parse_file, file)
            await store_entities(db, ast.entities)
```

### 영향
- **긍정적 영향**: 
  - 높은 병렬 처리 성능
  - 리소스 효율이 좋음
  - MCP SDK와 자연스러운 통합
- **부정적 영향**: 
  - 비동기 코드의 복잡성
  - 디버깅이 어려울 수 있음
  - 동기 라이브러리 통합 시 `to_thread`가 필요

### 관련 요구사항
- REQ-NFR-002 (병렬 처리)
- REQ-IDX-003 (증분 인덱싱)

---

## ADR-008: LRU 캐시 전략

### 상태
**승인됨** (2024-01)

### 컨텍스트
성능 최적화를 위한 캐시 전략을 선정합니다.

검토한 선택지:

| 선택지               | 특징                    |
| ----------------- | --------------------- |
| **LRU**           | 가장 오래전에 접근한 항목 제거, 단순 |
| **LFU**           | 사용 빈도가 가장 낮은 항목 제거    |
| **TTL**           | 시간 기반 만료              |
| **Write-through** | 쓰기 시 캐시를 함께 갱신        |

### 결정
**LRU (Least Recently Used)**기반 캐시 전략을 채택합니다.

### 근거
1. **접근 패턴**: 최근 편집한 파일이 반복적으로 접근됨
2. **구현 단순**: Python 표준 functools.lru_cache 활용 가능
3. **메모리 효율**: 크기 상한 설정 가능
4. **예측 가능성**: 동작이 직관적이고 이해하기 쉬움

```python
from functools import lru_cache
from cachetools import TTLCache

# AST 캐시(파일 내용 기반)
@lru_cache(maxsize=500)
def get_cached_ast(file_hash: str) -> AST:
    ...

# 쿼리 결과 캐시(TTL 포함)
query_cache = TTLCache(maxsize=100, ttl=300)
```

### 영향
- **긍정적 영향**: 
  - 반복 쿼리의 고속화
  - AST 재파싱 회피
  - 메모리 사용량 제어
- **부정적 영향**: 
  - 캐시 무효화 로직 필요
  - 메모리 오버헤드

### 관련 요구사항
- REQ-STR-003 (캐시 메커니즘)
- REQ-NFR-005 (응답 시간)

---

## ADR-009: 시맨틱 버저닝(SemVer) 채택

### 상태
**승인됨** (2024-01)

### 컨텍스트
프로젝트의 버전 관리 방식을 선정합니다.

### 결정
**시맨틱 버저닝(SemVer)**을 채택합니다.

```
MAJOR.MINOR.PATCH

예: 1.2.3
- MAJOR: 하위 호환이 깨지는 변경
- MINOR: 하위 호환을 유지하는 기능 추가
- PATCH: 하위 호환을 유지하는 버그 수정
```

### 근거
1. **업계 표준**: Python 패키지에서 널리 채택
2. **명확한 기대값**: 버전 번호만으로 변경 성격을 파악 가능
3. **의존성 관리**: pip/poetry에서 의존성 버전 지정이 용이

### 영향
- **긍정적 영향**: 
  - 사용자가 업데이트 영향도를 예측 가능
  - CI/CD 자동 릴리스에 적합
- **부정적 영향**: 
  - MAJOR 버전 업 판단이 어려울 수 있음

### 초기 로드맵
- **0.1.0**: 기본 기능(AST 분석, 그래프 구축)
- **0.2.0**: MCP 통합(Tools, Resources)
- **0.3.0**: 고급 기능(커뮤니티 탐지, 변경 영향 분석)
- **1.0.0**: 안정판 릴리스

---

## ADR-010: 오류 분류와 복구 전략

### 상태
**승인됨** (2024-01)

### 컨텍스트
에러 핸들링 방침을 정의할 필요가 있습니다.

### 결정
에러를 아래 카테고리로 분류하고, 각각에 대응하는 복구 전략을 정의합니다.

```python
class CodeGraphError(Exception):
    """기본 예외 클래스"""
    pass

class ParseError(CodeGraphError):
    """AST 분석 에러 - 복구 가능"""
    pass

class StorageError(CodeGraphError):
    """스토리지 에러 - 재시도 가능"""
    pass

class ConfigurationError(CodeGraphError):
    """설정 에러 - 복구 불가"""
    pass
```

### 오류 분류와 전략

| 카테고리   | 예시    | 복구 전략               |
| ------ | ----- | ------------------- |
| 복구 가능  | 구문 에러 | 부분 파싱, 로그 기록, 계속 진행 |
| 재시도 가능 | DB 락  | 지수 백오프로 재시도         |
| 복구 불가  | 설정 오류 | 즉시 실패, 명확한 에러 메시지   |

### 근거
1. **그레이스풀 디그레이데이션(Graceful Degradation)**: 一部の失敗でシステム全体が停止しない
2. **디버깅 용이성**: 에러 유형에 따른 대응이 명확
3. **사용자 경험**: 적절한 에러 메시지로 다음 액션을 유도

### 영향
- **긍정적 영향**: 
  - 시스템 견고성 향상
  - 디버깅 시간 단축
- **부정적 영향**: 
  - 에러 핸들링 코드 증가

### 관련 요구사항
- REQ-NFR-006 (오류 내성)

---

## 결정 요약

| ADR     | 결정 내용              | 상태  |
| ------- | ------------------ | --- |
| ADR-001 | Library-First 아키텍처 | 승인됨 |
| ADR-002 | SQLite 채택          | 승인됨 |
| ADR-003 | Tree-sitter AST 분석 | 승인됨 |
| ADR-004 | MCP SDK (Python)   | 승인됨 |
| ADR-005 | NetworkX 그래프 연산    | 승인됨 |
| ADR-006 | Pydantic 데이터 모델    | 승인됨 |
| ADR-007 | asyncio 비동기 I/O    | 승인됨 |
| ADR-008 | LRU 캐시 전략          | 승인됨 |
| ADR-009 | 시맨틱 버저닝            | 승인됨 |
| ADR-010 | 오류 분류와 복구 전략       | 승인됨 |

---

## 변경 이력

| 날짜         | 버전    | 변경 내용 |
| ---------- | ----- | ----- |
| 2024-01-XX | 1.0.0 | 초판 작성 |
