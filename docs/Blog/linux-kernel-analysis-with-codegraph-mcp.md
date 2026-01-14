---
title: 'CodeGraph MCP와 VS Code로 Linux 커널 코드를 분석해봤다'
tags:
  - Linux
  - Kernel
  - MCP
  - VSCode
  - AI
private: false
updated_at: '2025-11-27'
id: null
organization_url_name: null
slide: false
---

# 들어가며

Linux 커널은 약 3,000만 줄의 C 코드로 구성된 거대한 프로젝트입니다. 그 구조를 이해하는 것은 쉽지 않습니다.

이 글에서는 **CodeGraph MCP Server**를 사용해, AI 코딩 어시스턴트(GitHub Copilot)와 연동하면서 Linux 커널 코드를 분석하는 방법을 소개합니다.

## 이 글에서 알 수 있는 것

- CodeGraph MCP로 Linux 커널을 인덱싱하는 방법
- VS Code + GitHub Copilot로 커널 코드에 대해 AI에게 질문하는 방법
- 실제 분석 예시(스케줄러, 프로세스 관리 등)

## 전제 조건

- Python 3.11 이상
- VS Code + GitHub Copilot
- Linux 커널 소스 코드

---

# 제1장 환경 구성

## 1.1 CodeGraph MCP 설치

```bash
# 가상 환경 생성
python -m venv .venv
source .venv/bin/activate

# CodeGraph MCP 설치
pip install codegraph-mcp-server

# 버전 확인(v0.7.1 이상에서 C 언어 지원)
codegraph-mcp --version
```

## 1.2 Linux 커널 소스 받기

```bash
# 1.2 Linux 커널 소스 받기
git clone --depth 1 https://github.com/torvalds/linux.git
cd linux
```

## 1.3 VS Code MCP 설정

`.vscode/settings.json`에 아래를 추가:

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

---

# 제2장 커널 인덱스 생성

## 2.1 부분 인덱스(추천)

커널 전체를 인덱싱하면 시간이 오래 걸리므로, 먼저 특정 서브시스템부터 시작하는 것을 추천합니다.

```bash
# kernel/ 디렉터리만 인덱싱
codegraph-mcp index ./kernel --full --no-community
```

**실행 결과:**

```
Indexed 54,748 entities, 142,532 relations in 5.77s
```

| 항목     | 값       |
| ------ | ------- |
| 파일 수   | 596     |
| 엔티티 수  | 54,748  |
| 릴레이션 수 | 142,532 |
| 처리 시간  | 5.77초   |

## 2.2 다른 서브시스템 예시

```bash
# 메모리 관리
codegraph-mcp index ./mm --full --no-community

# 파일 시스템
codegraph-mcp index ./fs --full --no-community

# 네트워크
codegraph-mcp index ./net --full --no-community

# 드라이버(대규모)
codegraph-mcp index ./drivers --full --no-community
```

## 2.3 전체 인덱스(상급자용)

커널 전체를 인덱싱하는 경우:

```bash
# 경고: 수분~10여 분 걸립니다
codegraph-mcp index . --full --no-community
```

> **주의**: 커뮤니티 검출(`--no-community`를 제거)을 활성화하면 시간이 더 걸립니다. 대규모 코드베이스에서는 비활성화를 추천합니다.

---

# 제3장 MCP 서버 설정

## 3.1 VS Code(GitHub Copilot)에서 설정

MCP 서버는 클라이언트(VS Code, Claude Desktop 등)가 자동으로 기동합니다. 수동으로 기동할 필요는 없습니다.

VS Code설정 （`.vscode/settings.json`）：

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

VS Code를 열고, GitHub Copilot을 사용할 수 있는 상태로 만듭니다.

## 3.2 수동으로 서버 기동(디버그·확인용)

### stdio 트랜스포트

MCP 클라이언트에서 직접 기동되는 방식입니다:

```bash
codegraph-mcp serve --repo /path/to/linux
```

### SSE(HTTP) 트랜스포트

여러 클라이언트에서 동시 접속하거나, 서버를 켜둔 채로 인덱스를 갱신하고 싶은 경우:

```bash
# SSE 서버 기동(기본 포트: 8080)
codegraph-mcp start --repo /path/to/linux

# 포트를 지정하는 경우
codegraph-mcp start --repo /path/to/linux --port 3000
```

서버가 기동되면 아래처럼 메시지가 표시됩니다:

```
Starting SSE server on http://0.0.0.0:8080
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

> **💡 힌트**: `serve`는 stdio 트랜스포트(MCP 클라이언트용), `start`는 SSE 트랜스포트(HTTP 서버)입니다.

## 3.3 서버 상태 확인

SSE 서버가 정상적으로 기동했는지 확인하려면:

```bash
# 헬스 체크
curl http://localhost:8080/health

# 정상 응답
{"status":"ok"}
```

다른 터미널에서도 확인할 수 있습니다:

```bash
# 프로세스 확인
ps aux | grep codegraph-mcp

# 포트 확인
lsof -i :8080
# 또는
ss -tlnp | grep 8080
```

## 3.4 서버 종료

### 포그라운드에서 기동 중인 경우

```bash
# Ctrl+C로 종료
^C
INFO:     Shutting down
INFO:     Finished server process
```

### 백그라운드에서 기동 중인 경우

```bash
# 프로세스 ID 확인 후 종료
pkill -f "codegraph-mcp start"

# 또는 특정 포트를 사용하는 프로세스를 종료
kill $(lsof -t -i:8080)
```

### systemd 서비스로 관리하는 경우(옵션)

장기 운영이 필요하면 systemd 서비스로 등록할 수도 있습니다:

```ini
# /etc/systemd/system/codegraph-mcp.service
[Unit]
Description=CodeGraph MCP Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/linux
ExecStart=/usr/local/bin/codegraph-mcp start --port 8080
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 관리
sudo systemctl start codegraph-mcp
sudo systemctl status codegraph-mcp
sudo systemctl stop codegraph-mcp
```

---

# 제4장 분석 예시

## 4.1 스케줄러 함수 찾기

**질문:**
```
Linux 커널의 스케줄러와 관련된 함수를 알려줘
```

**Copilot 답변(CodeGraph MCP 도구 사용):**

```
query_codebase 도구를 사용해 검색했습니다.

스케줄러 관련 주요 함수:
1. schedule() - kernel/sched/core.c:6847
   - 메인 스케줄링 함수
   
2. __schedule() - kernel/sched/core.c:6780
   - 실제 컨텍스트 스위치를 수행하는 내부 함수
   
3. scheduler_tick() - kernel/sched/core.c:5765
   - 타이머 인터럽트에서 호출됨
   
4. wake_up_process() - kernel/sched/core.c:4534
   - 프로세스를 깨움
   
5. try_to_wake_up() - kernel/sched/core.c:4234
   - wake_up_process의 내부 구현
```

## 4.2 fork 시스템 콜 구현 추적

**질문:**
```
fork 시스템 콜 구현을 추적해서, 관련 함수를 알려줘
```

**Copilot 답변:**

```
find_callers 와 find_callees 도구를 사용했습니다.

fork 호출 체인:
1. sys_fork() - kernel/fork.c
   └── kernel_clone()
       ├── copy_process()
       │   ├── dup_task_struct()
       │   ├── copy_files()
       │   ├── copy_fs()
       │   ├── copy_mm()
       │   └── copy_thread()
       └── wake_up_new_task()

합계 100개 이상의 관련 엔티티가 발견되었습니다.
```

## 4.3 특정 함수 소스 코드 가져오기

**질문:**
```
copy_process 함수 소스 코드를 보여줘
```

**Copilot 답변:**

```
get_code_snippet 도구를 사용했습니다.

// kernel/fork.c
static __latent_entropy struct task_struct *copy_process(
    struct pid *pid,
    int trace,
    int node,
    struct kernel_clone_args *args)
{
    int pidfd = -1, retval;
    struct task_struct *p;
    struct multiprocess_signals delayed;
    struct file *pidfile = NULL;
    const u64 clone_flags = args->flags;
    ...
}
```

## 4.4 의존 관계 분석

**질문:**
```
schedule 함수가 의존하는 함수를 알려줘
```

**Copilot 답변:**

```
find_dependencies 도구를 사용했습니다.

schedule() 의 의존 대상(깊이 2):
├── __schedule()
│   ├── pick_next_task()
│   ├── context_switch()
│   ├── update_rq_clock()
│   └── deactivate_task()
├── preempt_disable()
├── preempt_enable()
└── sched_submit_work()
```

## 4.5 프로젝트 구조 이해

**질문:**
```
kernel/ 디렉터리의 주요 컴포넌트를 설명해 줘
```

**Copilot 답변:**

```
analyze_module_structure 와 global_search 도구를 사용했습니다.

kernel/ 주요 컴포넌트:

1. **스케줄러** (kernel/sched/)
   - 프로세스 스케줄링
   - CFS, 리얼타임 스케줄러
   - CPU 부하 분산

2. **프로세스 관리** (kernel/fork.c, kernel/exit.c)
   - 프로세스 생성·종료
   - 시그널 처리

3. **시간 관리** (kernel/time/)
   - 타이머, 클럭
   - hrtimer, 타임키핑

4. **동기화 프리미티브** (kernel/locking/)
   - mutex, spinlock, rwlock
   - RCU

5. **인터럽트 처리** (kernel/irq/)
   - IRQ 관리
   - softirq, tasklet
```

---

# 제5장 실전 유스케이스

## 5.1 버그 조사

특정 함수를 변경했을 때 영향 범위를 조사:

```
mutex_lock 함수를 변경하면, 영향을 받는 코드는?
```

## 5.2 코드 리뷰 지원

새 패치가 어느 부분에 영향을 주는지 확인:

```
이 패치는 어떤 서브시스템에 영향을 주나요?
관련 테스트 파일이 있나요?
```

## 5.3 온보딩

커널 개발 초보가 구조를 이해:

```
메모리 할당자의 구조를 설명해 줘
주요 함수와, 그 함수들이 어떻게 호출되는지 알려줘
```

---

# 제6장 성능 팁

## 6.1 인덱스 전략

| 시나리오        | 추천 설정                    |
| ----------- | ------------------------ |
| 특정 서브시스템 분석 | 해당 디렉터리만 인덱싱             |
| 전체 구조 파악    | `--no-community`로 빠른 인덱싱 |
| 상세 클러스터 분석  | 커뮤니티 검출 활성화              |

## 6.2 쿼리 최적화

```python
# 효율적: 엔티티 타입으로 필터
query_codebase(query="scheduler", entity_types=["function"])

# 효율적: 부분 ID 검색
find_callers(entity_id="schedule")  # 풀패스 불필요

# 비효율: 너무 넓은 쿼리
query_codebase(query="kernel")  # 결과가 너무 많음
```

## 6.3 증분 인덱스

코드를 변경한 뒤에는 증분 인덱스로 빠르게 갱신:

```bash
# 변경 파일만 재인덱싱
codegraph-mcp index . 
```

---

# 제7장 마무리

## CodeGraph MCP 장점

1. **제로 구성**: pip install로 바로 사용 가능
2. **고속**: kernel/ 디렉터리를 6초 이하로 인덱싱
3. **AI 연동**: GitHub Copilot에서 직접 쿼리 가능
4. **C 언어 지원**: v0.7.1에서 Linux 커널 분석 가능

## 활용 씬

- 커널 해커의 코드 내비게이션
- 버그 조사 시 영향 범위 분석
- 신입 개발자 온보딩
- 코드 리뷰 효율화

## 링크

- **CodeGraph MCP GitHub**: https://github.com/gaebalai/CodeGraphMCPServer
- **PyPI**: https://pypi.org/project/codegraph-mcp-server/
- **Linux Kernel**: https://github.com/torvalds/linux

---

# 참고 자료

- [Linux Kernel Documentation](https://www.kernel.org/doc/html/latest/)
- [Model Context Protocol](https://spec.modelcontextprotocol.io/)
