# One-Page PRD: CoreSight-G Platform

## 1. 개요
- 한 줄 요약: 온프레미스 GPU 서버(1~20대)와 서버 하드웨어를 하나의 관제 체계로 묶는 풀 관측성(메트릭·로그·트레이스·알림) 플랫폼. **Multi AI Agent 아키텍처(Orchestrator + Domain Agent 이중 구조)로 구현**하며, `CoreSight-G Platform` 를 기반 골격으로 사용한다.
- 배경 / 왜 지금 하는가: GPU 인프라(VRAM/utilization/ECC/XID)와 전통 서버 하드웨어(CPU/RAID/센서/BMC)는 모니터링 요구가 달라 분절된 도구로 운영되기 쉽고, 이는 장애 대응 지연과 SaaS 과금 누적으로 이어진다 (근거: `.docs/gpu_server_monitoring_scale_guide.md`, `.docs/enterprise_monitoring_roi_gpu_report.md`).
- 작성자 / 날짜 / 버전: bclim / 2026-07-22 / v0.2 (초안 — Multi AI Agent 아키텍처 요구 반영)

## 2. 문제와 대상 (Why & Who)
- 해결하려는 핵심 문제: GPU 계층과 서버 하드웨어 계층을 함께 보는 통합 관제 체계가 없다. GPU 장애 징후(XID·ECC·과열)와 하드웨어 장애(RAID degraded·PSU/팬 이상)를 각각 다른 도구·수작업으로 확인해 탐지와 원인 분석이 느리다.
- 비즈니스 관점 중요성: GPU 자원은 고가 자산 — 저활용(장기 10% 이하)·병목(VRAM 90%+)을 못 보면 자원 낭비, 장애를 늦게 보면 서비스 중단. 상용 SaaS(Datadog 호스트당 월 $15~, APM $31~)는 소규모에서도 기능 확장 시 과금이 누적된다.
- 근거 데이터 / VOC / 로그: `.docs/` 시장·ROI·규모별 가이드 4종 연구자료. `가정:` 사내 장애 로그·VOC 데이터는 아직 미수집 (Open Question).
- 타깃 사용자 / 페르소나: 인프라 운영자/SRE (1차), ML 엔지니어·연구자 (2차 — GPU 사용 현황 조회).
- 대표 사용 상황: 야간 GPU 노드 XID 오류 발생 → 알림 수신 → 대시보드에서 GPU·하드웨어·로그를 한 화면에서 상관 분석 → 노드 격리 판단.

## 3. 범위 (What — In / Out)
- 이번 릴리즈 핵심 기능 (P0/P1):

  | 우선순위 | 기능 |
  |---|---|
  | P0 | GPU 메트릭 수집: utilization, VRAM, temperature, power, ECC, XID (DCGM Exporter 또는 nvidia-smi/NVML 기반) |
  | P0 | 서버 하드웨어 메트릭 수집: CPU/메모리/디스크(SMART), RAID 상태, 팬/PSU/온도 센서, NIC 오류 |
  | P0 | 통합 대시보드: GPU + 하드웨어를 노드 단위 한 화면에서 상관 조회 |
  | P0 | 필수 알람: XID 즉시, ECC 증가, RAID degraded, 과열/팬 이상, VRAM 장기 고점, exporter 미수집 감지 |
  | P1 | 로그 수집·검색 (시스템 로그, GPU 드라이버/dmesg, BMC 이벤트) |
  | P1 | 트레이스 수집 (OpenTelemetry — 자체 수집 파이프라인 관측 및 향후 앱 계층 확장 대비) |
  | P0 | Multi AI Agent 기반 관제 어시스턴트: 자연어 질의 → Orchestrator 의도 분류 → 모니터링 Domain Agent(tool_use)가 메트릭·알람 조회 → SSE 스트리밍 응답 (`CoreSight-G Platform` 기반) |
  | P1 | Addon Agent 확장: 신규 관제 Agent(예: 로그 분석, 용량 계획)를 ZIP 핫 디플로이로 추가 |

- P2 확장 (Addon Agent — `.docs/` 연구자료 재검토 도출. 전부 `addon-agents/zip/` 규약 + `/status` 위젯 + intent 등록으로 구현):

  | 우선순위 | Addon Agent (key) | 기능 | 근거 (.docs) |
  |---|---|---|---|
  | P2-1 | 스토리지 진단 (storage-monitor) | 디스크 latency/IOPS, SMART/NVMe health, RAID 어레이 상세 조회·해석 | scale_guide 체크리스트 "Disk latency/IOPS·RAID degraded 필수", sw_hw_report 분류 1-스토리지 |
  | P2-2 | BMC/IPMI 이벤트 (bmc-monitor) | iDRAC/iLO/IPMI 이벤트·센서(팬·PSU·전압·온도) 조회, critical 이벤트 선제 대응 권고 | scale_guide "BMC/iDRAC/iLO event 권장", sw_hw_report 분류 1-관리보드 |
  | P2-3 | GPU 프로파일링 (gpu-profiler) | 고급 지표 — SM occupancy, Tensor pipe active, DRAM bandwidth, throttle reasons, PCIe/NVLink, MIG 단위 | ROI 보고서 수집 우선순위 2·3순위, 시장 보고서 고급 지표 + DCGM profiling 저오버헤드 |
  | P2-4 | 용량 계획·효율 (capacity-planner) | 저활용(장기 10%↓) 탐지, 추세 집계(장기 보존 계층), GPU efficiency 리포트, 카디널리티·저장 비용 거버넌스 | ROI 보고서 보존 전략·비용 최적화, 시장 보고서 로드맵 5단계 capacity planning·cost governance |
  | P2-5 | 이상 탐지 (anomaly-detector) | 메트릭·로그 기반 이상 탐지, 알람 노이즈 감소, 원인 분석 보조 | 시장 보고서 "AI/ML 이상 탐지·예측 = 핵심 차별점", sw_hw_report 분류 7 |
  | P2-6 | 네트워크 모니터링 (net-monitor) | NIC error/drop, 포트·대역폭 추이, SNMP 장비 상태 | scale_guide 체크리스트 "NIC error/drop 필수", sw_hw_report 분류 5 |
  | P2-7 | 워크로드 상관 (workload-correlator) | 프로세스/잡별 GPU 점유 ↔ 스케줄러(K8s/Slurm) 메타데이터 연계 분석 | scale_guide "GPU 노드/잡/파드 상관분석", GPU 목적 "프로세스별 원인 분석" |

  - P3 후보(보류): 합성 점검·RUM(분류 6 — 소규모 온프레미스 우선순위 낮음), SLO 리포팅(분류 7 — 이상 탐지 이후), 전원·환경 UPS/PDU(랙 센서 도입 시).

- 하지 않을 것 (Out of Scope):
  - Kubernetes 멀티클러스터·대규모(200대+) 지원 — 소규모 온프레미스(1~20대) 우선.
  - 상용 SaaS(Datadog/Dynatrace) 연동·이중화 — 오픈소스 스택 자체 운영.
  - APM 수준 애플리케이션 성능 분석 (계측 인프라는 P1 트레이스로 확보 — 앱 계층 분석은 범위 외).
  - ※ MIG/Tensor core 세부 메트릭은 v1.2 에서 Out of Scope → **P2-3(gpu-profiler)** 로 승격.
  - 자동 장애 조치(auto-remediation) — 알림·대응 정책 문서까지만.

## 4. 사용자 경험 (How — User Flow)
- 대표 시나리오 1: 운영자가 XID 오류 알림(메신저/메일)을 받고 → 대시보드에서 해당 노드의 GPU 상태·온도·전력·최근 로그를 한 화면에서 확인 → ECC 동반 증가 확인 시 노드 격리 및 티켓 발행.
- 대표 시나리오 2: ML 엔지니어가 주간 GPU 활용 대시보드에서 노드·프로세스별 VRAM/utilization 추이를 확인 → 저활용 노드에 잡 재배치.
- 대표 시나리오 3: 운영자가 관제 어시스턴트에 "어젯밤 node-03 GPU 온도 이상 원인 알려줘" 질의 → Orchestrator 가 의도 분류 후 GPU 모니터링 Agent·하드웨어 Agent 를 병렬 호출 → 메트릭·알람 이력을 tool_use 로 조회 → 종합 답변을 SSE 로 스트리밍.

## 5. 성공 지표 (Success — 비용지표 중심)
| KPI | 기준선(Baseline) | 목표값(Target) | 측정 방법 |
|---|---|---|---|
| 모니터링 TCO (라이선스+운영) | `가정:` SaaS 도입 시 호스트당 월 $15~46 상당 | 라이선스 $0 (오픈소스), 운영시간 주 4h 이내 | 월별 비용·운영시간 기록 |
| 메트릭 저장량/카디널리티 | 없음 (신규) | 1순위 메트릭 15s~30s 주기, 활성 시계열 노드당 상한 설정 후 준수율 95%+ | Prometheus TSDB 통계 |
| 데이터 보존 비용 | 없음 (신규) | 고해상도 단기(예: 15일) + 집계 장기 분리 계층 운영 | retention 설정·디스크 사용량 |
| 필수 메트릭 수집률 | 0% | GPU·HW 필수 항목 100% 노드 커버 | exporter up 메트릭 |
| MTTD (장애 탐지 시간) | `가정:` 수동 확인 — 수십 분~수 시간 | 필수 알람 항목 5분 이내 | 알람 발생~인지 시각 로그 |

## 6. 리스크 및 메모
- 주요 리스크:
  - 풀 관측성(로그·트레이스 포함) 범위가 소규모 인프라 대비 큼 — 메트릭(P0) 우선, 로그·트레이스(P1)는 단계 도입으로 완화.
  - 고카디널리티 라벨·고주기 수집 시 저장 비용 급증 — 수집 항목 1·2순위 계층화, 다운샘플링 정책 필수.
  - 자체 운영 오픈소스 스택은 운영 인건비가 ROI를 좌우 — 운영 자동화·표준 대시보드 재사용 전제.
- 의존성 (내부/외부): NVIDIA 드라이버·NVML/DCGM, 서버 BMC(IPMI/iDRAC/iLO) 접근 권한, 알림 채널(메신저/메일), 저장소 디스크 용량, `CoreSight-G Platform` 저장소(기반 골격), LLM Provider(Anthropic Claude API 키 또는 Ollama 로컬 모델).
- 규제·컴플라이언스 (업종: ICT/인프라 — `ict-saas` 베이스라인 제안): 감사로그·텔레메트리 보관/삭제 정책(내부통제), 접근통제(RBAC) — `가정:` 개인정보(PII)는 다루지 않음. ISMS-P 등 인증 대상 여부는 Open Question.
- 미결정 사항 (Open Questions):
  - 대상 서버 정확한 대수·GPU 모델(프로젝트명 4incGPU 의 "4" 의미 — GPU 4장 노드?).
  - 실행 환경: bare-metal/docker vs 단일 K8s (DCGM Exporter 배포 방식이 달라짐).
  - 로그·트레이스 스택 선택과 보존 기간 수치.
  - 사내 장애 이력 기준선 데이터 수집 여부.

---

## 7. 기술 메모 (Technical Notes — Multi AI Agent 아키텍처, 예시/초안)

참고 저장소: `/Users/wise/Developer/wise-project/Observability-4incGPU`
(근거 문서: 템플릿 `.docs/Multi AI Agent 아키텍처 가이드 v1.0.md`, `README.md`)

- **아키텍처 원칙 (템플릿 Phase 1 제약 준수)**:
  - Orchestrator + AI Assistant(Domain Agent) **이중 구조 고정** — 계층 추가 금지.
  - Orchestrator: ① Intent Classify → ② Parallel Route(asyncio.gather) → ③ Synthesize, SSE 이벤트 스트리밍.
  - Domain Agent: tool_use 루프 기반, 경량 모델(haiku 급) 사용.
  - Addon Agent: ZIP 핫 디플로이(importlib 동적 로드)로 도메인 Agent 확장.
  - **관제 Agent 배포 구조 (신규 요구, Iteration 16)**: Orchestrator·AI Assistant 외 모든 관제 Agent
    (GPU 모니터링·하드웨어 등)는 core 내장이 아닌 `addon-agents/zip/<agent>/` ZIP 구현체로 분리 관리.
    파일 규약: `<agent>-app.py` + `<agent>-meta.json` + `<agent>-worker-guide.md`(선택) + 패키징 `<agent>.zip`
    (참조: SeCuardian `addon-agents/zip` 구조).
  - **신규 관제 기능의 Addon-first 원칙 (신규 요구, Iteration 20~)**: P1 트레이스(OTel)부터 신규 관제
    조회·분석 기능은 core 라우터가 아닌 **Addon 에이전트 등록**으로 제공한다 (예: trace-monitor).
    core 에는 계측(OTel SDK 초기화)·인프라(compose 서비스)만 둔다.
- **관제 Domain Agent 후보 (예시/초안)**:

  | Agent | 역할 | 주요 tool |
  |---|---|---|
  | GPU Monitoring Agent | GPU 메트릭·XID/ECC 이력 조회, 이상 해석 | Prometheus 쿼리, 알람 이력 |
  | Hardware Agent | CPU/RAID/센서/BMC 상태 조회 | Prometheus/BMC 쿼리 |
  | Alert Agent | 알람 규칙 조회·요약, 대응 정책 안내 | Alertmanager API |
  | (P1 Addon) Log Analysis Agent | 로그 검색·이상 패턴 요약 | 로그 스토어 쿼리 |
- **기술 스택 (템플릿 준용)**: FastAPI + Python 3.12 + uv / Vite + React 19 + TS + Tailwind v4 / SQLite(local)→PostgreSQL 17 + Redis 7.4 / LLM: Claude(primary) + Ollama(local fallback), LiteLLM 게이트웨이 / Docker Compose → K8s + Helm.
- **관측 데이터 계층 (확정·구현됨)**: Prometheus v3.9 (scrape 15s, retention 15d) + 알람 규칙 7종.
  로컬 개발은 mock exporter(GPU 4장 DCGM 메트릭 시뮬레이션), 운영 전환 시 실제 DCGM Exporter/node_exporter 로 교체.
  조회 API `/api/metrics/{gpu,hardware,alerts,query}` (read-only).
- **비기능**: RBAC 3계층(Supervisor→Administrator→User/Viewer), JWT 인증, SSE 실시간 스트리밍, LLM API Key 인증(운영). `가정:` 온프레미스 폐쇄망일 경우 Ollama 단독 운용 가능해야 함 (Open Question).
- **리스크/트레이드오프**: LLM 호출 비용은 성공지표(TCO)에 포함해 통제 — 의도 분류·요약은 경량 모델 우선. 관제 어시스턴트는 조회(read-only) tool 만 제공, 노드 격리 등 조치 실행은 Out of Scope.

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|------|------|------|
| 2026-07-22 | v0.1 | 최초 초안 (설문 + `.docs/` 연구자료 기반) |
| 2026-07-22 | v0.2 | Multi AI Agent 아키텍처 요구 반영 (Wise-MultiAIAgent-Template 기반, §7 신설) |
| 2026-07-22 | v0.3 | 프로젝트명 CoreSight-G Platform 확정. Example Agent(board) 제거. Iteration 14 구현 반영 — 관측 데이터 계층(Prometheus+mock exporter) 확정, 필수 알람 규칙 7종, 메트릭 조회 API, GPU 모니터링·하드웨어 Domain Agent (§3 P0 中 메트릭 수집·알람 규칙·관제 어시스턴트 1차 구현. 통합 대시보드·알림 채널 연동은 잔여) |
| 2026-07-22 | v0.4 | Iteration 15 — 통합 관제 대시보드 구현(P0): `/dashboard` (활성 알람 배너 + GPU 카드/스파크라인 + HW 노드 테이블, 15s 폴링, 기본 진입 라우트), `GET /api/metrics/gpu/history`. 에이전트 관리 화면 nav_group(기본/관제 Agent) 섹션 분리. **신규 요구 접수**: 관제 Agent 구현체를 `addon-agents/zip/` ZIP 으로 분리 관리(§7 반영, Iteration 16 대상). P0 잔여: 알림 채널 연동 |
| 2026-07-22 | v0.5 | Iteration 16 — 관제 Agent 배포 구조 구현 완료: GPU 모니터링·하드웨어 Agent 구현체를 `addon-agents/zip/{gpu-monitor,hw-monitor}/` 로 이전 (app.py `router`+`_TOOLS`+`TOOL_EXECUTORS`+`SYSTEM_PROMPT` 규약, meta.json, 가이드, zip 패키징). core 는 Orchestrator·AI Assistant·범용 AddonToolAgent 프록시만 유지. P0 잔여: 알림 채널 연동 |
| 2026-07-22 | v0.6 | Iteration 17·18 — **P0 전체 완료**. ⑰ 화면 없는 addon 사이드바 노출 버그 수정(has_front 필터). ⑱ 알림 채널: Alertmanager(9093) → `POST /api/alerts/webhook`(Bearer 토큰) → `tbl_alert_history` 저장 + `NOTIFY_WEBHOOK_URL` 외부 중계, `GET /api/alerts/history`. 관제 어시스턴트 E2E 검증(Ollama 폴백 — tools 형 addon API 스펙 분기 수정, Claude 키는 운영 설정). README 에 Pre-install 가이드(관측 스택·LLM·webhook 토큰) 추가 |
| 2026-07-22 | v0.7 | Iteration 19 — **P1 로그 수집·검색 구현**: Loki 3.4(:3100, retention 15d) + mock 로그 생성기(syslog/dmesg/BMC), `GET /api/logs/{search,labels}`(LogQL 또는 job/keyword/level 간편 파라미터), 로그 분석 Agent(`addon-agents/zip/log-analyzer/`, intent `log_analysis`). 운영 전환: Promtail/Alloy 로 실 노드 수집. P1 잔여: 트레이스(OTel) |
| 2026-07-22 | v0.8 | Iteration 20 — **P1 트레이스 구현 (PRD §3 전 항목 완료)**: OTel 계측(`OTEL_ENABLED`, FastAPI+httpx→OTLP) + Jaeger(:16686/:4318) + trace-monitor addon(intent `trace_analysis`) — **Addon-first 원칙 첫 적용**(§7, core 조회 라우터 없음). **신규 요구 접수**: ① 관제 Agent 활성화 상태를 대시보드에 연동(활성 Agent 의 섹션/위젯만 표시) ② Addon 에이전트 활성화 시 대시보드 자동 반영(`/status` 위젯 규약) ③ 대시보드 위젯 미제공 addon 활성 시 예외처리 필수(스킵, 오류 미전파) — Iteration 21 대상 |
| 2026-07-22 | v0.9 | Iteration 21 — **대시보드 ↔ Agent 활성화 연동 구현**: GPU/HW 섹션은 해당 관제 Agent(`gpu_monitoring`/`hardware`) 활성 시에만 표시(비활성 시 조회 스킵). 활성 Addon 은 `GET /api/addon/<key>/status` **위젯 규약**으로 대시보드 자동 반영(프리미티브 필드 카드) — 새 addon 은 `/status` 구현만으로 연동, 미제공 addon 은 per-addon 예외처리로 조용히 스킵. **PRD §3 전 항목(P0+P1) 구현 완료** |
| 2026-07-22 | v1.0 | Iteration 22 — **Addon-first 정합 보완(요청 재확인)**: ① 로그 조회 core 라우터(`/api/logs/*`) 삭제 — log-analyzer addon 전용으로 일원화(트레이스는 기존 준수). ② 대시보드 addon 위젯을 에이전트 관리의 관제 Agent 토글(agent_config)과 AND 연동 — addon_key→config_key 매핑 규약(`-`→`_`). 위젯 미제공 addon 예외처리 유지 |
| 2026-07-22 | v1.1 | Iteration 23 — **P1 Agent 를 ADDON 에이전트로 등록·관리(재확인 요청 반영)**: log-analyzer·trace-monitor `is_builtin=0` + agent_config 미등록 → 에이전트 관리 "ADDON 에이전트" 섹션에서 토글·관리. orchestrator 가 addon `is_active=0` 을 intent 비활성으로 반영(채팅 라우팅 차단). 관리 체계 확정 — P0(GPU/HW)=내장 관제 AGENT, P1 이후=ADDON 에이전트 |
| 2026-07-22 | v1.2 | **P2 로드맵 수립** — `.docs/` 연구자료 4종 재검토로 Addon Agent 확장 후보 7종 도출·§3 P2 표 신설: storage-monitor, bmc-monitor, gpu-profiler, capacity-planner, anomaly-detector, net-monitor, workload-correlator (전부 Addon-first 규약). MIG/Tensor 세부 메트릭을 Out of Scope → P2-3 승격. P3 후보(합성점검·RUM, SLO 리포팅, 전원·환경) 보류 기록 |
| 2026-07-23 | v1.3 | Iteration 24 — **P2-1 스토리지 진단 Addon(storage-monitor) 구현**: 디스크 latency/IOPS/SMART/NVMe wear/RAID 스냅샷(조회 로직 구현체 내 — Addon-first), intent `storage`, `/status` 위젯, ADDON 에이전트 등록. 알람 규칙 SMARTUnhealthy·DiskLatencyHigh 추가(총 9종), mock exporter 스토리지 지표 확장. P2 잔여: bmc-monitor 이후 6종 |
| 2026-07-23 | v1.4 | Iteration 25 — **P2-2 BMC/IPMI Addon(bmc-monitor) 구현**: Prometheus(팬/전압/PSU/섀시전력/흡기온도) + Loki(`job=bmc` 이벤트 로그) 결합 조회(구현체 내 — Addon-first) 최초 사례, intent `bmc`, `/status` 위젯, ADDON 에이전트 등록. 알람 규칙 FanSpeedLow·VoltageOutOfRange 추가(총 11종). P2 잔여: gpu-profiler·capacity-planner·anomaly-detector·net-monitor·workload-correlator 5종 |
| 2026-07-23 | v1.5 | Iteration 26 — **P2-3 GPU 프로파일링 Addon(gpu-profiler) 구현**: SM occupancy·Tensor pipe active·DRAM active·throttle reasons·PCIe TX/RX(2·3순위 고급 지표, gpu-monitor 1순위와 분리) 조회(구현체 내 — Addon-first), intent `gpu_profiling`, `/status` 위젯, ADDON 에이전트 등록. 알람 규칙 GPUThrottling 추가(총 12종). P2 잔여: capacity-planner·anomaly-detector·net-monitor·workload-correlator 4종 |
| 2026-07-23 | v1.6 | Iteration 27 — **P2-4 용량 계획·효율 Addon(capacity-planner) 구현**: 저활용 GPU 탐지(`avg_over_time` 기간 평균, 임계값 조정 가능), 효율 리포트(fleet 평균 util/VRAM), 카디널리티 요약(메트릭별 활성 시계열 수 — PRD §5 성공지표 판단 근거) 조회(구현체 내 — Addon-first), intent `capacity_planning`, `/status` 위젯, ADDON 에이전트 등록. P2 잔여: anomaly-detector·net-monitor·workload-correlator 3종 |
| 2026-07-23 | v1.7 | Iteration 28 — **P2-5 이상 탐지 Addon(anomaly-detector) 구현**: z-score(population stdev, 표준 라이브러리만 사용) 기반 메트릭 이상 탐지 + 활성 알람 노드/GPU 단위 상관분석(구현체 내 — Addon-first), intent `anomaly_detection`, `/status` 위젯, ADDON 에이전트 등록. 라이브 검증: MOCK_ANOMALY 시 GPU3 온도 z-score 4.04 탐지 + 알람 9건 1노드 상관 확인. P2 잔여: net-monitor·workload-correlator 2종 |
| 2026-07-23 | v1.8 | Iteration 29 — **P2-6 네트워크 모니터링 Addon(net-monitor) 구현**: NIC 오류/드롭/링크상태/RX·TX 처리량 조회(구현체 내 — Addon-first), intent `network`, `/status` 위젯, ADDON 에이전트 등록. 알람 규칙 NICErrorsIncreasing·NICLinkDown 추가(총 14종). 관제 Agent 10종 완성(내장 2 + ADDON 8). P2 잔여: workload-correlator 1종 |
| 2026-07-23 | v1.9 | Iteration 30 — **P2-7 워크로드 상관 Addon(workload-correlator) 구현 — P2 로드맵 전체 완결(7/7)**: GPU 프로세스별(pid/job_id/user) 메모리 점유를 job/user 단위 집계(구현체 내 — Addon-first), intent `workload_correlation`, `/status` 위젯, ADDON 에이전트 등록. 라이브 검증: 분산 학습 잡(job-7a1, GPU0+1)이 정확히 상관됨 확인. **관제 Agent 11종 완성(내장 2 + ADDON 9)** — PRD P0+P1+P2 전체 범위 구현 완료 |
| 2026-07-23 | v2.0 | Iteration 31 — **버그 수정**: 채팅 "에이전트 목록" 응답에서 ADDON 에이전트 9종 누락 수정
  (`keyword_matcher` 가 tbl_agent_config 만 조회하던 것을 tbl_addon_agents 병합으로 개선).
  조사 중 부수 발견·수정: `_VALID_TYPES` 화이트리스트에 `"monitoring"` 누락으로 Addon 재업로드 시
  agent_type 이 조용히 "app" 으로 리셋되어 Addon-first 가드(tbl_agent_config 미등록)가 우회되던
  버그 확정·수정 |

---
*가정 항목(`가정:`)은 확인 후 갱신 필요. 근거: `.docs/` 연구자료 4종 + wise-dev-standard domains/ict-saas.yaml + Wise-MultiAIAgent-Template.*
