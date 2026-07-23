# 인프라 규모별 최적의 모니터링 툴 비교: GPU(VRAM/Core) 및 서버 하드웨어(CPU/RAID) 통합 가이드

## 개요
GPU 중심 인프라와 전통적인 서버 하드웨어 인프라는 모니터링 요구사항이 다르지만, 실제 운영에서는 하나의 통합 관제 체계 안에서 설계해야 한다[cite:47][cite:29][cite:69]. GPU 워크로드는 VRAM, GPU core utilization, ECC 오류, 전력, 온도, 프로세스별 점유를 중점적으로 봐야 하고, 서버 하드웨어는 CPU, 메모리, 디스크, RAID, 팬, 전원, 온도, BMC 상태를 중점적으로 봐야 한다[cite:53][cite:60][cite:61][cite:69].

이 문서는 다음 다섯 가지 요구를 통합해 정리한다.
- 인프라 규모별 최적의 모니터링 툴 비교[cite:17][cite:19][cite:29]
- GPU/서버 하드웨어 성능 모니터링 체크리스트[cite:47][cite:53][cite:61]
- 인프라 규모별 비용 효율성 비교[cite:81][cite:90][cite:93][cite:101]
- Kubernetes 환경에서 DCGM Exporter 설정 및 성능 최적화[cite:47][cite:59]
- GPU 클러스터 필수 알람 및 장애 대응 정책[cite:51][cite:54][cite:55]

## 모니터링 대상 체계

### GPU 계층
GPU는 단순 가속기가 아니라 독립적인 운영 자원이다. NVIDIA는 NVML과 `nvidia-smi`를 통해 GPU utilization, 메모리 사용량, ECC 오류, 온도, 팬 속도, 전력, 클럭, PState, 활성 프로세스, 프로세스별 할당 메모리를 수집할 수 있다고 설명한다[cite:46][cite:53][cite:60].

GPU 모니터링의 핵심 항목은 다음과 같다.
- GPU core utilization[cite:53][cite:60]
- VRAM total/used/free 및 memory utilization[cite:53][cite:60]
- Temperature, fan speed, power draw, power limit[cite:53][cite:55]
- ECC single/double bit errors[cite:55][cite:60]
- Clocks, PState, throttling 징후[cite:53][cite:60]
- XID errors 및 디바이스 헬스 진단[cite:51][cite:54]
- Process별 GPU 사용 및 메모리 점유[cite:60]

### 서버 하드웨어 계층
서버 하드웨어는 단순 CPU 사용률만 보는 것이 아니라 물리 상태와 예지보전 정보를 함께 봐야 한다. Checkmk와 LibreNMS 문서는 BMC, iLO, iDRAC, 센서, 온도, 팬, 전원, 스토리지 상태, 장치 health 정보를 수집하는 방식을 설명한다[cite:69][cite:61].

서버 하드웨어 모니터링의 핵심 항목은 다음과 같다.
- CPU usage, load, core saturation[cite:19][cite:33]
- Memory, swap, NUMA 불균형[cite:19][cite:33]
- Disk latency, IOPS, SMART/NVMe health[cite:61][cite:65]
- RAID controller, array degraded 상태[cite:65][cite:69]
- Fan, PSU, temperature, voltage[cite:61][cite:69]
- NIC throughput, packet error, drop[cite:29][cite:70]
- BMC/IPMI/iDRAC/iLO event[cite:69]

## 인프라 규모별 툴 비교

### 소규모 인프라
소규모는 대체로 1~20대 서버, 제한된 네트워크 장비, 전담 SRE 부재, 예산 제약이 큰 환경이다. 이 구간에서는 도입 속도와 유지보수 난이도가 가장 중요하다.

| 항목 | 권장 도구 | 이유 |
|---|---|---|
| 일반 서버/네트워크 | Zabbix[cite:29] | 서버, 네트워크, SNMP, 자동 발견을 한 플랫폼에서 처리 가능[cite:28][cite:29] |
| 네트워크 중심 | LibreNMS[cite:70] | 장비 자동 발견과 센서/포트 가시화가 강함[cite:61][cite:70] |
| GPU 연구 서버 1~5대 | `nvidia-smi` + Prometheus node_exporter 또는 DCGM Exporter[cite:46][cite:47][cite:53] | 최소 비용으로 VRAM/GPU 상태 확보 가능 |
| 빠른 SaaS 도입 | Grafana Cloud Free/Pro[cite:90] 또는 New Relic Free[cite:101] | 무료/저비용으로 시작 가능 |

소규모에서는 상용 SaaS가 운영 편의성은 높지만, 호스트 수가 적을 때도 기능이 늘면 과금 항목이 빠르게 누적될 수 있다. Datadog은 인프라 모니터링이 연간 약정 기준 호스트당 월 15달러부터 시작하고, APM은 호스트당 월 31달러 수준으로 별도 과금될 수 있다[cite:81][cite:83].

### 중규모 인프라
중규모는 20~200대 서버, 가상화/컨테이너 혼합, 다수 팀 운영, 로그·트레이스 필요성이 증가한 환경이다. 이 구간부터는 메트릭만 보는 도구보다 로그와 APM 연계성이 중요해진다.

| 항목 | 권장 도구 | 이유 |
|---|---|---|
| 하이브리드 서버/장비 중심 | Zabbix + Grafana + 로그 스택 | 장비/서버 수집과 시각화 분리 운영에 유리[cite:29][cite:12] |
| 네트워크+하드웨어 중심 | Checkmk[cite:69] | BMC, 하드웨어 센서, 장비 가시성 강점[cite:67][cite:69] |
| 클라우드 네이티브 | Prometheus + Grafana + OpenTelemetry | 쿠버네티스와 exporter 생태계가 강함[cite:19][cite:21][cite:59] |
| 빠른 운영 통합 | Datadog[cite:17], New Relic[cite:101] | 인프라, 로그, APM 통합 도입이 빠름 |
| GPU 노드 10대 이상 | DCGM Exporter + Prometheus + Grafana[cite:47][cite:48][cite:59] | GPU 메트릭 표준화와 대시보드 재사용이 용이 |

중규모부터는 비용 효율성을 단순 라이선스가 아니라 운영 인건비까지 포함해 계산해야 한다. 오픈소스는 라이선스 비용이 낮지만 운영 표준화, 스토리지 설계, 업그레이드, 고가용성 구축에 내부 인력이 더 들어간다[cite:1][cite:19].

### 대규모 인프라
대규모는 수백~수천 호스트, 멀티클러스터, 마이크로서비스, SLA/SLO, 다중 팀 운영이 특징이다. 이 구간에서는 수집량과 원인 분석 속도가 도구 선정의 핵심이다.

| 항목 | 권장 도구 | 이유 |
|---|---|---|
| 엔터프라이즈 풀스택 | Dynatrace[cite:43][cite:93], Instana[cite:31] | 자동 발견, AI 기반 분석, 풀스택 맥락 제공 |
| SaaS 통합 관측성 | Datadog[cite:17][cite:81], New Relic[cite:101] | 제품군 통합과 운영 생산성 강점 |
| 대형 클라우드 네이티브 | Prometheus 생태계 + OpenTelemetry | 벤더 종속성 완화, 유연한 설계 가능[cite:19][cite:21] |
| 대형 GPU/AI 클러스터 | DCGM Exporter + Prometheus + Grafana + 스케줄러 메타데이터[cite:47][cite:59] | GPU 노드/잡/파드 상관분석에 적합 |

Dynatrace는 호스트 크기와 무관하게 인프라 모니터링이 시간당 과금되는 구조를 제시하며, Foundation & Discovery와 Full-Stack Monitoring도 별도 단가를 제공한다[cite:93]. 따라서 대규모에서는 단가 자체보다 “어떤 기능을 어느 계층까지 활성화할 것인가”가 비용 설계의 핵심이 된다[cite:93][cite:94].

## 성능 모니터링 체크리스트

### GPU 체크리스트
| 항목 | 필수 여부 | 기준 예시 | 목적 |
|---|---|---|---|
| GPU utilization | 필수 | 평균 90% 이상 장기 지속 또는 10% 이하 장기 지속[cite:53][cite:60] | 과소/과대 활용 탐지 |
| VRAM used/free | 필수 | 사용률 90% 초과, OOM 빈발[cite:53][cite:60] | 메모리 병목 탐지 |
| ECC errors | 필수(데이터센터 GPU) | 1회 이상 증가 시 조사[cite:55][cite:60] | 하드웨어 안정성 확인 |
| Temperature | 필수 | 임계값 접근 시 경보[cite:53][cite:60] | 과열 방지 |
| Power draw/power cap | 필수 | cap 근접 지속 시 조사[cite:55] | 전력 제한 병목 확인 |
| XID errors | 필수 | 즉시 알람[cite:51][cite:54] | 장애 조기 탐지 |
| Process별 메모리 점유 | 필수 | 비정상 점유/메모리 누수 탐지[cite:60] | 사용자별 원인 분석 |

### 서버 하드웨어 체크리스트
| 항목 | 필수 여부 | 기준 예시 | 목적 |
|---|---|---|---|
| CPU usage/load | 필수 | 피크 시간 장기 80% 초과[cite:19][cite:33] | 용량 계획 |
| Memory/swap | 필수 | swap 사용 증가, reclaim 급증[cite:19][cite:33] | 성능 저하 방지 |
| Disk latency/IOPS | 필수 | 지연 급증, 큐 적체[cite:65] | 스토리지 병목 파악 |
| RAID degraded | 필수 | 즉시 알람[cite:65][cite:69] | 데이터 손실 예방 |
| Fan/PSU/temp | 필수 | 센서 abnormal 시 즉시 경보[cite:61][cite:69] | 물리 장애 예방 |
| NIC error/drop | 필수 | 인터페이스 오류 증가[cite:29][cite:70] | 네트워크 이상 탐지 |
| BMC/iDRAC/iLO event | 권장 | critical 이벤트 발생[cite:69] | 운영 선제 대응 |

## 비용 효율성 비교

### 비용 모델별 차이
관측성 도구의 비용은 단순 호스트 수가 아니라 호스트, 메트릭 시계열, 로그 GB, 트레이스 양, 세션 수, 컨테이너/파드 시간 등 다양한 과금 축으로 구성된다[cite:90][cite:93][cite:101]. 따라서 GPU 클러스터처럼 메트릭 종류가 많고 로그가 큰 환경은 “기본 호스트 가격”만 보고 선정하면 실제 비용을 과소평가하기 쉽다[cite:81][cite:90][cite:93].

| 플랫폼 | 기본 비용 구조 | 비용상 강점 | 비용상 유의점 |
|---|---|---|---|
| Zabbix | 라이선스 비용 없음 | 초기 라이선스 절감 | 운영 인건비와 스토리지 설계 부담 |
| Prometheus + Grafana OSS | 라이선스 비용 없음 | GPU/서버 혼합 수집에 유연 | 장기보관, HA, 운영 자동화 비용 발생[cite:19][cite:21] |
| Grafana Cloud | Free, Pro는 월 19달러 플랫폼 fee + 사용량 과금[cite:90] | 소규모 시작 비용 낮음 | active series와 logs/traces 증가 시 비용 상승[cite:90][cite:97] |
| New Relic | 월 100GB 무료 ingest, 초과분 GB당 0.40달러[cite:101] | 데이터 기반 단순 모델 | 고빈도 로그 환경에서 급증 가능 |
| Datadog | 인프라 호스트당 월 15달러부터, APM은 호스트당 월 31달러 수준[cite:81][cite:83] | 운영 통합과 빠른 도입 | 기능 확장 시 누적 과금이 큼 |
| Dynatrace | 호스트/메모리 GiB/시간 단위 과금[cite:93] | 대규모에서 정교한 사용량 기반 설계 가능 | 기능 조합 이해가 복잡할 수 있음 |

### 규모별 비용 효율성 판단
- 소규모: 무료 티어 또는 오픈소스가 일반적으로 가장 유리하다[cite:90][cite:101].
- 중규모: 운영 인력 비용을 포함하면 Datadog/New Relic/Grafana Cloud가 오히려 총소유비용(TCO)에서 경쟁력이 생길 수 있다[cite:81][cite:90][cite:101].
- 대규모: 수집량 통제가 되지 않으면 SaaS 비용이 크게 상승하므로, 메트릭/로그 샘플링과 보존정책이 필수다[cite:93][cite:97][cite:101].

## Kubernetes에서 DCGM Exporter 설정 가이드
DCGM Exporter는 Kubernetes 클러스터에서 GPU 텔레메트리를 수집하기 위한 NVIDIA 공식 경로다[cite:47][cite:59]. NVIDIA는 Helm 차트를 제공하며, Prometheus와 Grafana를 함께 구성하는 방법을 안내한다[cite:59].

### 기본 설정 절차
1. GPU 노드에 NVIDIA 드라이버와 컨테이너 런타임 지원을 준비한다[cite:47][cite:59].
2. Helm 저장소를 추가한다[cite:59].
3. `gpu-helm-charts/dcgm-exporter` 차트를 설치한다[cite:59].
4. Prometheus가 exporter endpoint를 스크레이프하도록 ServiceMonitor 또는 scrape 설정을 추가한다[cite:47][cite:59].
5. Grafana 대시보드를 연결해 GPU utilization, memory, temperature, power 지표를 시각화한다[cite:48][cite:59].

### 성능 최적화 기준
- 모든 메트릭을 무조건 수집하지 말고 운영 목적에 맞는 지표만 활성화한다. GPU 노드 수가 커질수록 시계열 수가 급격히 증가할 수 있다[cite:47][cite:90].
- scrape interval은 15초 또는 30초부터 시작하고, 초단위 고빈도 수집은 장애 분석 목적이 명확할 때만 적용한다[cite:47].
- 파드/잡/노드 라벨 체계를 정리해 VRAM 사용량과 실제 워크로드를 연결해야 한다[cite:47][cite:59].
- Prometheus 보존기간과 remote write 정책을 분리해 최근 상세 데이터와 장기 추세 데이터를 나눠 관리하는 것이 효율적이다[cite:19][cite:90].
- 고카디널리티 라벨을 제한해 비용과 성능 문제를 줄인다[cite:90][cite:97].

## GPU 클러스터 필수 알람 정책
GPU 클러스터에서는 단순 임계치 알람만으로는 부족하며, 장애 유형별 정책이 필요하다. NVIDIA 문서는 ECC, diagnostics, device health, XID 관련 진단 정보를 제공하며, 실무에서는 이를 운영 정책으로 연결해야 한다[cite:51][cite:54][cite:55].

### 필수 알람
- GPU down 또는 exporter 미수집 감지[cite:47]
- VRAM 사용률 장기 고점 유지[cite:53][cite:60]
- GPU utilization 장기 저활용 또는 비정상 고활용[cite:53][cite:60]
- ECC error 증가[cite:55][cite:60]
- Temperature 과열 또는 fan anomaly[cite:53][cite:60]
- Power cap 지속 근접[cite:55]
- XID error 즉시 감지[cite:51][cite:54]
- RAID degraded, PSU/fan failure, BMC critical event[cite:61][cite:65][cite:69]

### 대응 정책
| 장애 유형 | 1차 조치 | 2차 조치 | 에스컬레이션 |
|---|---|---|---|
| VRAM 부족/OOM | 잡 종료 여부 확인, 배치 크기 축소 | 스케줄링 정책 조정 | ML 플랫폼 담당자 |
| GPU 온도/전력 이상 | 냉각/전원 상태 확인 | 노드 cordon 또는 작업 이동 | 인프라 운영팀 |
| ECC/XID 오류 | GPU reset 가능 여부 검토 | 노드 격리 및 정밀 진단[cite:51][cite:55] | 하드웨어 벤더/데이터센터 |
| RAID degraded | 즉시 장애 티켓 발행 | 디스크 교체 및 rebuild | 스토리지/서버 운영팀 |
| exporter 데이터 미수집 | Pod 상태, daemonset, 드라이버 확인 | 노드 재등록 또는 exporter 재배포 | 플랫폼 운영팀 |

## 최종 권고안
- 소규모 GPU 연구실은 Prometheus + DCGM Exporter + Grafana 또는 Grafana Cloud Free/Pro가 가장 실용적이다[cite:59][cite:90].
- 전통적인 서버 하드웨어 중심 조직은 Zabbix 또는 Checkmk가 CPU, RAID, 센서, BMC까지 묶어 보기 좋다[cite:29][cite:69].
- 중대형 AI 플랫폼은 GPU 텔레메트리와 서버 하드웨어 상태를 한 대시보드에서 함께 보고, 애플리케이션 관측성은 별도 계층으로 확장하는 것이 바람직하다[cite:17][cite:31][cite:47].
- 비용 효율성은 도구 라이선스보다 데이터 수집량 통제, 메트릭 카디널리티 관리, 로그 보존 정책, 운영 자동화 수준에서 크게 갈린다[cite:90][cite:93][cite:101].
