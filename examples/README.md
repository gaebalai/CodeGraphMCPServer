# Examples

CodeGraphMCPServer의 사용 예제를 보관하는 디렉터리입니다.

## 파일 목록

| 파일 | 설명 |
|----------|------|
| `basic_usage.py` | CLI 및 코어 API의 기본적인 사용 방법 |
| `mcp_client.py` | MCP 클라이언트에서의 사용 예제 |

## 실행 방법

### 사전 준비

```bash
# 리포지토리 루트 디렉터리에서 실행
cd /path/to/CodeGraphMCPServer

# 가상 환경 활성화
source .venv/bin/activate

# 개발용 설치
pip install -e ".[dev]"
```

### basic_usage.py

코어 API를 직접 사용하는 예제:

```bash
python examples/basic_usage.py
```

**기능:**
- 리포지토리 인덱스 생성
- 엔티티 검색
- 의존 관계 분석
- 통계 정보 조회

### mcp_client.py

MCP 프로토콜을 통해 서버에 연결하는 예제:

```bash
# 먼저 서버를 기동 (별도 터미널)
codegraph-mcp serve --repo /path/to/project

# 클라이언트 실행
python examples/mcp_client.py
```

**기능:**
- MCP 서버 연결
- 도구 호출
- 리소스 읽기
- 프롬프트 조회

## CLI 사용 예제

### 인덱스 생성

```bash
# 전체 인덱스
codegraph-mcp index /path/to/repository --full

# 증분 인덱스
codegraph-mcp index /path/to/repository
```

### 통계 정보 조회

```bash
codegraph-mcp stats /path/to/repository
```

### 코드 검색

```bash
# 이름으로 검색
codegraph-mcp query "UserService" --repo /path/to/repository

# 타입으로 검색
codegraph-mcp query "class" --repo /path/to/repository --type class
```

### MCP 서버 기동

```bash
# stdio 트랜스포트 (기본값)
codegraph-mcp serve --repo /path/to/repository

# SSE 트랜스포트
codegraph-mcp serve --repo /path/to/repository --transport sse --port 8080
```

## MCP 클라이언트 설정 예제

### Claude Desktop

`~/.config/claude/claude_desktop_config.json`:

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

### VS Code (GitHub Copilot)

`.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "${workspaceFolder}"]
    }
  }
}
```

### Cursor

`~/.cursor/mcp.json`:

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

## AI 어시스턴트와의 대화 예시

### 의존 관계 분석

```
You: Calculator 클래스의 의존 관계를 알려줘

AI: [find_dependencies 도구 사용]
    Calculator는 다음에 의존합니다:
    - math 모듈
    - Validator 클래스
```

### 호출자 검색

```
You: add 메서드를 변경하면 영향 범위가 어떻게 돼?

AI: [find_callers 도구 사용]
    add의 호출자:
    - Calculator.sum_all() (calculator.py:25)
    - test_calculator.test_add() (test_calculator.py:10)
```

### 코드베이스 설명

```
You: 이 프로젝트의 구조를 설명해 줘

AI: [explain_codebase 프롬프트 사용]

    이 프로젝트는 다음과 같은 구조로 구성되어 있습니다:
    1. core/ - 핵심 로직
    2. mcp/ - MCP 인터페이스
    3. storage/ - 데이터 영속화
```
