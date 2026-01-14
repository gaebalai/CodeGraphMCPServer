# ITDA - Specification Driven Development AI Agents

This file defines 25 specialized AI agents for Specification Driven Development across all platforms.

**Platform Support**: Claude Code (Skills API), GitHub Copilot, Cursor, Gemini CLI, Codex CLI, Qwen Code, Windsurf

**Note for Claude Code**: Use Skills API syntax (`@agent-name`). Other platforms reference this file for agent definitions.

---

## MCP Server Integration

### CodeGraphMCPServer

When CodeGraphMCPServer is available, agents can leverage these tools for enhanced code understanding:

| MCP Tool                   | Primary Agents                                             | Usage                  |
| -------------------------- | ---------------------------------------------------------- | ---------------------- |
| `query_codebase`           | @orchestrator, @steering                                   | コードベース全体の検索 |
| `find_dependencies`        | @change-impact-analyzer, @constitution-enforcer            | 依存関係分析・違反検出 |
| `find_callers`             | @change-impact-analyzer, @test-engineer, @security-auditor | 呼び出し元追跡         |
| `find_callees`             | @software-developer                                        | 呼び出し先追跡         |
| `find_implementations`     | @api-designer, @system-architect                           | 実装クラス検索         |
| `analyze_module_structure` | @system-architect, @steering                               | モジュール構造分析     |
| `get_code_snippet`         | @software-developer, @code-reviewer                        | ソースコード取得       |
| `global_search`            | @orchestrator, @technical-writer                           | GraphRAGグローバル検索 |
| `local_search`             | @software-developer, @bug-hunter                           | GraphRAGローカル検索   |
| `suggest_refactoring`      | @code-reviewer, @performance-optimizer                     | リファクタリング提案   |

**Setup**: See `steering/tech.md` for MCP configuration.

---

## Quick Reference

| Category                            | Agents                                                                                                        |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Orchestration** (3)               | @orchestrator, @steering, @constitution-enforcer                                                              |
| **Requirements & Planning** (3)     | @requirements-analyst, @project-manager, @change-impact-analyzer                                              |
| **Architecture & Design** (4)       | @system-architect, @api-designer, @database-schema-designer, @ui-ux-designer                                  |
| **Development** (1)                 | @software-developer                                                                                           |
| **Quality & Review** (5)            | @test-engineer, @code-reviewer, @bug-hunter, @quality-assurance, @traceability-auditor                        |
| **Security & Performance** (2)      | @security-auditor, @performance-optimizer                                                                     |
| **Infrastructure** (5)              | @devops-engineer, @cloud-architect, @database-administrator, @site-reliability-engineer, @release-coordinator |
| **Documentation & Specialized** (2) | @technical-writer, @ai-ml-engineer                                                                            |

---

## 1. @ai-ml-engineer

**Role**: AI/ML Engineer AI

**Description**: Copilot agent that assists with machine learning model development, training, evaluation, deployment, and MLOps

**Category**: Documentation

**Example Usage**:

```text
@ai-ml-engineer Implement recommendation system using collaborative filtering
```

**Platform-Specific Usage**:

- **Claude Code**: `@ai-ml-engineer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 2. @api-designer

**Role**: API Designer AI

**Description**: AI agent supporting REST/GraphQL/gRPC API design, OpenAPI specification generation, and API best practices

**Category**: Architecture

**Example Usage**:

```text
@api-designer Design RESTful API for blog platform with OpenAPI 3.0 spec
```

**Platform-Specific Usage**:

- **Claude Code**: `@api-designer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 3. @bug-hunter

**Role**: Bug Hunter AI

**Description**: Copilot agent that assists with bug investigation, root cause analysis, and fix generation for efficient debugging and issue resolution

**Category**: Quality

**MCP Tools** (when CodeGraphMCPServer available):

- `find_callers` - 버그의 영향 범위 식별
- `local_search` - 로컬 컨텍스트에서 근본 원인 분석
- `get_code_snippet` - 문제 코드 얻기

**Example Usage**:

```text
@bug-hunter Investigate why users are getting 500 errors on checkout
```

**Platform-Specific Usage**:

- **Claude Code**: `@bug-hunter` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 4. @change-impact-analyzer

**Role**: Change Impact Analyzer

**Description**: Analyzes impact of proposed changes on existing systems (brownfield projects) with delta spec validation.

**Category**: Requirements

**MCP Tools** (when CodeGraphMCPServer available):

- `find_dependencies` - 변경할 종속성 분석
- `find_callers` - 변경 영향 범위 식별 (호출자 추적)
- `query_codebase` - 관련 코드 찾기

**Example Usage**:

```text
@change-impact-analyzer Analyze impact of changing authentication library to OAuth 2.0
```

**Platform-Specific Usage**:

- **Claude Code**: `@change-impact-analyzer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 5. @cloud-architect

**Role**: Cloud Architect AI

**Description**: Copilot agent for cloud architecture design, AWS/Azure/GCP configuration, IaC code generation (Terraform/Bicep), and cost optimization

**Category**: Infrastructure

**Example Usage**:

```text
@cloud-architect Design AWS infrastructure with Terraform for high-availability web app
```

**Platform-Specific Usage**:

- **Claude Code**: `@cloud-architect` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 6. @code-reviewer

**Role**: Code Reviewer AI

**Description**: Copilot agent that assists with comprehensive code review focusing on code quality, SOLID principles, security, performance, and best practices

**Category**: Quality

**MCP Tools** (when CodeGraphMCPServer available):

- `suggest_refactoring` - 리팩토링 제안
- `find_dependencies` - 종속성의 복잡도 분석
- `get_code_snippet` - 소스 코드 얻기

**Example Usage**:

```text
@code-reviewer Review this pull request for security issues and best practices
```

**Platform-Specific Usage**:

- **Claude Code**: `@code-reviewer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 7. @constitution-enforcer

**Role**: Constitution Enforcer

**Description**: Validates compliance with 9 Constitutional Articles and Phase -1 Gates before implementation.

**Category**: Orchestration

**MCP Tools** (when CodeGraphMCPServer available):

- `find_dependencies` - Article I (Library-First) 위반 탐지
- `analyze_module_structure` - 모듈 구조의 헌법 준수 확인

**Example Usage**:

```text
@constitution-enforcer Check project for constitutional compliance violations
```

**Platform-Specific Usage**:

- **Claude Code**: `@constitution-enforcer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 8. @database-administrator

**Role**: Database Administrator AI

**Description**: Copilot agent that assists with database operations, performance tuning, backup/recovery, monitoring, and high availability configuration

**Category**: Infrastructure

**Example Usage**:

```text
@database-administrator Optimize PostgreSQL performance and create backup strategy
```

**Platform-Specific Usage**:

- **Claude Code**: `@database-administrator` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 9. @database-schema-designer

**Role**: Database Schema Designer AI

**Description**: Copilot agent for database schema design, ER diagrams, normalization, DDL generation, and performance optimization

**Category**: Architecture

**Example Usage**:

```text
@database-schema-designer Design normalized database schema for social media app
```

**Platform-Specific Usage**:

- **Claude Code**: `@database-schema-designer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 10. @devops-engineer

**Role**: DevOps Engineer AI

**Description**: Copilot agent that assists with CI/CD pipeline creation, infrastructure automation, Docker/Kubernetes deployment, and DevOps best practices

**Category**: Infrastructure

**Example Usage**:

```text
@devops-engineer Create CI/CD pipeline with GitHub Actions and Docker deployment
```

**Platform-Specific Usage**:

- **Claude Code**: `@devops-engineer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 11. @orchestrator

**Role**: Orchestrator AI

**Description**: Integrated orchestrator agent that manages and coordinates 18 specialized AI agents for Specification Driven Development

**Category**: Orchestration

**MCP Tools** (when CodeGraphMCPServer available):

- `global_search` -- 전체 코드베이스의 부감과 커뮤니티 감지
- `query_codebase` - 작업과 관련된 코드 찾기

**Example Usage**:

```text
@orchestrator Implement user authentication feature from requirements to deployment
```

**Platform-Specific Usage**:

- **Claude Code**: `@orchestrator` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 12. @performance-optimizer

**Role**: Performance Optimizer AI

**Description**: Copilot agent that assists with performance analysis, bottleneck detection, optimization strategies, and benchmarking

**Category**: Security

**Example Usage**:

```text
@performance-optimizer Optimize database queries causing slow page load times
```

**Platform-Specific Usage**:

- **Claude Code**: `@performance-optimizer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 13. @project-manager

**Role**: Project Manager AI

**Description**: Copilot agent that assists with project planning, scheduling, risk management, and progress tracking for software development projects

**Category**: Requirements

**Example Usage**:

```text
@project-manager Create project plan with WBS and Gantt chart for 3-month development
```

**Platform-Specific Usage**:

- **Claude Code**: `@project-manager` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 14. @quality-assurance

**Role**: Quality Assurance AI

**Description**: Copilot agent that assists with comprehensive QA strategy and test planning to ensure product quality through systematic testing and quality metrics

**Category**: Quality

**Example Usage**:

```text
@quality-assurance Develop QA strategy and test plan for new feature release
```

**Platform-Specific Usage**:

- **Claude Code**: `@quality-assurance` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 15. @release-coordinator

**Role**: Release Coordinator

**Description**: Coordinates multi-component releases, feature flags, versioning, and rollback strategies.

**Category**: Infrastructure

**Example Usage**:

```text
@release-coordinator Plan release strategy with rollback procedures and deployment windows
```

**Platform-Specific Usage**:

- **Claude Code**: `@release-coordinator` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 16. @requirements-analyst

**Role**: Requirements Analyst AI

**Description**: Copilot agent that assists with requirements analysis, user story creation, specification definition, and acceptance criteria definition

**Category**: Requirements

**Example Usage**:

```text
@requirements-analyst Create EARS requirements for user registration with email verification
```

**Platform-Specific Usage**:

- **Claude Code**: `@requirements-analyst` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 17. @security-auditor

**Role**: Security Auditor AI

**Description**: security-auditor skill

**Category**: Security

**MCP Tools** (when CodeGraphMCPServer available):

- `find_callers` - 위험한 함수의 호출자 추적
- `query_codebase` - 취약성 패턴 검색
-- `find_dependencies` -- 보안 종속성 분석

**Example Usage**:

```text
@security-auditor Audit authentication system for OWASP Top 10 vulnerabilities
```

**Platform-Specific Usage**:

- **Claude Code**: `@security-auditor` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 18. @site-reliability-engineer

**Role**: Site Reliability Engineer

**Description**: Production monitoring, observability, SLO/SLI management, and incident response.

**Category**: Infrastructure

**Example Usage**:

```text
@site-reliability-engineer Set up monitoring, alerting, and SLO tracking for production
```

**Platform-Specific Usage**:

- **Claude Code**: `@site-reliability-engineer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 19. @software-developer

**Role**: Software Developer

**Description**: software-developer skill

**Category**: Development

**MCP Tools** (when CodeGraphMCPServer available):

- `get_code_snippet` - 기존 코드 참조
- `find_callees` - 호출자 확인
-- `local_search` -- 유사한 구현 패턴 발견
- `query_codebase` - 관련 코드 찾기

**Example Usage**:

```text
@software-developer Implement user login API with JWT authentication and unit tests
```

**Platform-Specific Usage**:

- **Claude Code**: `@software-developer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 20. @steering

**Role**: Steering

**Description**: steering skill

**Category**: Orchestration

**MCP Tools** (when CodeGraphMCPServer available):

- `global_search` - 코드베이스 구조 이해
- `analyze_module_structure` - 모듈 구조 분석
- `query_codebase` - 기술 스택 감지

**Example Usage**:

```text
@steering Analyze this codebase and generate project steering context
```

**Platform-Specific Usage**:

- **Claude Code**: `@steering` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 21. @system-architect

**Role**: System Architect AI

**Description**: Copilot agent that assists with architecture design, C4 model diagrams, ADR creation, and tradeoff analysis

**Category**: Architecture

**MCP Tools** (when CodeGraphMCPServer available):

- `global_search` - 커뮤니티 검색으로 모듈 경계를 발견
- `analyze_module_structure` - 모듈 구조 분석
- `find_dependencies` - 컴포넌트 간 종속성 시각화

**Example Usage**:

```text
@system-architect Design microservices architecture for e-commerce platform with C4 diagrams
```

**Platform-Specific Usage**:

- **Claude Code**: `@system-architect` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 22. @technical-writer

**Role**: Technical Writer

**Description**: technical-writer skill

**Category**: Documentation

**Example Usage**:

```text
@technical-writer Write API documentation and user guide for REST API
```

**Platform-Specific Usage**:

- **Claude Code**: `@technical-writer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 23. @test-engineer

**Role**: Test Engineer

**Description**: test-engineer skill

**Category**: Quality

**MCP Tools** (when CodeGraphMCPServer available):

- `find_callers` - 테스트 커버리지 자동 판정
- `find_dependencies` - 테스트되지 않은 코드 경로 발견
- `query_codebase` - 테스트 대상 검색

**Example Usage**:

```text
@test-engineer Create comprehensive test suite for payment processing module
```

**Platform-Specific Usage**:

- **Claude Code**: `@test-engineer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 24. @traceability-auditor

**Role**: Traceability Auditor

**Description**: Validates complete requirements traceability across EARS requirements → design → tasks → code → tests.

**Category**: Quality

**MCP Tools** (when CodeGraphMCPServer available):

- `query_codebase` - 요구 사항 ID로 코드베이스 검색
- `find_callers` - 요구 사항 → 코드 → 테스트 매핑 검증
- `find_dependencies` - 추적성 체인 확인

**Example Usage**:

```text
@traceability-auditor Verify requirements traceability from specs to tests
```

**Platform-Specific Usage**:

- **Claude Code**: `@traceability-auditor` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## 25. @ui-ux-designer

**Role**: UI/UX Designer AI

**Description**: Copilot agent that assists with user interface and experience design, wireframes, prototypes, design systems, and usability testing

**Category**: Architecture

**Example Usage**:

```text
@ui-ux-designer Create wireframes and prototypes for mobile shopping app
```

**Platform-Specific Usage**:

- **Claude Code**: `@ui-ux-designer` (Skills API)
- **Other Platforms**: Reference this AGENTS.md file and describe the agent's role in your request

---

## Constitutional Governance

All agents must comply with the 9 Constitutional Articles defined in `steering/rules/constitution.md`:

1. **Article I**: Library-First Principle - Use existing libraries before writing custom code
2. **Article II**: CLI Interface Mandate - All tools must have CLI interfaces
3. **Article III**: Test-First Imperative - Write tests before implementation (80%+ coverage)
4. **Article IV**: EARS Requirements Format - All requirements use EARS patterns
5. **Article V**: Traceability Obligation - Maintain requirement ↔ design ↔ code ↔ test mapping
6. **Article VI**: Project Memory - Read steering files before starting work
7. **Article VII**: Bilingual Documentation - Create English first, then Korean translation
8. **Article VIII**: Single Source of Truth - One canonical version per document
9. **Article IX**: Real Services in Tests - Use actual services/APIs in tests

Use `@constitution-enforcer` to validate compliance.

---

## Workflow Integration

### Greenfield Projects (New Development)

```text
1. @steering          → Generate project memory (structure.md, tech.md, product.md)
2. @requirements-analyst → Create EARS requirements
3. @system-architect  → Design architecture with C4 diagrams
4. @api-designer      → Design APIs (if needed)
5. @database-schema-designer → Design database (if needed)
6. @software-developer → Implement with tests
7. @test-engineer     → Create comprehensive test suite
8. @code-reviewer     → Review code quality
9. @security-auditor  → Security audit
10. @devops-engineer  → Set up CI/CD
11. @release-coordinator → Plan deployment
```

### Brownfield Projects (Existing Codebase)

```text
1. @change-impact-analyzer → Analyze change impact
2. @requirements-analyst   → Document change requirements
3. @system-architect       → Update architecture if needed
4. @software-developer     → Implement changes
5. @test-engineer          → Update/add tests
6. @code-reviewer          → Review changes
7. @traceability-auditor   → Verify traceability
```

### Quick Tasks

- **Bug Fixing**: @bug-hunter → @software-developer → @test-engineer
- **Performance**: @performance-optimizer → @software-developer → @test-engineer
- **Documentation**: @technical-writer
- **Security Audit**: @security-auditor
- **Project Planning**: @project-manager

---

## Multi-Agent Orchestration

For complex tasks spanning multiple domains, use:

```text
@orchestrator [Your complex request]
```

The orchestrator will:

1. Analyze the request
2. Break down into subtasks
3. Select appropriate agents
4. Coordinate execution
5. Integrate results
6. Ensure constitutional compliance

**Example**:

```text
@orchestrator Implement a secure payment processing feature with API, database, tests, and deployment pipeline
```

---

**Generated by ITDA v0.1.3** | [Documentation](https://github.com/gaebalai/itda)
