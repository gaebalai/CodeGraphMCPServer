# CodeGraphMCPServer 문서

CodeGraphMCPServer의 기술 문서입니다.

## 문서 목록

| 문서 | 설명 |
|-------------|------|
| [API 레퍼런스](./api.md) | MCP Tools, Resources, Prompts의 상세 사양 |
| [설정 가이드](./configuration.md) | 환경 변수, 설정 파일, 클라이언트 설정 |
| [사용 예제](./examples.md) | CLI, Python, MCP 클라이언트에서의 사용 예 |

## 퀵 링크

### 입문

- [README](../README.md) - 프로젝트 개요 및 퀵 스타트
- [설치](../README.md#설치)
- [퀵 스타트](../README.md#퀵스타트)

### API

- [MCP Tools (14종)](./api.md#mcp-tools-14종)
- [MCP Resources (4종)](./api.md#mcp-resources-4종)
- [MCP Prompts (6종)](./api.md#mcp-prompts-6종)

### 설정

- [환경 변수](./configuration.md#환경변수)
- [설정 파일 (codegraph.toml)](./configuration.md#설정파일)
- [MCP 클라이언트 설정](./configuration.md#mcp클라이언트설정)
- [LLM 설정](./configuration.md#llm설정)

### 사용 예제

- [CLI 사용 예제](./examples.md#cli사용예제)
- [AI 어시스턴트 연동](./examples.md#ai어시스턴트연동)
- [Python에서 사용](./examples.md#python에서사용)

## 샘플 코드

[`examples/`](../examples/) 디렉터리에 샘플 코드가 있습니다:

- `basic_usage.py` - 코어 API의 기본 사용 방법
- `mcp_client.py` - MCP 클라이언트 연결 예제

## 지원 플랫폼

| 클라이언트 | 지원 상태 |
|-------------|-------------|
| Claude Desktop | ✅ 완전 지원 |
| VS Code (GitHub Copilot) | ✅ 완전 지원 |
| Cursor | ✅ 완전 지원 |
| Windsurf | ✅ 완전 지원 |

## 지원 언어

| 언어 | AST 분석 | 비고 |
|-----|--------|------|
| Python | ✅ | Tree-sitter |
| TypeScript | ✅ | Tree-sitter |
| JavaScript | ✅ | Tree-sitter |
| Rust | ✅ | Tree-sitter |

## 버전 정보

- CodeGraphMCPServer: 0.1.0
- MCP Protocol: 2024-11-05
- Python: 3.11+
