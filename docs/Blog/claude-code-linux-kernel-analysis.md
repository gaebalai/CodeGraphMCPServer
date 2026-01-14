---
title: 'Claude Code + CodeGraph MCP로 Linux 커널 코드 분석하기'
tags:
  - Linux
  - Kernel
  - MCP
  - ClaudeCode
  - AI
private: false
updated_at: '2025-11-27'
id: null
organization_url_name: null
slide: false
---

# 들어가며

Linux 커널은 약 3,000만 줄의 C 코드로 구성된 세계 최대급 오픈소스 프로젝트입니다. 그 구조를 이해하는 일은 숙련된 개발자에게도 쉽지 않습니다.

이 글에서는 **Claude Code**(Anthropic사의 AI 코딩 에이전트)와 **CodeGraph MCP Server**를 조합해 Linux 커널 코드를 효율적으로 분석하는 방법을 소개합니다.

## 이 글에서 알 수 있는 것

- Claude Code에서 MCP 서버를 설정하는 방법
- CodeGraph MCP로 Linux 커널을 인덱싱하는 방법
- Claude Code를 활용한 커널 코드 분석의 실전 예시

## 전제 조건

- Python 3.11 이상
- Claude Code(`claude` CLI 커맨드)
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

# 버전 확인(v0.7.1 이후 C 언어 지원)
codegraph-mcp --version
```

## 1.2 Linux 커널 소스 받기

```bash
# 커널 소스를 클론(shallow clone으로 속도 개선)
git clone --depth 1 https://github.com/torvalds/linux.git
cd linux
```

## 1.3 Claude Code MCP 설정

### 방법1: CLI 커맨드로 추가(권장)

**stdio 트랜스포트(프로세스 직접 기동):**

```bash
claude mcp add codegraph -- codegraph-mcp serve --repo /path/to/linux
```

**HTTP 트랜스포트(SSE 서버 경유):**

먼저 별도 터미널에서 SSE 서버를 기동:

```bash
cd /path/to/linux
codegraph-mcp start --port 8080
```

그 다음 Claude Code에 추가:

```bash
claude mcp add --transport http codegraph http://0.0.0.0:8080
```

> **💡 힌트**: HTTP 트랜스포트는 여러 클라이언트가 동시에 접속할 수 있고, 서버를 켜둔 상태로 인덱스를 갱신할 수 있습니다.

### 방법2: 설정 파일로 추가

Claude Code 설정 파일 `~/.claude/claude_desktop_config.json`을 편집:

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "/path/to/linux"]
    }
  }
}
```

또는 프로젝트별 설정 `.mcp.json`：

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph-mcp",
      "args": ["serve", "--repo", "."]
    }
  }
}
```

---

# 제2장 커널 인덱스 생성

## 2.1 부분 인덱스(권장)

커널 전체는 너무 크기 때문에, 먼저 특정 서브시스템부터 시작합니다.

```bash
# kernel/ 디렉터리만 인덱싱
cd /path/to/linux
codegraph-mcp index ./kernel --full --no-community
```

**실행 결과:**

```
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Metric        ┃ Value         ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Entities      │ 54,748        │
│ Relations     │ 142,532       │
│ Files Indexed │ 596           │
│ Files Skipped │ 0             │
│ Duration      │ 5.77s         │
└───────────────┴───────────────┘

Indexing completed successfully!
```

## 2.2 다른 서브시스템

```bash
# 메모리 관리
codegraph-mcp index ./mm --full --no-community

# 파일 시스템
codegraph-mcp index ./fs --full --no-community

# 네트워크
codegraph-mcp index ./net --full --no-community
```

> **💡 힌트**: `--no-community`옵션으로 커뮤니티 검출을 스킵하면 인덱싱 속도가 빨라집니다.

---

# 제3장 Claude Code로 분석하기

## 3.1 Claude Code 실행

```bash
cd /path/to/linux
claude
```

Claude Code가 실행되면, 자동으로 CodeGraph MCP 서버가 기동되고 인덱싱된 코드 그래프를 사용할 수 있게 됩니다.

## 3.2 분석 예시1: 스케줄러 구조 이해하기

**프롬프트:**
```
Linux 커널 스케줄러의 주요 함수와 그 관계를 말해.
```

**Claude Code의 답변:**

```
codegraph에서 Linux 커널 스케줄러에 대한 주요 함수를 검색한 결과를 요약합니다.

## Linux 커널 스케줄러 관련 함수 (codegraph 검색 결과)

### 코어 스케줄러 (kernel/sched/core.c)

| 함수 이름 | 위치 | 설명 |
|--------------------|-------------|------------------|
| try_to_wake_up | core.c:4143 | 작업을 일으키는 |
| enqueue_task | core.c:2080 | 작업을 큐에 추가 |
| dequeue_task | core.c:2106 | 작업을 큐에서 제거 |
| pick_next_task | core.c:5986 | 다음에 수행할 작업 선택 |
| sched_core_enqueue | core.c:298 | 핵심 스케줄링 대기열 |
| sched_core_dequeue | core.c:311 | 코어 스케줄링 디큐 |
| prio_less | core.c:219 | 우선 순위 비교 |
| __task_prio | core.c:191 | 작업 우선 순위 획득 |

### CFS (Completely Fair Scheduler) (kernel/sched/fair.c)

| 함수 이름 | 위치 | 설명 |
|-------------------------|----------------|---------------|
| enqueue_task_fair | fair.c:6917 | CFS 런큐에 추가 |
| dequeue_task_fair | fair.c:7161 | CFS 런큐에서 삭제 |
| calc_delta_fair | fair.c:290 | 공정한 실행 시간 계산 |
| update_load_add/sub/set | fair.c:165-177 | 로드 업데이트 |
| list_add_leaf_cfs_rq | fair.c:310 | CFS rq 목록 조작 |

### 실시간 스케줄러 (kernel/sched/rt.c)

| 함수 이름 | 위치 | 설명 |
|-----------------------||-----------|----------------|
| enqueue_task_rt | rt.c:1430 | RT 작업 추가 |
| dequeue_task_rt | rt.c:1450 | RT 작업 삭제 |
| init_rt_rq | rt.c:68 | RT 런큐 초기화 |
| sched_rt_period_timer | rt.c:101 | RT 스케줄러 주기 타이머 |
| init_rt_bandwidth | rt.c:125 | RT 대역폭 초기화 |

### 데드라인 스케줄러 (kernel/sched/deadline.c)

| 함수 이름 | 위치 | 설명 |
|-----------------|-----------------|----------|
| enqueue_task_dl | deadline.c:2054 | DL 태스크 추가 |
| dequeue_task_dl | deadline.c:2114 | DL 작업 삭제 |

### sched_ext (BPF 확장 스케줄러) (kernel/sched/ext.c)

| 함수 이름 | 위치 | 설명 |
|------------------|------------|------------|
| enqueue_task_scx | ext.c:1334 | SCX 태스크 추가 |
| dequeue_task_scx | ext.c:1430 | SCX 태스크 삭제 |
| do_enqueue_task | ext.c:1215 | 작업 대기열 실행 |

### 통계 · PSI (kernel/sched/stats.h)

| 함수 이름 | 위치 | 설명 |
|--------------------|-------------|---------------|
| psi_enqueue | stats.h:130 | PSI 대기열 처리 |
| psi_dequeue | stats.h:169 | PSI 디큐 처리 |
| psi_sched_switch | stats.h:213 | PSI 컨텍스트 스위치 |
| sched_info_arrive | stats.h:263 | 일정 정보 도착 |
| sched_info_enqueue | stats.h:289 | 스케줄 정보 대기열 |

더 자세한 검색을 하려면:
codegraph-mcp query "<키워드>" --format text
```

## 3.3 분석 예시2: 시스템 콜 구현 추적

**프롬프트:**
```
fork 시스템 호출 구현을 추적하여 주요 함수 호출 계층 구조를 보여줍니다.
```

**Claude Code의 답변:**

```
Linux 커널 fork 시스템 호출 호출 계층 구조

User Space
    │
    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  SYSCALL_DEFINE0(fork)                         [kernel/fork.c:2689]          │
│  SYSCALL_DEFINE0(vfork)                        [kernel/fork.c:2705]          │
│  SYSCALL_DEFINE5(clone, ...)                   [kernel/fork.c:2718-2738]     │
│  SYSCALL_DEFINE2(clone3, ...)                  [kernel/fork.c:2890]          │
└──────────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  kernel_clone(struct kernel_clone_args *args)  [kernel/fork.c:2568]          │
│    ├─ ptrace_event_enabled() - ptrace 이벤트 판정                           │
│    ├─ copy_process() ─────────────────┐                                      │
│    ├─ trace_sched_process_fork()      │                                      │
│    ├─ get_task_pid()                  │                                      │
│    ├─ wake_up_new_task() ────────┐    │                                      │
│    └─ wait_for_vfork_done()      │    │                                      │
└──────────────────────────────────┼────┼──────────────────────────────────────┘
                                   │    │
                    ┌──────────────┘    │
                    ▼                   │
┌─────────────────────────────────┐     │
│  wake_up_new_task()             │     │
│  [kernel/sched/core.c:4813]     │     │
│    ├─ __set_task_cpu()          │     │
│    ├─ select_task_rq()          │     │
│    ├─ activate_task()           │     │
│    │    └─ enqueue_task()       │     │
│    ├─ wakeup_preempt()          │     │
│    └─ task_woken() callback     │     │
└─────────────────────────────────┘     │
                                        │
         ┌──────────────────────────────┘
         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  copy_process()                                [kernel/fork.c:1926]          │
│  (프로세스 복제의 핵심 함수)                                                          │
│                                                                              │
│  1. 플래그 검증                                                                 │
│     ├─ CLONE_NEWNS, CLONE_FS, CLONE_THREAD등의 조합 체크                        │
│                                                                              │
│  2. 태스크(task) 구조체 복제                                                   │
│     └─ dup_task_struct()              [kernel/fork.c:866]                    │
│          ├─ alloc_task_struct_node() - task_struct 메모리 할당                 │
│          ├─ arch_dup_task_struct() - 아키텍처 의존 복사                         │
│          ├─ alloc_thread_stack_node() - 스택 할당                               │
│          └─ setup_thread_stack() - 스택 설정                               │
│                                                                              │
│  3. 자격(credential) 정보 복사                                                  │
│     └─ copy_creds()                   [kernel/cred.c]                        │
│                                                                              │
│  4. 스케줄러 초기화                                                            │
│     └─ sched_fork()                   [kernel/sched/core.c:4678]             │
│          ├─ __sched_fork() - 스케줄링 데이터 초기화                       │
│          ├─ p->__state = TASK_NEW                                            │
│          ├─ uclamp_fork()                                                    │
│          ├─ sched_class 設定 (rt/fair/ext)                                   │
│          └─ init_entity_runnable_average()                                   │
│                                                                              │
│  5. 각종 리소스 복사                                                           │
│     ├─ copy_files()                   [kernel/fork.c:1573] - fd 테이블        │
│     ├─ copy_fs()                      [kernel/fork.c:1552] - 파일 시스템       │
│     ├─ copy_sighand()                 [kernel/fork.c:1603] - 시그널 핸들러      │
│     ├─ copy_signal()                  [kernel/fork.c:1652] - 시그널 정보        │
│     ├─ copy_mm()                      [kernel/fork.c:1514] - 메모리 공간        │
│     │    └─ dup_mm() → dup_mmap() (CLONE_VM이 없는 경우)                       │
│     ├─ copy_namespaces()              [kernel/nsproxy.c] - 네임스페이스         │
│     ├─ copy_io()                      [block/blk-ioc.c] - I/O 컨텍스트          │
│     └─ copy_thread()                  [arch 의존] - 레지스터/스레드 정보         │
│                                                                              │
│  6. PID 할당                                                               │
│     └─ alloc_pid()                    [kernel/pid.c]                         │
│                                                                              │
│  7. cgroup 처리                                                               │
│     ├─ cgroup_can_fork()                                                     │
│     └─ sched_cgroup_fork()            [kernel/sched/core.c:4748]             │
│                                                                              │
│  8. 프로세스 트리에 추가                                                       │
│     ├─ klp_copy_process() - 라이브 패치(Live Patch)                            │
│     ├─ sched_core_fork()                                                     │
│     ├─ init_task_pid() - PID 설정                                            │
│     ├─ attach_pid() - PID 해시 등록                                           │
│     └─ list_add_tail() - 부모/자식/형제 리스트 추가                                 │
│                                                                              │
│  9. 후처리                                                                    │
│     ├─ sched_post_fork()                                                     │
│     ├─ cgroup_post_fork()                                                    │
│     └─ perf_event_fork()                                                     │
└──────────────────────────────────────────────────────────────────────────────┘

## 주요 함수의 위치

| 함수 이름 | 파일 | 행 번호 |
|-------------------------|---------------------|-----------|
| SYSCALL_DEFINE0(fork)   | kernel/fork.c       | 2689      |
| SYSCALL_DEFINE0(vfork)  | kernel/fork.c       | 2705      |
| SYSCALL_DEFINE5(clone)  | kernel/fork.c       | 2718-2738 |
| SYSCALL_DEFINE2(clone3) | kernel/fork.c       | 2890      |
| kernel_clone()          | kernel/fork.c       | 2568      |
| copy_process()          | kernel/fork.c       | 1926      |
| dup_task_struct()       | kernel/fork.c       | 866       |
| copy_mm()               | kernel/fork.c       | 1514      |
| copy_files()            | kernel/fork.c       | 1573      |
| copy_fs()               | kernel/fork.c       | 1552      |
| copy_sighand()          | kernel/fork.c       | 1603      |
| copy_signal()           | kernel/fork.c       | 1652      |
| sched_fork()            | kernel/sched/core.c | 4678      |
| sched_cgroup_fork()     | kernel/sched/core.c | 4748      |
| wake_up_new_task()      | kernel/sched/core.c | 4813      |
```

## 3.4 분석 예시3: 특정 함수의 영향 범위

**프롬프트:**
```
mutex_lock 함수를 변경하면 어떤 코드에 영향이 있습니까?
```

**Claude Code의 답변:**

```
mutex_lock 변경의 영향 범위

## 영향 개요

mutex_lock()은 Linux 커널 전체에서 23,243곳에서 사용되고 있으며,
관련 API 전체 기준으로는 54,047곳에 영향을 줍니다.

## 구현 파일

| 파일                           | 행 번호 | 설정                 |
|--------------------------------|--------|----------------------|
| kernel/locking/mutex.c         | 269    | 일반 (비 PREEMPT_RT) |
| kernel/locking/rtmutex_api.c   | 601    | PREEMPT_RT           |

## mutex_lock() 내부 호출

mutex_lock(lock)
    │
    ├─ might_sleep()           // 슬립 가능성 체크
    │
    └─ __mutex_trylock_fast()  [mutex.c:150] - 패스트패스(빠른 경로)
         │
         ├─ 성공 → 즉시 반환
         │
         └─ 실패 → __mutex_lock_slowpath() [mutex.c:1047]
                    └─ __mutex_lock() → 스핀/슬립 대기

## 서브시스템별 사용 위치

| 서브시스템 | 사용 위치 수 | 주요 영향 영역          |
|-----------|-------------|-------------------------|
| drivers/  | 18,499      | 디바이스 드라이버 전반  |
| fs/       | 1,078       | 파일 시스템             |
| net/      | 823         | 네트워크 스택           |
| kernel/   | 708         | 코어 기능               |
| arch/     | 701         | 아키텍처 의존 코드      |
| sound/    | 686         | 오디오 서브시스템       |
| mm/       | 124         | 메모리 관리             |
| block/    | 110         | 블록 디바이스           |

## drivers/ 내부 상세

| 서브디렉터리           | 사용 위치 수 |
|---------------------|-------|
| drivers/net/        | 3,830 |
| drivers/gpu/        | 2,450 |
| drivers/media/      | 1,607 |
| drivers/iio/        | 895   |
| drivers/hwmon/      | 808   |
| drivers/usb/        | 720   |
| drivers/infiniband/ | 565   |
| drivers/scsi/       | 512   |

## kernel/ 내부 상세

| 서브디렉터리          | 사용 위치 수 |
|--------------------|-------|
| kernel/trace/      | 196   |
| kernel/bpf/        | 64    |
| kernel/locking/    | 62    |
| kernel/events/     | 49    |
| kernel/workqueue.c | 47    |
| kernel/sched/      | 31    |
| kernel/cgroup/     | 29    |

## 관련 API (동시에 영향을 받을 가능성)

| API                         | 사용 위치 수 |
|-----------------------------|-------------|
| mutex_lock()                | 23,243      |
| mutex_unlock()              | ~23,000     |
| mutex_lock_nested()         | 약 600      |
| mutex_lock_interruptible()  | 약 400      |
| mutex_lock_killable()       | 약 100      |
| mutex_trylock()             | 약 3,500    |

## 변경 시 주의사항

1. CONFIG_PREEMPT_RT: RT 커널에서는 rtmutex 기반 구현을 사용
2. CONFIG_DEBUG_LOCK_ALLOC: 디버그 시 mutex_lock_nested()로 매크로 확장
3. 슬립 가능 컨텍스트: might_sleep()로 아토믹 컨텍스트에서의 사용을 탐지
4. lockdep: 데드락 탐지를 위한 의존 관계 추적

## 테스트 권장 범위

변경 내용에 따라:
- 전체 드라이버 스트레스 테스트
- 파일 시스템 I/O 테스트
- 네트워크 부하 테스트
- 스케줄러/코어 스트레스 테스트
- lockdep를 활성화한 빌드 및 테스트
```

## 3.5 분석 예제 4: 코드 스니펫 가져오기

**프롬프트:**
```
context_switch 함수의 소스 코드를 보여줘
```

**Claude Code의 답변:**

```
context_switch 함수의 소스 코드

파일: kernel/sched/core.c:5269-5329

context_switch(struct rq *rq, struct task_struct *prev,
             struct task_struct *next, struct rq_flags *rf)
{
      prepare_task_switch(rq, prev, next);

      /*
       * For paravirt, this is coupled with an exit in switch_to to
       * combine the page table reload and the switch backend into
       * one hypercall.
       */
      arch_start_context_switch(prev);

      /*
       * kernel -> kernel   lazy + transfer active
       *   user -> kernel   lazy + mmgrab_lazy_tlb() active
       *
       * kernel ->   user   switch + mmdrop_lazy_tlb() active
       *   user ->   user   switch
       *
       * switch_mm_cid() needs to be updated if the barriers provided
       * by context_switch() are modified.
       */
      if (!next->mm) {                                // to kernel
              enter_lazy_tlb(prev->active_mm, next);

              next->active_mm = prev->active_mm;
              if (prev->mm)                           // from user
                      mmgrab_lazy_tlb(prev->active_mm);
              else
                      prev->active_mm = NULL;
      } else {                                        // to user
              membarrier_switch_mm(rq, prev->active_mm, next->mm);
              /*
               * sys_membarrier() requires an smp_mb() between setting
               * rq->curr / membarrier_switch_mm() and returning to userspace.
               *
               * The below provides this either through switch_mm(), or in
               * case 'prev->active_mm == next->mm' through
               * finish_task_switch()'s mmdrop().
               */
              switch_mm_irqs_off(prev->active_mm, next->mm, next);
              lru_gen_use_mm(next->mm);

              if (!prev->mm) {                        // from kernel
                      /* will mmdrop_lazy_tlb() in finish_task_switch(). */
                      rq->prev_mm = prev->active_mm;
                      prev->active_mm = NULL;
              }
      }

      /* switch_mm_cid() requires the memory barriers above. */
      switch_mm_cid(rq, prev, next);

      prepare_lock_switch(rq, next, rf);

      /* Here we just switch the register state and the stack. */
      switch_to(prev, next, prev);
      barrier();

      return finish_task_switch(prev);
}

---
## 관련 함수

### prepare_task_switch (core.c:5117-5129)

static inline void
prepare_task_switch(struct rq *rq, struct task_struct *prev,
                  struct task_struct *next)
{
      kcov_prepare_switch(prev);
      sched_info_switch(rq, prev, next);
      perf_event_task_sched_out(prev, next);
      rseq_preempt(prev);
      fire_sched_out_preempt_notifiers(prev, next);
      kmap_local_sched_out();
      prepare_task(next);
      prepare_arch_switch(next);
}

### finish_task_switch (core.c:5150-5232)

static struct rq *finish_task_switch(struct task_struct *prev)
      __releases(rq->lock)
{
      struct rq *rq = this_rq();
      struct mm_struct *mm = rq->prev_mm;
      unsigned int prev_state;

      /* preempt_count チェック */
      if (WARN_ONCE(preempt_count() != 2*PREEMPT_DISABLE_OFFSET,
                    "corrupted preempt_count: %s/%d/0x%x\n",
                    current->comm, current->pid, preempt_count()))
              preempt_count_set(FORK_PREEMPT_COUNT);

      rq->prev_mm = NULL;

      prev_state = READ_ONCE(prev->__state);
      vtime_task_switch(prev);
      perf_event_task_sched_in(prev, current);
      finish_task(prev);
      tick_nohz_task_switch();
      finish_lock_switch(rq);
      finish_arch_post_lock_switch();
      kcov_finish_switch(current);
      kmap_local_sched_in();

      fire_sched_in_preempt_notifiers(current);

      if (mm) {
              membarrier_mm_sync_core_before_usermode(mm);
              mmdrop_lazy_tlb_sched(mm);
      }

      if (unlikely(prev_state == TASK_DEAD)) {
              if (prev->sched_class->task_dead)
                      prev->sched_class->task_dead(prev);

              put_task_stack(prev);
              put_task_struct_rcu_user(prev);
      }

      return rq;
}

---
## 호출 흐름

__schedule() [core.c:6929]
    │
    ▼
context_switch(rq, prev, next, &rf)
    │
    ├─ prepare_task_switch()
    │     ├─ kcov_prepare_switch()
    │     ├─ sched_info_switch()
    │     ├─ perf_event_task_sched_out()
    │     ├─ rseq_preempt()
    │     ├─ fire_sched_out_preempt_notifiers()
    │     ├─ kmap_local_sched_out()
    │     ├─ prepare_task()
    │     └─ prepare_arch_switch()
    │
    ├─ arch_start_context_switch()
    │
    ├─ [메모리 공간 전환]
    │     ├─ next->mm == NULL (커널 스레드로)
    │     │     ├─ enter_lazy_tlb()
    │     │     └─ mmgrab_lazy_tlb() (사용자 공간에서 온 경우)
    │     │
    │     └─ next->mm != NULL (사용자 프로세스로)
    │           ├─ membarrier_switch_mm()
    │           ├─ switch_mm_irqs_off()  ← 페이지 테이블 전환
    │           └─ lru_gen_use_mm()
    │
    ├─ switch_mm_cid()
    │
    ├─ prepare_lock_switch()
    │
    ├─ switch_to(prev, next, prev)  ← 레지스터/스택 전환 (아키텍처 의존)
    │
    ├─ barrier()
    │
    └─ finish_task_switch(prev)
          ├─ vtime_task_switch()
          ├─ perf_event_task_sched_in()
          ├─ finish_task()
          ├─ tick_nohz_task_switch()
          ├─ finish_lock_switch()
          ├─ finish_arch_post_lock_switch()
          ├─ kcov_finish_switch()
          ├─ kmap_local_sched_in()
          ├─ fire_sched_in_preempt_notifiers()
          ├─ mmdrop_lazy_tlb_sched() (必要な場合)
          └─ [TASK_DEAD処理] (タスク終了時)

## 메모리 공간 전환의 4가지 패턴

| From   | To     | 처리 내용                         |
| ------ | ------ | ----------------------------- |
| kernel | kernel | lazy TLB + active_mm 전달       |
| user   | kernel | lazy TLB + mmgrab_lazy_tlb()  |
| kernel | user   | switch_mm + mmdrop_lazy_tlb() |
| user   | user   | switch_mm                     |
```

---

# 제4장 실전 유스케이스

## 4.1 버그 조사

특정 패닉이나 크래시의 원인을 조사할 때 활용합니다:

```
프롬프트: schedule_timeout 함수에서 타임아웃이
정상적으로 동작하지 않는 경우, 어떤 함수를 확인해야 할까?
```

## 4.2 패치 작성 지원

새 기능을 추가할 때 영향 범위를 확인합니다:

```
프롬프트: task_struct에 새로운 필드를
추가한 경우, 어떤 파일을 수정해야 할까?
```

## 4.3 코드 리뷰

제출된 패치에 대한 리뷰를 지원합니다:

```
프롬프트: 이 패치는 sched_entity 구조체를
변경하고 있는데, 영향을 받는 함수를 나열해줘
```

## 4.4 문서 생성

코드로부터 문서를 자동 생성합니다:

```
프롬프트: kernel/sched/ 디렉터리의
모듈 구조를 문서화해줘
```

---

# 제5장 Tips & 트러블슈팅

## 5.1 성능 최적화

| 상황 | 권장 설정 |
|------|-----------|
| 특정 서브시스템 분석 | 해당 디렉터리만 인덱싱 |
| 고속 인덱싱 | `--no-community` 옵션 |
| 메모리 절약 | 서브시스템 단위로 분할 인덱싱 |

## 5.2 자주 발생하는 문제

### MCP 서버가 기동되지 않는 경우

```bash
# 서버 수동 테스트
codegraph-mcp serve --repo /path/to/linux

# 로그 확인
cat ~/.codegraph/server.log
```

### 인덱스가 오래된 경우

```bash
# 증분 인덱싱으로 갱신
codegraph-mcp index /path/to/linux/kernel
```

### 메모리 부족

대규모 코드베이스에서는 서브시스템 단위로 인덱스를 생성합니다:

```bash
# 개별 인덱싱
codegraph-mcp index ./kernel --full --no-community
codegraph-mcp index ./mm --full --no-community
codegraph-mcp index ./fs --full --no-community
```

---

# 제6장 정리

## Claude Code + CodeGraph MCP의 장점

1. **자연어 기반 코드 분석**: 복잡한 grep 명령 불필요
2. **구조적 이해**: 함수 호출 관계를 자동으로 추적
3. **영향 범위 분석**: 변경에 따른 영향을 사전에 파악
4. **고속 처리**: 5만 개 엔티티를 6초 내 인덱싱
5. **제로 설정**: pip install만으로 즉시 사용 가능

## 활용 시나리오

- 커널 해커의 일상적인 코드 네비게이션
- 신규 개발자 온보딩
- 버그 조사 시 영향 범위 식별
- 패치 작성 및 리뷰 효율화

## 링크

- **CodeGraph MCP**: https://github.com/gaebalai/CodeGraphMCPServer
- **PyPI**: https://pypi.org/project/codegraph-mcp-server/
- **Claude Code**: https://claude.ai/code
- **Linux Kernel**: https://github.com/torvalds/linux

---

# 참고 자료

- [Linux Kernel Documentation](https://www.kernel.org/doc/html/latest/)
- [Model Context Protocol](https://spec.modelcontextprotocol.io/)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
