# CodeGraphMCPServer 사용 예제

이 문서에서는 CodeGraphMCPServer의 실전적인 사용 예제를 소개합니다.

## 목차

- [퀵 스타트](#퀵-스타트)
- [CLI 사용 예제](#cli-사용-예제)
- [AI 어시스턴트 연동 예제](#ai-어시스턴트-연동-예제)
- [Python에서 사용](#python에서-사용)
- [MCP 클라이언트에서 사용](#mcp-클라이언트에서-사용)
- [실전 유스케이스](#실전-유스케이스)

---

## 퀵 스타트

### 1. 설치

```bash
pip install codegraph-mcp
```

### 2. 리포지토리 인덱싱

```bash
codegraph-mcp index /path/to/your/project --full
```

### 3. MCP 서버 기동

```bash
codegraph-mcp serve --repo /path/to/your/project
```

### 4. Claude Desktop 또는 VS Code에서 연결

설정 파일에 아래를 추가:

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "/path/to/your/project"]
    }
  }
}
```

---

## CLI 사용 예제

### 인덱스 생성

```bash
# 전체 인덱스
codegraph-mcp index /path/to/project --full

# 증분 인덱스(변경 파일만)
codegraph-mcp index /path/to/project

# 언어 지정
codegraph-mcp index /path/to/project --languages python,typescript
```

**출력 예:**
```
Indexing /path/to/project...
Processing: src/services/auth.py
Processing: src/services/user.py
Processing: src/models/user.py
...

Indexed 256 entities, 512 relations in 2.35s
```

### 통계 정보 확인

```bash
codegraph-mcp stats /path/to/project
```

**출력 예:**
```
Repository Statistics
=====================
Repository: /path/to/project

Entities: 256
Relations: 512
Communities: 8
Files: 45

Entities by type:
  - class: 45
  - function: 120
  - method: 85
  - module: 6

Relations by type:
  - calls: 280
  - contains: 150
  - imports: 52
  - implements: 30
```

### 코드 검색

```bash
# 자연어 검색
codegraph-mcp query "인증 처리" --repo /path/to/project

# 엔티티명으로 검색
codegraph-mcp query "UserService" --repo /path/to/project --max-results 5
```

**출력 예:**
```
Search Results for "UserService"
================================

1. class UserService (src/services/user.py:10-150)
   Service for managing user operations

2. method UserService.create_user (src/services/user.py:25-45)
   Create a new user account

3. method UserService.update_user (src/services/user.py:47-70)
   Update existing user information
```

### 서버 기동

```bash
# stdio 트랜스포트(기본값)
codegraph-mcp serve --repo /path/to/project

# SSE 트랜스포트(HTTP 기반)
codegraph-mcp serve --repo /path/to/project --transport sse --port 8080

# 디버그 모드
CODEGRAPH_LOG_LEVEL=DEBUG codegraph-mcp serve --repo /path/to/project
```

---

## AI 어시스턴트 연동 예제

### 의존 관계 조사

**사용자:**
> UserService 클래스의 의존 관계를 알려줘

**AI(find_dependencies 도구 사용):**
> UserService는 아래 클래스/모듈에 의존합니다:
> 
> 1. **DatabaseConnection** (src/database/connection.py)
>    - 데이터베이스 연결 관리
> 2. **UserRepository** (src/repositories/user.py)
>    - 사용자 데이터 CRUD 작업
> 3. **Logger** (src/utils/logging.py)
>    - 로그 출력
> 4. **PasswordHasher** (src/auth/password.py)
>    - 비밀번호 해시 처리

### 영향 범위 분석

**사용자:**
> authenticate메서드를 변경하면 영향 범위가 어떻게 돼?

**AI(find_callers 도구 사용):**
> `authenticate`메서드는 아래에서 호출됩니다:
> 
> | 호출자 | 파일 | 행 번호 |
> |-----------|---------|--------|
> | `LoginController.login` | controllers/auth.py | 45 |
> | `APIMiddleware.verify_token` | middleware/api.py | 23 |
> | `TestAuth.test_authenticate` | tests/test_auth.py | 78 |
> 
> 변경 시 위 3곳에 대한 영향을 확인해 주세요.

### 코드베이스 이해

**사용자:**
> 이 프로젝트의 주요 컴포넌트를 설명해 줘

**AI（global_search + explain_codebase프롬프트 사용）:**
> 이 프로젝트는 3계층 아키텍처로 구성되어 있습니다:
> 
> ## 1. Controllers계층
> HTTP 요청 처리를 담당
> - `AuthController`: 인증 관련 엔드포인트
> - `UserController`: 사용자 관리 엔드포인트
> - `APIController`: API 공통 처리
> 
> ## 2. Services계층
> 비즈니스 로직 구현
> - `AuthService`: 인증·인가 처리
> - `UserService`: 사용자 관리 처리
> - `NotificationService`: 알림 처리
> 
> ## 3. Repositories계층
> 데이터 접근을 추상화
> - `UserRepository`: 사용자 데이터 접근
> - `TokenRepository`: 토큰 관리

### 코드 리뷰

**사용자:**
> process_payment메서드를 리뷰해 줘

**AI(code_review 프롬프트 사용):**
> ## 코드 리뷰: `process_payment`
> 
> ### 보안
> ⚠️ **문제**: 카드 정보가 로그로 출력될 가능성
> ```python
> logger.info(f"Processing payment: {card_data}")  # 35행
> ```
> **권장**: 민감 데이터는 마스킹 처리
> 
> ### 성능
> ⚠️ **문제**: 동기 DB 호출이 여러 번 발생
> **권장**: 배치 처리 또는 async화 검토
> 
> ### 코드 품질
> ✅ 에러 핸들링은 적절
> ✅ 함수 책임은 명확
> ⚠️ 함수가 김(85행) → 추출을 검토

### 기능 구현 가이던스

**사용자:**
> 2단계 인증 기능을 추가하고 싶어

**AI(implement_feature 프롬프트 사용):**
> ## 2단계 인증 구현 가이드
> 
> ### 1. 변경이 필요한 파일
> - `src/services/auth.py` - 인증 로직 확장
> - `src/models/user.py` - 2FA 설정 추가
> - `src/controllers/auth.py` - 신규 엔드포인트
> 
> ### 2. 신규로 생성할 파일
> - `src/services/totp.py` - TOTP 생성/검증
> - `src/models/totp_secret.py` - 시크릿 관리
> 
> ### 3. 구현 절차
> 1. `User`모델에 `totp_enabled`와 `totp_secret`추가
> 2. `TOTPService`클래스 생성
> 3. `AuthService.authenticate`확장
> 4. 신규 엔드포인트 추가

---

## Python에서 사용

### 기본 사용 예제

```python
import asyncio
from pathlib import Path
from codegraph_mcp.core.parser import ASTParser
from codegraph_mcp.core.graph import GraphEngine, GraphQuery
from codegraph_mcp.core.indexer import Indexer

async def main():
    repo_path = Path("/path/to/project")
    
    # 1. 리포지토리 인덱싱
    indexer = Indexer()
    result = await indexer.index_repository(repo_path)
    print(f"Indexed {result.entities_count} entities")
    
    # 2. 그래프 엔진 초기화
    engine = GraphEngine(repo_path)
    await engine.initialize()
    
    try:
        # 3. 엔티티 검색
        query = GraphQuery(query="UserService", max_results=10)
        result = await engine.query(query)
        
        for entity in result.entities:
            print(f"{entity.name} ({entity.type.value})")
        
        # 4. 의존 관계 분석
        if result.entities:
            deps = await engine.find_dependencies(result.entities[0].id)
            print(f"\nDependencies: {len(deps.entities)}")
            
        # 5. 통계 가져오기
        stats = await engine.get_statistics()
        print(f"\nTotal entities: {stats.entity_count}")
        
    finally:
        await engine.close()

asyncio.run(main())
```

### 파서를 직접 사용

```python
from codegraph_mcp.core.parser import ASTParser

# 코드 분석
parser = ASTParser()
code = '''
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        return a * b
'''

entities, relations = parser.parse_code(
    code=code,
    language="python",
    file_path="calculator.py"
)

print(f"Found {len(entities)} entities:")
for entity in entities:
    print(f"  - {entity.name} ({entity.type.value})")

print(f"\nFound {len(relations)} relations:")
for rel in relations:
    print(f"  - {rel.source_id} --[{rel.type.value}]--> {rel.target_id}")
```

### GraphRAG 검색

```python
import asyncio
from pathlib import Path
from codegraph_mcp.core.graph import GraphEngine
from codegraph_mcp.core.graphrag import GraphRAGSearch

async def graphrag_example():
    repo_path = Path("/path/to/project")
    
    engine = GraphEngine(repo_path)
    await engine.initialize()
    
    try:
        # GraphRAG 검색 초기화
        search = GraphRAGSearch(engine, use_llm=True)
        
        # 글로벌 검색
        result = await search.global_search(
            query="이 프로젝트의 인증 플로우를 설명해 줘"
        )
        
        print(f"Answer: {result.answer}")
        print(f"Confidence: {result.confidence}")
        print(f"Communities searched: {result.communities_searched}")
        
        # 로컬 검색
        result = await search.local_search(
            query="이 클래스 사용법은?",
            entity_id="user_service"
        )
        
        print(f"\nLocal search answer: {result.answer}")
        
    finally:
        await engine.close()

asyncio.run(graphrag_example())
```

---

## MCP 클라이언트에서 사용

### MCP SDK를 사용한 연결

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def mcp_client_example():
    # 서버 파라미터 설정
    server_params = StdioServerParameters(
        command="codegraph-mcp",
        args=["serve", "--repo", "/path/to/project"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 도구 목록 가져오기
            tools = await session.list_tools()
            print(f"Available tools: {len(tools.tools)}")
            
            # 도구 호출
            result = await session.call_tool(
                "query_codebase",
                arguments={"query": "UserService", "max_results": 5}
            )
            print(f"Result: {result.content[0].text}")
            
            # 리소스 읽기
            stats = await session.read_resource("codegraph://stats")
            print(f"Stats: {stats.contents[0].text}")
            
            # 프롬프트 가져오기
            prompt = await session.get_prompt(
                "code_review",
                arguments={"entity_id": "user_service"}
            )
            print(f"Prompt: {prompt.messages[0].content.text[:200]}...")

asyncio.run(mcp_client_example())
```

---

## 실전 유스케이스

### 1. 레거시 코드 이해

대규모 레거시 프로젝트를 인수인계받은 경우:

```
# 1. 인덱스 생성
codegraph-mcp index ./legacy-project --full

# 2. 통계로 전체 그림 파악
codegraph-mcp stats ./legacy-project

# 3. AI 어시스턴트에 질문
"이 프로젝트의 주요 컴포넌트를 설명해 줘"
"데이터베이스와의 상호작용은 어디서 이뤄져?"
"인증 플로우를 추적해 줘"
```

### 2. 리팩터링 영향 분석

메서드를 변경하기 전에 영향 범위를 확인:

```
"processOrder 메서드의 호출자를 전부 알려줘"
"이 메서드가 의존하는 클래스는 뭐야?"
"변경하면 영향받는 테스트는 뭐야?"
```

### 3. 신규 기능 구현 계획

신규 기능을 추가할 때 가이던스:

```
"알림 기능을 추가하고 싶어. 기존 코드랑 어떻게 통합해야 해?"
"비슷한 기능이 이미 구현돼 있는지 찾아줘"
"이 기능을 구현하기에 최적의 위치는 어디야?"
```

### 4. 코드 리뷰 지원

Pull Request 리뷰 시:

```
"AuthService 클래스를 보안 관점에서 리뷰해 줘"
"이 PR에서 변경된 파일의 영향 범위는?"
"새로 추가된 메서드 테스트 케이스를 제안해 줘"
```

### 5. 온보딩

신규 팀원 교육:

```
"프로젝트 아키텍처를 설명해 줘"
"개발 시작하려면 어떤 파일부터 보면 돼?"
"테스트 실행 방법과 구조를 설명해 줘"
```

---

## 샘플 스크립트

프로젝트의 `examples/` 디렉터리에 아래 샘플이 있습니다:

- `basic_usage.py` - 기본 사용 예제
- `mcp_client.py` - MCP 클라이언트 연결 예제

실행 방법:

```bash
cd /path/to/CodeGraphMCPServer
source .venv/bin/activate
python examples/basic_usage.py
```

---

## 관련 문서

- [API 레퍼런스](./api.md)
- [사용예제](./examples.md)
- [README](../README.md)
