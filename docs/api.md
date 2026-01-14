# CodeGraphMCPServer API 레퍼런스

이 문서에서는 CodeGraphMCPServer가 제공하는 MCP API(Tools, Resources, Prompts)의 상세를 설명합니다.

## 목차

- [개요](#개요)
- [MCP Tools (14종)](#mcp-tools-14종)
  - [그래프 쿼리 도구](#그래프-쿼리-도구)
  - [코드 조회 도구](#코드-조회-도구)
  - [GraphRAG 도구](#graphrag-도구)
  - [관리 도구](#관리-도구)
- [MCP Resources (4종)](#mcp-resources-4종)
- [MCP Prompts (6종)](#mcp-prompts-6종)
- [데이터 타입](#데이터-타입)

---

## 개요

CodeGraphMCPServer는 Model Context Protocol(MCP)을 통해 아래 API를 제공합니다:

| 카테고리 | 수량 | 설명 |
|---------|------|------|
| Tools | 14 | 코드 분석·검색·관리 기능 |
| Resources | 4 | 코드 그래프 데이터 접근 |
| Prompts | 6 | 정형적인 코드 분석 작업 템플릿 |

---

## MCP Tools (14종)

### 그래프 쿼리 도구

#### `query_codebase`

자연어로 코드 그래프를 검색합니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "자연어 쿼리"
    },
    "max_results": {
      "type": "integer",
      "description": "최대 결과 수",
      "default": 20
    }
  },
  "required": ["query"]
}
```

**사용 예:**

```json
{
  "name": "query_codebase",
  "arguments": {
    "query": "인증 처리를 수행하는 클래스",
    "max_results": 10
  }
}
```

**응답 예:**

```json
{
  "entities": [
    {
      "id": "auth_service",
      "name": "AuthService",
      "type": "class",
      "file_path": "src/services/auth.py",
      "start_line": 15,
      "relevance": 0.95
    }
  ],
  "total_count": 3
}
```

---

#### `find_dependencies`

지정한 엔티티의 의존 관계를 검색합니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "entity_id": {
      "type": "string",
      "description": "엔티티 ID"
    },
    "depth": {
      "type": "integer",
      "description": "의존 관계 탐색 깊이",
      "default": 2
    }
  },
  "required": ["entity_id"]
}
```

**사용 예:**

```json
{
  "name": "find_dependencies",
  "arguments": {
    "entity_id": "user_service",
    "depth": 3
  }
}
```

**응답 예:**

```json
{
  "entities": [
    {
      "id": "database_connection",
      "name": "DatabaseConnection",
      "type": "class",
      "depth": 1
    },
    {
      "id": "logger",
      "name": "Logger",
      "type": "class",
      "depth": 1
    }
  ],
  "total_dependencies": 5
}
```

---

#### `find_callers`

함수·메서드의 호출자(호출 원)를 검색합니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "entity_id": {
      "type": "string",
      "description": "함수/메서드 ID"
    }
  },
  "required": ["entity_id"]
}
```

**사용 예:**

```json
{
  "name": "find_callers",
  "arguments": {
    "entity_id": "authenticate"
  }
}
```

**응답 예:**

```json
{
  "callers": [
    {
      "id": "login_controller_login",
      "name": "login",
      "type": "method"
    },
    {
      "id": "api_middleware_verify",
      "name": "verify_token",
      "type": "method"
    }
  ]
}
```

---

#### `find_callees`

함수·메서드의 호출 대상(호출 선)을 검색합니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "entity_id": {
      "type": "string",
      "description": "함수/메서드 ID"
    }
  },
  "required": ["entity_id"]
}
```

**사용 예:**

```json
{
  "name": "find_callees",
  "arguments": {
    "entity_id": "process_request"
  }
}
```

**응답 예:**

```json
{
  "callees": [
    {
      "id": "validate_input",
      "name": "validate_input",
      "type": "function"
    },
    {
      "id": "save_to_db",
      "name": "save_to_db",
      "type": "method"
    }
  ]
}
```

---

#### `find_implementations`

인터페이스·추상 클래스의 구현체를 검색합니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "entity_id": {
      "type": "string",
      "description": "인터페이스/클래스 ID"
    }
  },
  "required": ["entity_id"]
}
```

**사용 예:**

```json
{
  "name": "find_implementations",
  "arguments": {
    "entity_id": "repository_interface"
  }
}
```

**응답 예:**

```json
{
  "implementations": [
    {
      "id": "user_repository",
      "name": "UserRepository",
      "type": "class"
    },
    {
      "id": "product_repository",
      "name": "ProductRepository",
      "type": "class"
    }
  ]
}
```

---

#### `analyze_module_structure`

모듈·파일의 구조를 분석합니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "파일 경로"
    }
  },
  "required": ["file_path"]
}
```

**사용 예:**

```json
{
  "name": "analyze_module_structure",
  "arguments": {
    "file_path": "src/services/user_service.py"
  }
}
```

**응답 예:**

```json
{
  "file": "src/services/user_service.py",
  "entities": [
    {
      "type": "class",
      "name": "UserService",
      "lines": "10-150"
    },
    {
      "type": "method",
      "name": "create_user",
      "lines": "25-45"
    },
    {
      "type": "method",
      "name": "update_user",
      "lines": "47-70"
    }
  ]
}
```

---

### 코드 조회 도구

#### `get_code_snippet`

엔티티의 소스 코드를 가져옵니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "entity_id": {
      "type": "string",
      "description": "엔티티 ID"
    },
    "include_context": {
      "type": "boolean",
      "description": "주변 컨텍스트 포함",
      "default": true
    }
  },
  "required": ["entity_id"]
}
```

**사용 예:**

```json
{
  "name": "get_code_snippet",
  "arguments": {
    "entity_id": "calculate_total",
    "include_context": true
  }
}
```

**응답 예:**

```json
{
  "entity_id": "calculate_total",
  "name": "calculate_total",
  "source": "def calculate_total(items: list[Item]) -> float:\n    \"\"\"Calculate the total price of items.\"\"\"\n    return sum(item.price * item.quantity for item in items)"
}
```

---

#### `read_file_content`

파일 내용을 가져옵니다(행 범위 지정 가능).

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "파일 경로"
    },
    "start_line": {
      "type": "integer",
      "description": "시작 행 번호"
    },
    "end_line": {
      "type": "integer",
      "description": "종료 행 번호"
    }
  },
  "required": ["file_path"]
}
```

**사용 예:**

```json
{
  "name": "read_file_content",
  "arguments": {
    "file_path": "src/models/user.py",
    "start_line": 1,
    "end_line": 50
  }
}
```

**응답 예:**

```json
{
  "file": "src/models/user.py",
  "content": "from dataclasses import dataclass\n\n@dataclass\nclass User:\n    ...",
  "lines": "1-50"
}
```

---

#### `get_file_structure`

파일 구조 개요를 가져옵니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string",
      "description": "파일 경로"
    }
  },
  "required": ["file_path"]
}
```

**사용 예:**

```json
{
  "name": "get_file_structure",
  "arguments": {
    "file_path": "src/core/engine.py"
  }
}
```

**응답 예:**

```json
{
  "file": "src/core/engine.py",
  "entities": [
    {"type": "class", "name": "Engine", "lines": "15-200"},
    {"type": "method", "name": "__init__", "lines": "20-35"},
    {"type": "method", "name": "start", "lines": "37-55"},
    {"type": "method", "name": "stop", "lines": "57-70"}
  ]
}
```

---

### GraphRAG 도구

#### `global_search`

GraphRAG를 사용해 커뮤니티를 가로지르는 글로벌 검색을 실행합니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "검색 쿼리"
    }
  },
  "required": ["query"]
}
```

**사용 예:**

```json
{
  "name": "global_search",
  "arguments": {
    "query": "이 프로젝트의 인증 플로우는 어떻게 되어 있나요?"
  }
}
```

**응답 예:**

```json
{
  "query": "이 프로젝트의 인증 플로우는 어떻게 되어 있나요?",
  "answer": "이 프로젝트의 인증 플로우는 3단계로 구성되어 있습니다...",
  "communities_searched": 5,
  "confidence": 0.87,
  "relevant_communities": [
    {"id": 1, "name": "Authentication Module", "relevance": 0.95},
    {"id": 3, "name": "User Management", "relevance": 0.72}
  ],
  "supporting_entities": [
    {
      "id": "auth_service",
      "name": "AuthService",
      "type": "class",
      "file": "src/services/auth.py",
      "relevance": 0.95
    }
  ]
}
```

---

#### `local_search`

GraphRAG를 사용해 엔티티 근방의 로컬 검색을 실행합니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "검색 쿼리"
    },
    "entity_id": {
      "type": "string",
      "description": "검색 시작 엔티티"
    }
  },
  "required": ["query", "entity_id"]
}
```

**사용 예:**

```json
{
  "name": "local_search",
  "arguments": {
    "query": "이 클래스는 어떻게 사용되나요?",
    "entity_id": "user_repository"
  }
}
```

**응답 예:**

```json
{
  "query": "이 클래스는 어떻게 사용되나요?",
  "answer": "UserRepository는 주로 UserService에서 사용되고 있으며...",
  "start_entity": "user_repository",
  "entities_searched": 15,
  "confidence": 0.82,
  "relevant_entities": [
    {
      "id": "user_service",
      "name": "UserService",
      "type": "class",
      "relevance": 0.90
    }
  ],
  "relationships": [
    {"source": "user_service", "target": "user_repository", "type": "calls"}
  ]
}
```

---

### 관리 도구

#### `suggest_refactoring`

리팩터링 제안을 가져옵니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "entity_id": {
      "type": "string",
      "description": "분석 대상 엔티티"
    },
    "type": {
      "type": "string",
      "enum": ["extract", "rename", "move", "simplify"],
      "description": "리팩터링 종류"
    }
  },
  "required": ["entity_id"]
}
```

**사용 예:**

```json
{
  "name": "suggest_refactoring",
  "arguments": {
    "entity_id": "process_order",
    "type": "extract"
  }
}
```

**응답 예:**

```json
{
  "entity": "process_order",
  "suggestions": [
    {
      "type": "extract",
      "reason": "Function is 85 lines, consider extraction"
    },
    {
      "type": "simplify",
      "reason": "High cyclomatic complexity (12)"
    }
  ]
}
```

---

#### `reindex_repository`

리포지토리 재인덱싱을 트리거합니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "incremental": {
      "type": "boolean",
      "description": "증분 업데이트만 실행",
      "default": true
    }
  }
}
```

**사용 예:**

```json
{
  "name": "reindex_repository",
  "arguments": {
    "incremental": false
  }
}
```

**응답 예:**

```json
{
  "entities": 256,
  "relations": 512,
  "files": 45,
  "duration": 2.35
}
```

---

#### `execute_shell_command`

리포지토리 컨텍스트에서 셸 명령을 실행합니다.

**입력 스키마:**

```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "실행할 셸 명령"
    },
    "timeout": {
      "type": "integer",
      "description": "타임아웃(초)",
      "default": 30
    }
  },
  "required": ["command"]
}
```

**사용 예:**

```json
{
  "name": "execute_shell_command",
  "arguments": {
    "command": "git status",
    "timeout": 10
  }
}
```

**응답 예:**

```json
{
  "exit_code": 0,
  "stdout": "On branch main\nnothing to commit, working tree clean\n",
  "stderr": ""
}
```

---

## MCP Resources (4종)

### `codegraph://entities/{entity_id}`

특정 엔티티의 상세 정보를 가져옵니다.

**URI 패턴:** `codegraph://entities/{entity_id}`

**응답 예:**

```json
{
  "entity": {
    "id": "user_service",
    "type": "class",
    "name": "UserService",
    "qualified_name": "src.services.user_service.UserService",
    "file_path": "src/services/user_service.py",
    "start_line": 10,
    "end_line": 150,
    "signature": "class UserService:",
    "docstring": "Service for managing users.",
    "source_code": "class UserService:\n    ..."
  },
  "relations": {
    "callers": [
      {"id": "api_controller", "name": "APIController"}
    ],
    "callees": [
      {"id": "user_repository", "name": "UserRepository"}
    ]
  }
}
```

---

### `codegraph://files/{file_path}`

특정 파일의 코드 그래프 정보를 가져옵니다.

**URI 패턴:** `codegraph://files/{file_path}`

**응답 예:**

```json
{
  "file_path": "src/services/auth.py",
  "entities": [
    {
      "id": "auth_service",
      "type": "class",
      "name": "AuthService",
      "start_line": 15,
      "end_line": 120,
      "signature": "class AuthService:"
    },
    {
      "id": "authenticate",
      "type": "method",
      "name": "authenticate",
      "start_line": 25,
      "end_line": 55,
      "signature": "def authenticate(self, username: str, password: str) -> bool:"
    }
  ],
  "relations": [
    {"source": "auth_service", "target": "authenticate", "type": "contains"}
  ],
  "entity_count": 8
}
```

---

### `codegraph://communities/{community_id}`

코드 커뮤니티 정보를 가져옵니다.

**URI 패턴:** `codegraph://communities/{community_id}`

**응답 예:**

```json
{
  "community": {
    "id": 1,
    "level": 0,
    "name": "Authentication Module",
    "summary": "This community contains authentication-related classes and functions.",
    "member_count": 12
  },
  "members": [
    {"id": "auth_service", "type": "class", "name": "AuthService", "file": "src/services/auth.py"},
    {"id": "token_manager", "type": "class", "name": "TokenManager", "file": "src/auth/token.py"}
  ]
}
```

---

### `codegraph://stats`

코드 그래프 전체 통계 정보를 가져옵니다.

**URI 패턴:** `codegraph://stats`

**응답 예:**

```json
{
  "statistics": {
    "entities": 256,
    "relations": 512,
    "communities": 8,
    "files": 45,
    "languages": ["python", "typescript"]
  },
  "entities_by_type": {
    "class": 45,
    "function": 120,
    "method": 85,
    "module": 6
  },
  "relations_by_type": {
    "calls": 280,
    "contains": 150,
    "imports": 52,
    "implements": 30
  }
}
```

---

## MCP Prompts (6종)

### `code_review`

코드 리뷰를 수행하기 위한 프롬프트를 생성합니다.

**인자:**

| 이름          | 필수 | 설명                                  |
| ----------- | -- | ----------------------------------- |
| `entity_id` | ✅  | 리뷰 대상 엔티티 ID                        |
| `focus`     | ❌  | 리뷰 초점(security, performance, style) |

**사용 예:**

```json
{
  "name": "code_review",
  "arguments": {
    "entity_id": "process_payment",
    "focus": "security"
  }
}
```

**생성되는 프롬프트(요약):**

```
# Code Review Request

## Entity Information
- Name: process_payment
- Type: function
- File: src/payments/processor.py:45-120

## Source Code
[코드 포함]

## Context
- Called by: PaymentController.handle_payment, ...
- Calls: validate_card, charge_card, ...

## Review Focus
security

Please review this code for:
1. Potential bugs or errors
2. Code quality issues
3. Performance concerns
4. Security vulnerabilities
5. Suggestions for improvement
```

---

### `explain_codebase`

코드베이스 전체 설명을 생성하기 위한 프롬프트를 생성합니다.

**인자:**

| 이름      | 필수 | 설명                        |
| ------- | -- | ------------------------- |
| `depth` | ❌  | 설명 깊이(overview, detailed) |

**사용 예:**

```json
{
  "name": "explain_codebase",
  "arguments": {
    "depth": "detailed"
  }
}
```

---

### `implement_feature`

신규 기능 구현 가이던스를 제공하는 프롬프트를 생성합니다.

**인자:**

| 이름                 | 필수 | 설명        |
| ------------------ | -- | --------- |
| `description`      | ✅  | 기능 설명     |
| `related_entities` | ❌  | 관련 기존 엔티티 |

**사용 예:**

```json
{
  "name": "implement_feature",
  "arguments": {
    "description": "사용자 인증에 2단계 인증을 추가한다",
    "related_entities": "auth_service,user_service"
  }
}
```

---

### `debug_issue`

문제 디버깅을 지원하는 프롬프트를 생성합니다.

**인자:**

| 이름              | 필수 | 설명           |
| --------------- | -- | ------------ |
| `error_message` | ✅  | 에러 메시지 또는 증상 |
| `context`       | ❌  | 추가 컨텍스트      |

**사용 예:**

```json
{
  "name": "debug_issue",
  "arguments": {
    "error_message": "TypeError: 'NoneType' object is not subscriptable at line 45",
    "context": "This occurs when processing user input from the API"
  }
}
```

---

### `refactor_guidance`

리팩터링 가이던스를 제공하는 프롬프트를 생성합니다.

**인자:**

| 이름          | 필수 | 설명          |
| ----------- | -- | ----------- |
| `entity_id` | ✅  | 리팩터링 대상 엔티티 |
| `goal`      | ❌  | 리팩터링 목표     |

**사용 예:**

```json
{
  "name": "refactor_guidance",
  "arguments": {
    "entity_id": "data_processor",
    "goal": "improve testability"
  }
}
```

---

### `test_generation`

테스트 코드를 생성하기 위한 프롬프트를 생성합니다.

**인자:**

| 이름          | 필수 | 설명                        |
| ----------- | -- | ------------------------- |
| `entity_id` | ✅  | 테스트 대상 엔티티                |
| `test_type` | ❌  | 테스트 종류(unit, integration) |

**사용 예:**

```json
{
  "name": "test_generation",
  "arguments": {
    "entity_id": "calculate_shipping",
    "test_type": "unit"
  }
}
```

---

## 데이터 타입

### Entity

코드 엔티티를 나타내는 구조체.

| 필드               | 타입         | 설명      |
| ---------------- | ---------- | ------- |
| `id`             | string     | 고유 식별자  |
| `type`           | EntityType | 엔티티 유형  |
| `name`           | string     | 이름      |
| `qualified_name` | string     | 완전 수식명  |
| `file_path`      | string     | 파일 경로   |
| `start_line`     | integer    | 시작 행 번호 |
| `end_line`       | integer    | 종료 행 번호 |
| `signature`      | string     | 시그니처    |
| `docstring`      | string     | 문서 문자열  |
| `source_code`    | string     | 소스 코드   |

### EntityType

엔티티 유형 열거형.

| 값           | 설명    |
| ----------- | ----- |
| `module`    | 모듈    |
| `class`     | 클래스   |
| `function`  | 함수    |
| `method`    | 메서드   |
| `interface` | 인터페이스 |
| `enum`      | 열거형   |
| `struct`    | 구조체   |
| `trait`     | 트레이트  |

### RelationType

관계 유형 열거형.

| 값            | 설명  |
| ------------ | --- |
| `calls`      | 호출  |
| `contains`   | 포함  |
| `imports`    | 임포트 |
| `implements` | 구현  |
| `extends`    | 상속  |
| `uses`       | 사용  |
| `defines`    | 정의  |

---

## 에러 핸들링

모든 도구는 에러 발생 시 아래 형식으로 에러를 반환합니다:

```json
{
  "error": "Entity not found",
  "entity_id": "unknown_entity"
}
```

일반적인 에러:

| 에러                    | 원인                | 대응 방법           |
| --------------------- | ----------------- | --------------- |
| `Entity not found`    | 지정한 엔티티가 존재하지 않음  | entity_id 확인    |
| `File not found`      | 지정한 파일이 존재하지 않음   | 파일 경로 확인        |
| `Community not found` | 지정한 커뮤니티가 존재하지 않음 | community_id 확인 |
| `Unknown tool`        | 존재하지 않는 도구를 호출함   | 도구 이름 확인        |
| `Command timed out`   | 셸 명령이 타임아웃        | timeout 값을 늘림   |

---

## 버전 정보

- API 버전: 1.0
- MCP 프로토콜 버전: 2024-11-05
- 서버 버전: 0.1.0
