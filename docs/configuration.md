# CodeGraphMCPServer 설정 가이드

이 문서에서는 CodeGraphMCPServer의 설정 방법과 각 MCP 클라이언트에서의 구성 예제를 설명합니다.

## 목차

- [환경 변수](#환경-변수)
- [설정 파일](#설정-파일)
- [MCP 클라이언트 설정](#mcp-클라이언트-설정)
  - [Claude Desktop](#claude-desktop)
  - [VS Code (GitHub Copilot)](#vs-code-github-copilot)
  - [Cursor](#cursor)
  - [Windsurf](#windsurf)
- [트랜스포트 설정](#트랜스포트-설정)
- [LLM 설정](#llm-설정)
- [성능 튜닝](#성능-튜닝)

---

## 환경 변수

CodeGraphMCPServer는 아래 환경 변수를 지원합니다:

### 기본 설정

| 변수명 | 기본값 | 설명 |
|--------|-----------|------|
| `CODEGRAPH_REPO_PATH` | 현재 디렉터리 | 분석 대상 리포지토리 경로 |
| `CODEGRAPH_DB_PATH` | `~/.codegraph/db` | 데이터베이스 저장 위치 |
| `CODEGRAPH_LOG_LEVEL` | `INFO` | 로그 레벨 (DEBUG, INFO, WARNING, ERROR) |

### LLM 설정

| 변수명 | 기본값 | 설명 |
|--------|-----------|------|
| `OPENAI_API_KEY` | 없음 | OpenAI API 키 |
| `ANTHROPIC_API_KEY` | 없음 | Anthropic API 키 |
| `CODEGRAPH_LLM_PROVIDER` | `rule_based` | LLM 제공자(openai, anthropic, local, rule_based) |
| `CODEGRAPH_LLM_MODEL` | 제공자 의존 | 사용할 모델명 |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API 엔드포인트 |

### 캐시 설정

| 변수명 | 기본값 | 설명 |
|--------|-----------|------|
| `CODEGRAPH_CACHE_DIR` | `~/.codegraph/cache` | 캐시 디렉터리 |
| `CODEGRAPH_CACHE_TTL` | `3600` | 캐시 유효기간(초) |

### 인덱스 설정

| 변수명 | 기본값 | 설명 |
|--------|-----------|------|
| `CODEGRAPH_LANGUAGES` | `python,typescript,javascript,rust` | 대상 언어(콤마 구분) |
| `CODEGRAPH_EXCLUDE_PATTERNS` | `node_modules,__pycache__,.git` | 제외 패턴 |

---

## 설정 파일

### `codegraph.toml`

프로젝트 루트에 `codegraph.toml`을 배치하면, 프로젝트 고유 설정이 가능합니다:

```toml
[codegraph]
# 기본 설정
repo_path = "."
db_path = ".codegraph/db"
log_level = "INFO"

[index]
# 인덱스 설정
languages = ["python", "typescript", "rust"]
exclude_patterns = [
    "node_modules",
    "__pycache__",
    ".git",
    ".venv",
    "dist",
    "build",
]
max_file_size = 1048576  # 1MB

[semantic]
# 시맨틱 분석 설정
llm_enabled = true
llm_provider = "openai"
llm_model = "gpt-4o-mini"
embedding_model = "text-embedding-3-small"

[community]
# 커뮤니티 탐지 설정
algorithm = "louvain"
resolution = 1.0
min_community_size = 3

[cache]
# 캐시 설정
enabled = true
ttl = 3600
max_size = 104857600  # 100MB

[performance]
# 성능 설정
max_workers = 4
batch_size = 100
timeout = 300
```

---

## MCP 클라이언트 설정

### Claude Desktop

#### macOS

설정 파일: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "/path/to/your/project"],
      "env": {
        "CODEGRAPH_LOG_LEVEL": "INFO",
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### Windows

설정 파일: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "C:\\path\\to\\your\\project"],
      "env": {
        "CODEGRAPH_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Linux

설정 파일: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "/home/user/projects/my-project"],
      "env": {
        "CODEGRAPH_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### VS Code (GitHub Copilot)

#### 워크스페이스 설정

`.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "${workspaceFolder}"],
      "env": {
        "CODEGRAPH_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### 사용자 설정(글로벌)

VS Code설정:

```json
{
  "mcp.servers": {
    "codegraph-global": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "${workspaceFolder}"]
    }
  }
}
```

#### 복수 프로젝트 대응

```json
{
  "mcp.servers": {
    "codegraph-frontend": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "${workspaceFolder}/frontend"]
    },
    "codegraph-backend": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "${workspaceFolder}/backend"]
    }
  }
}
```

### Cursor

설정 파일: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "/path/to/your/project"],
      "env": {
        "CODEGRAPH_LOG_LEVEL": "INFO",
        "CODEGRAPH_LLM_PROVIDER": "openai"
      }
    }
  }
}
```

### Windsurf

설정 파일: `~/.windsurf/mcp.json`

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

## 트랜스포트 설정

### stdio(기본값)

표준 입출력을 사용하는 트랜스포트. 대부분의 MCP 클라이언트에서 사용됩니다.

```bash
codegraph-mcp serve --repo /path/to/project --transport stdio
```

클라이언트 설정:

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "/path/to/project"]
    }
  }
}
```

### SSE (Server-Sent Events)

HTTP 기반 트랜스포트. 원격 서버 또는 디버깅에 유용합니다.

```bash
codegraph-mcp serve --repo /path/to/project --transport sse --port 8080
```

#### SSE 클라이언트 설정 예

```json
{
  "mcpServers": {
    "codegraph": {
      "type": "sse",
      "url": "http://localhost:8080/sse"
    }
  }
}
```

#### Docker + SSE

```yaml
# docker-compose.yml
version: '3.8'
services:
  codegraph:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - /path/to/project:/repo:ro
    command: ["serve", "--repo", "/repo", "--transport", "sse", "--port", "8080"]
```

---

## LLM설정

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
export CODEGRAPH_LLM_PROVIDER="openai"
export CODEGRAPH_LLM_MODEL="gpt-4o-mini"
```

또는 `codegraph.toml`:

```toml
[semantic]
llm_enabled = true
llm_provider = "openai"
llm_model = "gpt-4o-mini"
```

### Anthropic

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export CODEGRAPH_LLM_PROVIDER="anthropic"
export CODEGRAPH_LLM_MODEL="claude-3-haiku-20240307"
```

또는 `codegraph.toml`:

```toml
[semantic]
llm_enabled = true
llm_provider = "anthropic"
llm_model = "claude-3-haiku-20240307"
```

### 로컬 LLM (Ollama)

```bash
# Ollama 기동
ollama serve

# 모델 다운로드
ollama pull llama3.2

# 환경 변수 설정
export CODEGRAPH_LLM_PROVIDER="local"
export CODEGRAPH_LLM_MODEL="llama3.2"
export OLLAMA_BASE_URL="http://localhost:11434"
```

또는 `codegraph.toml`:

```toml
[semantic]
llm_enabled = true
llm_provider = "local"
llm_model = "llama3.2"
ollama_url = "http://localhost:11434"
```

### 룰 기반(기본값)

LLM을 사용하지 않고, 룰 기반 분석을 수행합니다:

```toml
[semantic]
llm_enabled = false
llm_provider = "rule_based"
```

---

## 성능 튜닝

### 대규모 리포지토리용

```toml
[index]
# 큰 파일 스킵
max_file_size = 524288  # 512KB

# 병렬 처리 증가
[performance]
max_workers = 8
batch_size = 200

# 캐시 적극 활용
[cache]
enabled = true
max_size = 524288000  # 500MB
ttl = 86400  # 24時間
```

### 메모리 제한 환경용

```toml
[performance]
max_workers = 2
batch_size = 50

[cache]
enabled = true
max_size = 52428800  # 50MB

[index]
max_file_size = 262144  # 256KB
```

### 제외 패턴 최적화

```toml
[index]
exclude_patterns = [
    # 의존성
    "node_modules",
    ".venv",
    "vendor",
    
    # 빌드 산출물
    "dist",
    "build",
    "target",
    "__pycache__",
    "*.pyc",
    
    # 테스트 데이터
    "fixtures",
    "testdata",

    # 문서
    "docs/api",

    # 생성 파일
    "*.generated.*",
    "*.min.js",
    "*.bundle.js",
]
```

---

## 트러블슈팅

### 서버가 기동되지 않음

1. Python 버전 확인:
   ```bash
   python --version  # 3.11이상 필요
   ```

2. 설치 확인:
   ```bash
   pip show codegraph-mcp
   ```

3. 상세 로그 활성화:
   ```bash
   CODEGRAPH_LOG_LEVEL=DEBUG codegraph-mcp serve --repo .
   ```

### 인덱싱이 느림

1. 제외 패턴 확인
2. `max_file_size`조정
3. `max_workers`증가

### 메모리 사용량이 많음

1. `batch_size`감소
2. `max_workers`감소
3. `cache.max_size`감소

### LLM에러

1. API키 확인
2. 모델명 확인
3. 네트워크 연결 확인

---

## 관련 문서

- [API 레퍼런스](./api.md)
- [사용예제](./examples.md)
- [README](../README.md)
