# CodeGraphMCPServer

**제로 설정으로 실행 가능한 경량·고속 소스 코드 분석 MCP 서버**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)
[![Tests](https://img.shields.io/badge/tests-334%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-64%25-yellow.svg)]()

## 개요

CodeGraphMCPServer는 코드베이스의 구조를 이해하고 GraphRAG(Graph Retrieval-Augmented Generation) 기능을 제공하는 MCP 서버이다.  
외부 데이터베이스가 필요 없는 자체 완결형 아키텍처로, MCP를 지원하는 AI 도구(GitHub Copilot, Claude Desktop, Cursor 등)에서 코드베이스에 대한 구조적 이해와 효율적인 코드 보완을 가능하게 한다.

### 🧠 GraphRAG 기능

- **커뮤니티 탐지**: Louvain 알고리즘을 이용한 코드 모듈 자동 클러스터링
- **LLM 통합**: OpenAI / Anthropic / 로컬 LLM을 지원하는 멀티 프로바이더 구조
- **글로벌 검색**: 커뮤니티 요약을 활용한 코드베이스 전체 이해
- **로컬 검색**: 엔티티 인접 영역의 컨텍스트 탐색

### ✨ 주요 특징

| 특징 | 설명 |
|------|------|
| 🚀 **제로 설정 실행** | 외부 DB 불필요, `pip install && serve` 만으로 즉시 사용 가능 |
| 🌳 **AST 분석** | Tree-sitter 기반의 고속·정확한 코드 분석 |
| 🔗 **그래프 구성** | 코드 엔티티 간 관계를 그래프로 모델링 |
| 🔍 **14개 MCP 도구** | 의존성 분석, 호출 추적, 코드 검색 |
| 📚 **4개 MCP 리소스** | 엔티티, 파일, 커뮤니티, 통계 정보 |
| 💬 **6개 MCP 프롬프트** | 코드 리뷰, 기능 구현, 디버깅 지원 |
| ⚡ **고속 인덱싱** | 10만 라인 기준 30초 이내, 증분 업데이트 2초 이내 |
| 🌐 **다국어 지원** | Python, TypeScript, JavaScript, Rust, Go, Java, PHP, C#, C, C++, HCL, Ruby, Kotlin, Swift, Scala, Lua (총 16개 언어) |

## 실행 환경 요구사항

- Python 3.11 이상
- MCP 지원 클라이언트 (GitHub Copilot, Claude Desktop, Cursor, Windsurf)

## 설치

### pip로 설치

```bash
pip install codegraph-mcp
```

### 소스 코드로 설치(개발용)

```bash
git clone https://github.com/gaebalai/CodeGraphMCPServer.git
cd CodeGraphMCPServer
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -e ".[dev]"
```

## 빠른 시작

### 1. 리포지토리 인덱싱

```bash
# 전체 인덱싱
codegraph-mcp index /path/to/repository --full

# 증분 인덱싱 (기본값)
codegraph-mcp index /path/to/repository

# 파일 감시를 통한 자동 재인덱싱 (v0.7.0 신규)
codegraph-mcp watch /path/to/repository
codegraph-mcp watch /path/to/repository --debounce 2.0  
codegraph-mcp watch /path/to/repository --community     
```

**출력 예시:**
```
Indexed 16 entities, 37 relations in 0.81s
```

### 2. 통계 정보 확인

```bash
codegraph-mcp stats /path/to/repository
```

**코드 검색:**
```
Repository Statistics
=====================
Repository: /path/to/repository

Entities: 16
Relations: 37
Communities: 0
Files: 1

Entities by type:
  - class: 2
  - function: 2
  - method: 11
  - module: 1
```

### 3. 코드 검색

```bash
codegraph-mcp query "Calculator" --repo /path/to/repository
```

### 4. MCP 서버로 실행

```bash
# stdio 트랜스포트 (기본값)
codegraph-mcp serve --repo /path/to/repository

# SSE 트랜스포트
codegraph-mcp serve --repo /path/to/repository --transport sse --port 8080
```

## MCP 클라이언트 설정

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

## 🛠 MCP 도구 (14종)

### 그래프 쿼리 도구

| 도구                         | 설명               | 주요 인자                  |
| -------------------------- | ---------------- | ---------------------- |
| `query_codebase`           | 자연어 기반 코드 그래프 검색 | `query`, `max_results` |
| `find_dependencies`        | 엔티티 의존성 검색       | `entity_id`, `depth`   |
| `find_callers`             | 호출자 검색           | `entity_id`            |
| `find_callees`             | 호출 대상 검색         | `entity_id`            |
| `find_implementations`     | 인터페이스 구현체 검색     | `entity_id`            |
| `analyze_module_structure` | 모듈 구조 분석         | `file_path`            |

### 코드 조회 도구

| 도구                   | 설명           | 주요 인자                                 |
| -------------------- | ------------ | ------------------------------------- |
| `get_code_snippet`   | 엔티티 소스 코드 조회 | `entity_id`, `include_context`        |
| `read_file_content`  | 파일 내용 조회     | `file_path`, `start_line`, `end_line` |
| `get_file_structure` | 파일 구조 요약     | `file_path`                           |

### GraphRAG 도구

| 도구              | 설명             | 주요 인자                |
| --------------- | -------------- | -------------------- |
| `global_search` | 커뮤니티 기반 글로벌 검색 | `query`              |
| `local_search`  | 엔티티 인접 로컬 검색   | `query`, `entity_id` |

### 관리 도구

| 도구                      | 설명         | 주요 인자                |
| ----------------------- | ---------- | -------------------- |
| `suggest_refactoring`   | 리팩터링 제안    | `entity_id`, `type`  |
| `reindex_repository`    | 리포지토리 재인덱싱 | `incremental`        |
| `execute_shell_command` | 셸 명령 실행    | `command`, `timeout` |

## MCP 리소스 (4종)

| URI 패턴                         | 설명          |
| ------------------------------ | ----------- |
| `codegraph://entities/{id}`    | 엔티티 상세 정보   |
| `codegraph://files/{path}`     | 파일 내 엔티티 목록 |
| `codegraph://communities/{id}` | 커뮤니티 정보     |
| `codegraph://stats`            | 그래프 통계      |

## MCP 프롬프트 (6종)

| 프롬프트                | 설명        | 인자                                   |
| ------------------- | --------- | ------------------------------------ |
| `code_review`       | 코드 리뷰 수행  | `entity_id`, `focus_areas`           |
| `explain_codebase`  | 코드베이스 설명  | `scope`, `detail_level`              |
| `implement_feature` | 기능 구현 가이드 | `feature_description`, `constraints` |
| `debug_issue`       | 디버깅 지원    | `issue_description`, `context`       |
| `refactor_guidance` | 리팩터링 가이드  | `entity_id`, `goal`                  |
| `test_generation`   | 테스트 생성    | `entity_id`, `test_type`             |

## 사용 예시

### AI 어시스턴트와의 대화 예시

```
You: UserService 클래스의 의존 관계를 알려줘

AI: [find_dependencies 도구 사용]
    UserService는 다음에 의존합니다:
    - DatabaseConnection (database.py)
    - Logger (utils/logging.py)
    - UserRepository (repositories/user.py)
```

```
You: authenticate 메서드를 변경하면 영향 범위가 어떻게 돼?

AI: [find_callers 도구 사용]
    authenticate 호출자 목록:
    - LoginController.login() (controllers/auth.py:45)
    - APIMiddleware.verify_token() (middleware/api.py:23)
    - TestUserService.test_auth() (tests/test_user.py:78)
```

```
You: 이 프로젝트의 주요 컴포넌트를 설명해줘

AI: [global_search 도구 사용]
    [explain_codebase 프롬프트 사용]
    
    이 프로젝트는 3계층 아키텍처로 구성되어 있습니다:
    1. Controllers계층: HTTP 요청 처리
    2. Services계층: 비즈니스 로직
    3. Repositories계층: 데이터 접근
```

## 개발

### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함 실행
pytest --cov=src/codegraph_mcp --cov-report=html

# 특정 테스트 실행
pytest tests/unit/test_parser.py -v
```

### 린트 & 포맷

```bash
# Ruff로 린트 검사
ruff check src tests

# Ruff로 코드 포맷
ruff format src tests

# MyPy로 타입 체크
mypy src
```

## 아키텍처

```
src/codegraph_mcp/
├── __init__.py          # 패키지 초기화
├── __main__.py          # CLI 엔트리 포인트
├── server.py            # MCP 서버
├── config.py            # 설정 관리
├── core/                # 코어 로직
│   ├── parser.py        # Tree-sitter AST 파서
│   ├── graph.py         # NetworkX 그래프 엔진
│   ├── indexer.py       # 리포지토리 인덱서
│   ├── community.py     # 커뮤니티 탐지 (Louvain)
│   ├── semantic.py      # 시맨틱 분석
│   ├── llm.py           # LLM 통합 (OpenAI / Anthropic / Local)
│   └── graphrag.py      # GraphRAG 검색 엔진
├── storage/             # 스토리지 계층
│   ├── sqlite.py        # SQLite 영속화
│   ├── cache.py         # 파일 캐시
│   └── vectors.py       # 벡터 스토어
├── mcp/                 # MCP 인터페이스
│   ├── tools.py         # 14개 MCP 도구
│   ├── resources.py     # 4개 MCP 리소스
│   └── prompts.py       # 6개 MCP 프롬프트
└── languages/           # 언어 지원 (11개 언어)
    ├── python.py        # Python 추출기
    ├── typescript.py    # TypeScript 추출기
    ├── javascript.py    # JavaScript 추출기
    ├── rust.py          # Rust 추출기
    ├── go.py            # Go 추출기
    ├── java.py          # Java 추출기
    ├── php.py           # PHP 추출기
    ├── csharp.py        # C# 추출기
    ├── cpp.py           # C++ 추출기
    ├── hcl.py           # HCL(Terraform) 추출기
    └── ruby.py          # Ruby 추출기
```

## 성능

### 실측 수치 (v0.3.0)

| 메트릭      | 실측 값          | 비고                    |
| -------- | ------------- | --------------------- |
| 인덱싱 속도   | **초당 32 엔티티** | 67개 파일, 941개 엔티티      |
| 파일 처리 속도 | **파일당 0.44초** | Python / TS / Rust 혼합 |
| 증분 인덱싱   | **2초 미만**     | 변경된 파일만 처리            |
| 쿼리 응답 시간 | **2ms 미만**    | 그래프 검색                |

### 목표 수치

| 메트릭             | 목표 값     |
| --------------- | -------- |
| 초기 인덱싱 (10만 라인) | 30초 미만   |
| 증분 인덱싱          | 2초 미만    |
| 쿼리 응답 시간        | 500ms 미만 |
| 기동 시간           | 2초 미만    |
| 메모리 사용량         | 500MB 미만 |

## 라이선스

MIT License - [LICENSE](LICENSE) 참고

## 참고

- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP사양
- [Tree-sitter](https://tree-sitter.github.io/) - AST 분석
- [NetworkX](https://networkx.org/) - 그래프 알고리즘
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag) - GraphRAG 개념

## 관련 링크

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
