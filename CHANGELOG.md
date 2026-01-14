# 변경이력

이 프로젝트의 주목할 만한 변경 사항은 모두 이 파일에 기록된다.

포맷은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따르며,  
이 프로젝트는 [시맨틱 버저닝](https://semver.org/lang/ko/)을 준수한다.

## [0.9.0] - 2025-12-11

### 추가

#### 신규 언어 지원 (4개 언어)
- **Kotlin** (`kotlin.py`): 클래스, 인터페이스, 객체, 함수, 프로퍼티 추출
  - 지원 확장자: `.kt`, `.kts`
  - tree-sitter-kotlin >= 1.0.0
- **Swift** (`swift.py`): 클래스, 구조체, 프로토콜, 함수, 익스텐션 추출
  - 지원 확장자: `.swift`
  - tree-sitter-swift >= 0.0.1
- **Scala** (`scala.py`): 클래스, 트레이트, 객체, 함수 추출
  - 지원 확장자: `.scala`, `.sc`
  - tree-sitter-scala >= 0.20.0
- **Lua** (`lua.py`): 함수, 로컬 함수, 테이블 할당 추출
  - 지원 확장자: `.lua`
  - tree-sitter-lua >= 0.1.0

### 변경
- 지원 언어 수: **16개 언어** (기존 12개에서 증가)
- parser.py에 신규 언어용 LANGUAGE_EXTENSIONS 추가
- `__init__.py`에 신규 추출기(Extractor) 등록 추가

### 테스트
- Kotlin, Swift, Scala, Lua 추출기용 신규 테스트 26건 추가
- 총 테스트 결과: **334 passed**, 1 skipped

---

## [0.7.0] - 2025-11-27

### 추가

#### C 언어 지원
- `.c` 파일 확장자 지원 추가(순수 C 언어)
- C 파일은 Tree-sitter C++ 파서로 분석
- 지원 확장자: `.c`, `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`, `.hxx`
- 지원 언어 수: **12개 언어** (기존 11개에서 증가)

#### 파일 감시(`watch` 명령)
- **`codegraph-mcp watch`**: 리포지토리를 감시하고 파일 변경 시 자동 재인덱싱
  - 설정 가능한 디바운스를 통한 실시간 파일 감시
  - `--debounce` 옵션으로 변경 간 지연 시간 설정(기본값: 1.0초)
  - `--community` 플래그로 재인덱싱 후 커뮤니티 탐지 실행
  - 지원 언어 파일만 필터링
  - Ctrl+C로 정상 종료 지원

#### GitHub Actions CI/CD
- **CI 워크플로** (`.github/workflows/ci.yml`):
  - main 브랜치로의 push/PR 시 실행
  - Python 3.11 및 3.12에서 테스트
  - ruff를 이용한 린팅, mypy를 이용한 타입 체크
  - Codecov로 커버리지 리포트 업로드
  - 빌드 검증
- **릴리스 워크플로** (`.github/workflows/release.yml`):
  - 버전 태그(v*) 기준으로 트리거
  - 릴리스 전 테스트 실행
  - 아티팩트를 포함한 GitHub 릴리스 생성
  - PyPI로 자동 배포

### 변경
- cpp.py 추출기(Extractor)의 docstring을 “C/C++ 전용”으로 업데이트
- parser.py의 LANGUAGE_EXTENSIONS에 C/C++ 매핑 추가

### 테스트
- watch 명령용 신규 CLI 테스트 8건 추가
- 합계: 308 passed, 1 skipped

---

## [0.6.0] - 2025-11-27

### 추가

#### 엔티티 ID 부분 일치 지원
- **`resolve_entity_id()`**: 부분적인 엔티티 ID를 완전한 ID로 해석
  - 완전 일치, 이름 일치, qualified_name 접미사 일치
  - `file::name` 패턴 지원 (예: `linux.rs::hashmap_random_keys`)
- **`search_entities()`**: 패턴 기반 엔티티 검색
- `find_callers()`, `find_callees()`, `find_dependencies()`에서 부분 ID 지원

#### 자동 커뮤니티 탐지
- **`--community` 플래그**(기본값): 인덱싱 후 자동으로 커뮤니티 탐지 수행
- **`--no-community` 플래그**: 대규모 리포지토리를 위해 커뮤니티 탐지 생략
- 인덱싱 결과에 커뮤니티 수와 모듈성(Modularity) 표시

#### query_codebase 기능 강화
- **관련도 스코어링**: 완전 일치 (1.0), 접두사 일치 (0.8), 부분 일치 (0.6)
- **`include_related`**: 관련 엔티티를 결과에 포함
- **`include_community`**: 커뮤니티 정보 포함
- **`entity_types` 필터**: function, class, method 등으로 필터링
- JSON 출력에 score 및 community_id 포함

#### 증분 커뮤니티 업데이트
- **`update_incremental()`**: 변경된 엔티티를 최적의 커뮤니티로 재할당
- 변경 비율 20% 초과 시 전체 재탐지 트리거
- 변경 추적을 위한 `IndexResult.changed_entity_ids` 제공

#### 백그라운드 서버 관리
- **`codegraph-mcp start`**: MCP 서버를 백그라운드(데몬 모드)로 실행
  - 기본값으로 포트 8080의 SSE 트랜스포트 사용
  - PID 파일은 `~/.codegraph/server.pid`에 저장
  - 로그는 `~/.codegraph/server.log`에 기록
- **`codegraph-mcp stop`**: 백그라운드 MCP 서버 정상 종료
- **`codegraph-mcp status`**: 최신 로그와 함께 서버 상태 확인


### 변경

#### 커뮤니티 탐지 성능 개선
- **배치 그래프 구성**: 성능 향상을 위해 `add_nodes_from()` / `add_edges_from()` 사용
- **배치 DB 쓰기**: 커뮤니티 저장 시 `executemany()` 사용
- **대규모 그래프 샘플링**: 차수 기반 샘플링으로 `max_nodes=50000` 적용
- 23만 개 이상의 엔티티를 가진 리포지토리 처리 성공

#### SSE 트랜스포트
- `/messages/` 엔드포인트에서 `Route` 대신 `Mount`를 사용하도록 수정
- 클라이언트 연결 종료 시 NoneType 오류를 방지하기 위해 적절한 `Response()` 반환
- 공식 MCP SSE 구현 패턴에 맞게 수정

#### CLI 유니코드 호환성
- 일부 터미널에서 인코딩 오류를 유발하던 유니코드 이모지 제거
- 서러게이트 인코딩 문제를 방지하기 위해 `SpinnerColumn` 제거
- 더 넓은 호환성을 위해 Rich 콘솔에 `legacy_windows=True` 옵션 추가

### 테스트 완료
- Rust 컴파일러 리포지토리(23만+ 엔티티, 3만4천+ 파일) 인덱싱 성공
- SSE 트랜스포트를 통해 14개 MCP 도구 전부 정상 동작 확인

### 테스트
- 스코어링 및 커뮤니티 통합을 위한 신규 테스트 6건 추가
- 합계: 300 passed, 1 skipped

---

## [0.5.0] - 2025-11-25

### 변경

#### 성능 최적화 - 배치 데이터베이스 쓰기
- **인덱싱 성능 47배 향상**: 엔티티와 관계(Relation)에 대한 배치 쓰기 처리 구현
  - 변경 전: 67개 파일 기준 29.47초 (초당 32 엔티티)
  - 변경 후: 67개 파일 기준 0.63초 (초당 1495 엔티티)
- 리포지토리당 데이터베이스 커밋 횟수를 약 5700회에서 3회로 감소
- GraphEngine에 `add_entities_batch()` 및 `add_relations_batch()` 메서드 추가
- 배치 쓰기 이전에 모든 분석 결과를 수집하도록 Indexer 로직 개선

#### 기술 상세
- 대량 삽입(Bulk Insert)에 SQLite의 `executemany()` 사용
- 엔티티/관계 단위가 아닌 배치 단위로 단일 커밋 수행
- 배치 파일 추적 로직 업데이트

#### CLI 기능 강화
- **Rich 진행 표시**: `codegraph-mcp index` 명령에 애니메이션이 포함된 진행 바 추가
  - 실시간 진행 바가 포함된 스피너 애니메이션
  - 파일 단위 처리 상태 표시
  - 엔티티/관계 수 및 소요 시간을 포함한 결과 테이블
  - 색상으로 구분된 상태 메시지

#### 성능 측정 결과(실측)
- 인덱싱 속도: **초당 32 엔티티**
- 파일 처리 시간: **파일당 0.44초**
- 증분 인덱싱: **2초 미만**
- 쿼리 응답 시간: **2ms 미만**


---

## [0.4.0] - 2025-11-27

### 追加

#### CLI強化
- **Richプログレス表示**: `codegraph-mcp index` コマンドにアニメーション付きプログレスバーを追加
  - リアルタイムプログレスバー付きスピナーアニメーション
  - ファイルごとの処理表示
  - エンティティ/リレーション数と所要時間を含む結果テーブル
  - 色分けされたステータスメッセージ

#### パフォーマンス測定値（実測）
- インデックス速度: **32 エンティティ/秒**
- ファイル処理: **0.44 秒/ファイル**
- 増分インデックス: **< 2秒**
- クエリレスポンス: **< 2ms**

### 변경
- CLI 진행 표시를 위해 `rich>=13.0.0` 의존성 추가
- `Indexer.index_repository()`에 선택적 `progress_callback` 파라미터 추가

---

## [0.1.0] - 2025-11-24

### 추가

#### 언어 지원 - 신규 7개 언어
- **Go 언어 지원**: Go 소스 파일에 대한 완전한 AST 분석
  - 리시버 타입을 포함한 함수 및 메서드 추출
  - 구조체 및 인터페이스 추출
  - 패키지 및 import 처리
  - 호출 관계 탐지

- **Java 언어 지원**: 포괄적인 Java 분석
  - 클래스, 인터페이스, 열거형 추출
  - 메서드 및 생성자 추출
  - 상속 관계(extends / implements) 탐지
  - import 문 처리

- **PHP 언어 지원**: PHP 소스 파일에 대한 완전한 AST 분석
  - 클래스, 인터페이스, 트레이트 추출
  - 메서드 및 함수 추출
  - 네임스페이스 처리
  - 상속 및 implements 관계 탐지

- **C# 언어 지원**: 포괄적인 C# 분석
  - 클래스, 구조체, 인터페이스, 열거형 추출
  - 메서드, 생성자, 프로퍼티 추출
  - 네임스페이스 처리
  - 상속 관계 탐지
  - using 디렉티브 처리

- **C++ 언어 지원**: 완전한 C++ 분석
  - 클래스 및 구조체 추출
  - 함수 및 메서드 추출(헤더 선언 포함)
  - 네임스페이스 처리
  - include 디렉티브 처리
  - 상속 관계 탐지
  - 템플릿 클래스 지원

- **HCL (Terraform) 언어 지원**: Infrastructure as Code 분석
  - 리소스 및 데이터 소스 추출
  - 변수 및 출력(Output) 추출
  - 모듈 및 locals 블록 추출
  - 프로바이더 블록 추출

- **Ruby 언어 지원**: 완전한 Ruby 분석
  - 클래스 및 모듈 추출
  - 메서드 및 싱글톤 메서드 추출
  - 상속 관계 탐지
  - require / require_relative 처리
  - 모듈 include / extend 탐지

- **AST 분석**: Tree-sitter 기반 다중 언어 코드 분석
  - 클래스/함수/메서드 추출을 포함한 Python 지원
  - 인터페이스 및 타입 별칭 처리를 포함한 TypeScript 지원
  - JavaScript 지원(ES6+, JSX, CommonJS, ESM)
  - struct / enum / trait / impl 추출을 포함한 Rust 지원

- **코드 그래프 엔진**: NetworkX 기반 그래프 구성
  - 엔티티 추출(클래스, 함수, 메서드, 모듈)
  - 관계 탐지(calls, contains, imports, implements, extends)
  - 설정 가능한 깊이의 의존성 분석

- **GraphRAG 통합**: 그래프 기반 검색 증강 생성
  - Louvain 알고리즘 기반 커뮤니티 탐지
  - 전체 코드 커뮤니티를 아우르는 글로벌 검색
  - 엔티티 인접 영역 기반 로컬 검색
  - LLM 통합(OpenAI, Anthropic, Ollama, 룰 기반)

- **스토리지 계층**: SQLite 기반 영속화
  - aiosqlite를 활용한 비동기 DB 처리
  - 성능 향상을 위한 파일 기반 캐싱
  - 시맨틱 검색을 위한 벡터 스토리지

#### MCP 인터페이스
- **14개 MCP 도구**:
  - 그래프 쿼리: `query_codebase`, `find_dependencies`, `find_callers`, `find_callees`, `find_implementations`, `analyze_module_structure`
  - 코드 조회: `get_code_snippet`, `read_file_content`, `get_file_structure`
  - GraphRAG: `global_search`, `local_search`
  - 관리: `suggest_refactoring`, `reindex_repository`, `execute_shell_command`

- **4개 MCP 리소스**:
  - `codegraph://entities/{id}` - 엔티티 상세 정보
  - `codegraph://files/{path}` - 파일 그래프 정보
  - `codegraph://communities/{id}` - 커뮤니티 데이터
  - `codegraph://stats` - 그래프 통계

- **6개 MCP 프롬프트**:
  - `code_review` - 코드 리뷰 지원
  - `explain_codebase` - 코드베이스 설명
  - `implement_feature` - 기능 구현 가이드
  - `debug_issue` - 디버깅 지원
  - `refactor_guidance` - 리팩터링 제안
  - `test_generation` - 테스트 생성 지원

#### 트랜스포트 프로토콜
- 표준 MCP 클라이언트용 stdio 트랜스포트(기본값)
- HTTP 기반 통합을 위한 SSE 트랜스포트

#### CLI 명령
- `codegraph-mcp serve` - MCP 서버 실행
- `codegraph-mcp index` - 리포지토리 인덱싱
- `codegraph-mcp query` - 코드 엔티티 검색
- `codegraph-mcp stats` - 그래프 통계 출력

#### 문서
- 포괄적인 API 레퍼런스(`docs/api.md`)
- 설정 가이드(`docs/configuration.md`)
- 사용 예제(`docs/examples.md`)
- `examples/` 디렉터리 내 샘플 스크립트

### 성능
- 초기 인덱싱: 약 700개 엔티티를 21초에 처리
- 쿼리 응답 시간: 평균 2ms 미만
- 증분 인덱싱: 2초 미만

### 변경
- `tree-sitter-php`, `tree-sitter-c-sharp`, `tree-sitter-cpp`, `tree-sitter-hcl`, `tree-sitter-ruby`, `tree-sitter-go`, `tree-sitter-java`를 포함하도록 의존성 업데이트
- 7개의 신규 추출기(Extractor)로 언어 레지스트리 확장

### 테스트
- PHP, C#, C++, HCL, Ruby, Java, Go 파서용 신규 테스트 103건 추가
- 테스트 총계: 345건 (v0.1.0의 312건에서 증가)

---

## [진행중]

### 진행중인 기능
- 10만 라인 이상의 리포지토리를 위한 성능 최적화
- MkDocs 기반 문서 사이트
- 그래프 시각화를 위한 Web UI

---
