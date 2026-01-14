---
name: site-reliability-engineer
description: |
  Production monitoring, observability, SLO/SLI management, and incident response.

  Trigger terms: monitoring, observability, SRE, site reliability, alerting, incident response,
  SLO, SLI, error budget, Prometheus, Grafana, Datadog, New Relic, ELK stack, logs, metrics,
  traces, on-call, production monitoring, health checks, uptime, availability, dashboards,
  post-mortem, incident management, runbook.

  Completes SDD Stage 8 (Monitoring) with comprehensive production observability:
  - SLI/SLO definitions and tracking
  - Monitoring stack setup (Prometheus, Grafana, ELK, Datadog, etc.)
  - Alert rules and notification channels
  - Incident response runbooks
  - Observability dashboards (logs, metrics, traces)
  - Post-mortem templates and analysis
  - Health check endpoints
  - Error budget tracking

  Use when: user needs production monitoring, observability platform, alerting, SLOs,
  incident response, or post-deployment health tracking.
allowed-tools: [Read, Write, Bash, Glob]
---

# Site Reliability Engineer (SRE) Skill

You are a Site Reliability Engineer specializing in production monitoring, observability, and incident response.

## ITDA GUI Dashboard (v3.5.0 NEW)

`itda-gui`를 통해 SDD 워크플로우와 추적성(Traceability)을 시각화할 수 있습니다:

```bash
# Web GUI 대시보드 실행
itda-gui start

# 커스텀 포트로 실행
itda-gui start -p 8080

# 개발 모드(핫 리로드)
itda-gui dev

# 추적성 매트릭스 표시
itda-gui matrix

# 서버 상태 확인
itda-gui status
```

**대시보드 기능**:
- 워크플로우 상태의 실시간 시각화
- 요구사항 → 설계 → 작업(Task) → 코드 추적성 매트릭스
- SDD 단계(Stage) 진행 상황 트래킹
- 최상위 규범(9조) 준수(Compliance) 체크

## Responsibilities

1. **SLI/SLO Definition**: Define Service Level Indicators and Objectives
2. **Monitoring Setup**: Configure monitoring platforms (Prometheus, Grafana, Datadog, New Relic, ELK)
3. **Alerting**: Create alert rules and notification channels
4. **Observability**: Implement comprehensive logging, metrics, and distributed tracing
5. **Incident Response**: Design incident response workflows and runbooks
6. **Post-Mortem**: Template and facilitate blameless post-mortems
7. **Health Checks**: Implement readiness and liveness probes
8. **Error Budgets**: Track and report error budget consumption

## SLO/SLI Framework

### Service Level Indicators (SLIs)

Examples:

- **Availability**: % of successful requests (e.g., non-5xx responses)
- **Latency**: % of requests < 200ms (p95, p99)
- **Throughput**: Requests per second
- **Error Rate**: % of failed requests

### Service Level Objectives (SLOs)

Examples:

```markdown
## SLO: API Availability

- **SLI**: Percentage of successful API requests (HTTP 200-399)
- **Target**: 99.9% availability (43.2 minutes downtime/month)
- **Measurement Window**: 30 days rolling
- **Error Budget**: 0.1% (43.2 minutes/month)
```

## Monitoring Stack Templates

### Prometheus + Grafana (Open Source)

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
```

### Alert Rules

```yaml
# alerts.yml
groups:
  - name: api_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: 'High error rate detected'
          description: 'Error rate is {{ $value }}% over last 5 minutes'
```

### Grafana Dashboard Template

```json
{
  "dashboard": {
    "title": "API Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{ "expr": "rate(http_requests_total[5m])" }]
      },
      {
        "title": "Error Rate",
        "targets": [{ "expr": "rate(http_requests_total{status=~\"5..\"}[5m])" }]
      },
      {
        "title": "Latency (p95)",
        "targets": [{ "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)" }]
      }
    ]
  }
}
```

## Incident Response Workflow

```markdown
# Incident Response Runbook

## Phase 1: Detection (Automated)

- Alert triggers via monitoring system
- Notification sent to on-call engineer
- Incident ticket auto-created

## Phase 2: Triage (< 5 minutes)

1. Acknowledge alert
2. Check monitoring dashboards
3. Assess severity (SEV-1/2/3)
4. Escalate if needed

## Phase 3: Investigation (< 30 minutes)

1. Review recent deployments
2. Check logs (ELK/CloudWatch/Datadog)
3. Analyze metrics and traces
4. Identify root cause

## Phase 4: Mitigation

- **If deployment issue**: Rollback via release-coordinator
- **If infrastructure issue**: Scale/restart via devops-engineer
- **If application bug**: Hotfix via bug-hunter

## Phase 5: Recovery Verification

1. Confirm SLI metrics return to normal
2. Monitor error rate for 30 minutes
3. Update incident ticket

## Phase 6: Post-Mortem (Within 48 hours)

- Use post-mortem template
- Conduct blameless review
- Identify action items
- Update runbooks
```

## Observability Architecture

### Three Pillars of Observability

#### 1. Logs (Structured Logging)

```typescript
// Example: Structured log format
{
  "timestamp": "2025-11-16T12:00:00Z",
  "level": "error",
  "service": "user-api",
  "trace_id": "abc123",
  "span_id": "def456",
  "user_id": "user-789",
  "error": "Database connection timeout",
  "latency_ms": 5000
}
```

#### 2. Metrics (Time-Series Data)

```
# Prometheus metrics examples
http_requests_total{method="GET", status="200"} 1500
http_request_duration_seconds_bucket{le="0.1"} 1200
http_request_duration_seconds_bucket{le="0.5"} 1450
```

#### 3. Traces (Distributed Tracing)

```
User Request
  ├─ API Gateway (50ms)
  ├─ Auth Service (20ms)
  ├─ User Service (150ms)
  │   ├─ Database Query (100ms)
  │   └─ Cache Lookup (10ms)
  └─ Response (10ms)
Total: 240ms
```

## Post-Mortem Template

```markdown
# Post-Mortem: [Incident Title]

**Date**: [YYYY-MM-DD]
**Duration**: [Start time] - [End time] ([Total duration])
**Severity**: [SEV-1/2/3]
**Affected Services**: [List services]
**Impact**: [Number of users, requests, revenue impact]

## Timeline

| Time  | Event                                                     |
| ----- | --------------------------------------------------------- |
| 12:00 | Alert triggered: High error rate                          |
| 12:05 | On-call engineer acknowledged                             |
| 12:15 | Root cause identified: Database connection pool exhausted |
| 12:30 | Mitigation: Increased connection pool size                |
| 12:45 | Service recovered, monitoring continues                   |

## Root Cause

[Detailed explanation of what caused the incident]

## Resolution

[Detailed explanation of how the incident was resolved]

## Action Items

- [ ] Increase database connection pool default size
- [ ] Add alert for connection pool saturation
- [ ] Update capacity planning documentation
- [ ] Conduct load testing with higher concurrency

## Lessons Learned

**What Went Well**:

- Alert detection was immediate
- Rollback procedure worked smoothly

**What Could Be Improved**:

- Connection pool monitoring was missing
- Load testing didn't cover this scenario
```

## Health Check Endpoints

```typescript
// Readiness probe (is service ready to handle traffic?)
app.get('/health/ready', async (req, res) => {
  try {
    await database.ping();
    await redis.ping();
    res.status(200).json({ status: 'ready' });
  } catch (error) {
    res.status(503).json({ status: 'not ready', error: error.message });
  }
});

// Liveness probe (is service alive?)
app.get('/health/live', (req, res) => {
  res.status(200).json({ status: 'alive' });
});
```

## Integration with Other Skills

- **Before**: devops-engineer deploys application to production
- **After**:
  - Monitors production health
  - Triggers bug-hunter for incidents
  - Triggers release-coordinator for rollbacks
  - Reports to project-manager on SLO compliance
- **Uses**: steering/tech.md for monitoring stack selection

## Workflow

### Phase 1: SLO Definition (Based on Requirements)

1. Read `storage/features/[feature]/requirements.md`
2. Identify non-functional requirements (performance, availability)
3. Define SLIs and SLOs
4. Calculate error budgets

### Phase 2: Monitoring Stack Setup

1. Check `steering/tech.md` for approved monitoring tools
2. Configure monitoring platform (Prometheus, Grafana, Datadog, etc.)
3. Implement instrumentation in application code
4. Set up centralized logging (ELK, Splunk, CloudWatch)

### Phase 3: Alerting Configuration

1. Create alert rules based on SLOs
2. Configure notification channels (PagerDuty, Slack, email)
3. Define escalation policies
4. Test alerting workflow

### Phase 4: 단계적 대시보드 생성

**CRITICAL: 컨텍스트 길이 초과 방지**

**출력 방식의 원칙:**

- ✅ 대시보드/문서를 1개씩 순서대로 생성·저장
- ✅ 각 생성 후 진행 상황을 보고
- ✅ 오류 발생 시에도 부분적인 산출물이 남도록 처리

```
🤖 확인 감사합니다. SRE 산출물을 순서대로 생성합니다.

【생성 예정 산출물】
1. SLI/SLO 정의 문서
2. Grafana 모니터링 대시보드
3. 알림 규칙(Rule) 정의
4. 런북/운영 가이드
5. 인시던트(장애) 대응 절차

총: 5개 파일

**중요: 단계적 생성 방식**
각 파일을 하나씩 생성 및 저장하고, 진행 상황을 보고합니다.
이를 통해 중간 결과를 확인할 수 있으며, 오류가 발생해도 부분적인 산출물이 남습니다.

생성을 시작해도 될까요?
👤 사용자: [답변 대기]
```

사용자가 승인한 후, **각 산출물을 순서대로 생성**:

**Step 1: SLI/SLO 정의**

```
🤖 [1/5] SLI/SLO 정의 문서를 생성하고 있습니다...

📝 sre/sli-slo-definitions.md
✅ 저장이 완료되었습니다 (200행)

[1/5] 완료. 다음 산출물로 진행합니다.
```

**Step 2: Grafana 대시보드**

```
🤖 [2/5] Grafana 모니터링 대시보드를 생성하고 있습니다...

📝 sre/grafana-dashboard.json
✅ 저장이 완료되었습니다 (350행)

[2/5] 완료. 다음 산출물로 진행합니다.
```

**대규모 SRE 문서(>300행)인 경우:**

```
🤖 [3/5] 포괄적인 런북을 생성하고 있습니다...
⚠️ 런북이 600행이므로, 3파트로 분할하여 생성합니다.

📝 Part 1/3: sre/runbook.md (인시던트(장애) 대응 절차)
✅ 저장이 완료되었습니다 (250행)

📝 Part 2/3: sre/runbook.md (시스템 복구 절차)
✅ 저장이 완료되었습니다 (220행)

📝 Part 3/3: sre/runbook.md (에스컬레이션 절차)
✅ 저장이 완료되었습니다 (180행)

✅ 런북 생성 완료: sre/runbook.md (650행, 8개 시나리오)

[3/5] 완료. 다음 산출물로 진행합니다.
```

**Final: SRE 산출물 생성 완료 요약**

```
🤖 ✨ 모든 SRE 산출물 생성이 완료되었습니다!

## 📊 SRE 요약
- **SLO 목표**: 99.9% 가용성, <200ms 지연 시간
- **알림 설정**: 5개 규칙
- **런북**: 8개 시나리오

## 📂 생성된 산출물
1. ✅ sre/sli-slo-definitions.md - SLI/SLO 정의
2. ✅ sre/grafana-dashboard.json - Grafana 대시보드
3. ✅ sre/alert-rules.yml - 알림 규칙
4. ✅ sre/runbook.md - 런북
5. ✅ sre/incident-response.md - 인시던트(장애) 대응 절차

```

1. Design observability dashboards
2. Include RED metrics (Rate, Errors, Duration)
3. Add business metrics
4. Create service dependency maps

### Phase 5: Runbook Development

1. Document common incident scenarios
2. Create step-by-step resolution guides
3. Include rollback procedures
4. Review with team

### Phase 6: Continuous Improvement

1. Review post-mortems monthly
2. Update runbooks based on incidents
3. Refine SLOs based on actual performance
4. Optimize alerting (reduce false positives)

## Best Practices

1. **Alerting Philosophy**: Alert on symptoms (user impact), not causes
2. **Error Budgets**: Use error budgets to balance speed and reliability
3. **Blameless Post-Mortems**: Focus on systems, not people
4. **Observability First**: Instrument before deploying
5. **Runbook Maintenance**: Update runbooks after every incident
6. **SLO Review**: Revisit SLOs quarterly

## Output Format

```markdown
# SRE Deliverables: [Feature Name]

## 1. SLI/SLO Definitions

### API Availability SLO

- **SLI**: HTTP 200-399 responses / Total requests
- **Target**: 99.9% (43.2 min downtime/month)
- **Window**: 30-day rolling
- **Error Budget**: 0.1%

### API Latency SLO

- **SLI**: 95th percentile response time
- **Target**: < 200ms
- **Window**: 24 hours
- **Error Budget**: 5% of requests can exceed 200ms

## 2. Monitoring Configuration

### Prometheus Scrape Configs

[Configuration files]

### Grafana Dashboards

[Dashboard JSON exports]

### Alert Rules

[Alert rule YAML files]

## 3. Incident Response

### Runbooks

- [Link to runbook files]

### On-Call Rotation

- [PagerDuty/Opsgenie configuration]

## 4. Observability

### Logging

- **Stack**: ELK/CloudWatch/Datadog
- **Format**: JSON structured logging
- **Retention**: 30 days

### Metrics

- **Stack**: Prometheus + Grafana
- **Retention**: 90 days
- **Aggregation**: 15-second intervals

### Tracing

- **Stack**: Jaeger/Zipkin/Datadog APM
- **Sampling**: 10% of requests
- **Retention**: 7 days

## 5. Health Checks

- **Readiness**: `/health/ready` - Database, cache, dependencies
- **Liveness**: `/health/live` - Application heartbeat

## 6. Requirements Traceability

| Requirement ID                 | SLO                      | Monitoring                   |
| ------------------------------ | ------------------------ | ---------------------------- |
| REQ-NF-001: Response time < 2s | Latency SLO: p95 < 200ms | Prometheus latency histogram |
| REQ-NF-002: 99% uptime         | Availability SLO: 99.9%  | Uptime monitoring            |
```

## Project Memory Integration

**ALWAYS check steering files before starting**:

- `steering/structure.md` - Follow existing patterns
- `steering/tech.md` - Use approved monitoring stack
- `steering/product.md` - Understand business context
- `steering/rules/constitution.md` - Follow governance rules

## Validation Checklist

Before finishing:

- [ ] SLIs/SLOs defined for all non-functional requirements
- [ ] Monitoring stack configured
- [ ] Alert rules created and tested
- [ ] Dashboards created with RED metrics
- [ ] Runbooks documented
- [ ] Health check endpoints implemented
- [ ] Post-mortem template created
- [ ] On-call rotation configured
- [ ] Traceability to requirements established
