# 소프트웨어/하드웨어 모니터링 솔루션 비교 리포트: 인프라 규모별 최적 툴 선정 기준

## 개요
소프트웨어 모니터링과 하드웨어 모니터링은 분리된 영역이 아니라 하나의 운영 가시성 체계로 설계하는 것이 바람직하다[cite:17][cite:31][cite:33]. 특히 연구·AI·컴퓨터비전 환경에서는 CPU, 메모리, 스토리지뿐 아니라 GPU, VRAM, ECC 오류, 전력, 온도, 클럭, 프로세스별 GPU 점유까지 함께 수집해야 원인 분석과 성능 튜닝이 가능하다[cite:47][cite:53][cite:60].

이 리포트는 모니터링 영역을 대분류·중분류·소분류로 세분화하고, 각 분류별 목적과 기능 목록, 상용 및 오픈소스 도구를 정리한 뒤, 인프라 규모별 최적의 선정 기준을 제시한다[cite:19][cite:29][cite:43].

## 분류 체계

### 대분류
1. 하드웨어 및 물리 인프라 모니터링[cite:29][cite:69]
2. 시스템 및 플랫폼 모니터링[cite:19][cite:33]
3. 애플리케이션 성능 모니터링(APM)[cite:31][cite:35]
4. 로그·메트릭·트레이스 관측성[cite:12][cite:24]
5. 네트워크 및 장비 모니터링[cite:29][cite:70]
6. 사용자 경험 및 합성 테스트[cite:25][cite:33]
7. 보안·운영 자동화·거버넌스 모니터링[cite:17][cite:40]

### 중분류와 소분류

#### 1) 하드웨어 및 물리 인프라 모니터링
- 서버 하드웨어: CPU 소켓, 메모리 DIMM, 팬, PSU, RAID, 디스크, 온도 센서, 전압 레일[cite:69][cite:61]
- 가상화 호스트: ESXi, Hyper-V, KVM 호스트 리소스와 하드웨어 상태[cite:71][cite:33]
- 스토리지: SAN, NAS, Ceph, RAID 어레이, SSD SMART, NVMe 상태[cite:65][cite:61]
- 네트워크 장비: 스위치, 라우터, 방화벽, 무선장비, 포트 상태, 대역폭, 인터페이스 오류[cite:29][cite:70]
- 전원 및 환경: UPS, PDU, 랙 환경 센서, 온습도, 전력 사용량[cite:72][cite:61]
- 관리보드/BMC: iDRAC, iLO, IMM, IPMI, SNMP 기반 하드웨어 텔레메트리[cite:69]
- GPU/AI 가속기: GPU 코어 사용률, VRAM 사용량, 메모리 대역 사용률, ECC 오류, 온도, 전력, 클럭, XID 오류, 프로세스별 점유 메모리[cite:47][cite:53][cite:60]

#### 2) 시스템 및 플랫폼 모니터링
- OS 자원: CPU, 메모리, 스왑, 파일시스템, 프로세스, 서비스 상태[cite:19][cite:33]
- 컨테이너 및 쿠버네티스: 노드, 파드, 컨테이너, 스케줄링, 리소스 할당량[cite:43][cite:59]
- 미들웨어: 웹서버, WAS, 메시지 큐, 캐시, 런타임 VM[cite:17][cite:35]
- 데이터 플랫폼: DBMS, 검색엔진, 스트림 처리, 배치 처리[cite:17][cite:32]

#### 3) 애플리케이션 성능 모니터링(APM)
- 요청 지연시간, 처리량, 오류율[cite:31][cite:35]
- 서비스 의존성 맵[cite:36][cite:43]
- 분산 트레이싱과 병목 분석[cite:24][cite:33]
- 코드 레벨 프로파일링, 예외 추적, 배포 영향 분석[cite:31][cite:35]

#### 4) 관측성
- 메트릭 수집, 시계열 저장, 질의[cite:19]
- 로그 수집, 색인, 검색, 상관분석[cite:12][cite:24]
- 트레이스 수집과 서비스 그래프[cite:24][cite:33]
- 경보, 이벤트 라우팅, 에스컬레이션[cite:16][cite:17]

#### 5) 네트워크 및 장비 모니터링
- SNMP polling, trap, NetFlow/sFlow/IPFIX[cite:29][cite:70]
- 포트별 상태, 인터페이스 에러, 대역폭 추이[cite:29][cite:70]
- 장비 자동 발견, 토폴로지 가시화[cite:26][cite:29]

#### 6) 사용자 경험
- RUM(실사용자 모니터링)[cite:25][cite:33]
- Synthetics(API, 브라우저, 네트워크 경로 테스트)[cite:25][cite:33]

#### 7) 보안·운영·거버넌스
- 변경 감지와 구성 drift 파악[cite:32][cite:39]
- 이상 탐지와 AI 기반 원인 분석[cite:31][cite:40]
- SLA/SLO 관리와 리포팅[cite:17][cite:35]

## GPU를 포함한 하드웨어 모니터링 재정리
GPU는 더 이상 특수 장비가 아니라 AI, HPC, VDI, 비디오 처리, 시뮬레이션 환경의 핵심 인프라 자원이므로 하드웨어 모니터링의 독립 카테고리로 다루는 것이 적절하다[cite:47][cite:60]. NVIDIA는 NVML을 통해 GPU 식별 정보, GPU 및 메모리 활용률, ECC 오류 수, 온도, 팬 속도, 전력, 활성 프로세스와 프로세스별 할당 메모리, 클럭 및 PState를 조회할 수 있다고 설명한다[cite:60].

### GPU 모니터링 목적
- 학습/추론 작업의 병목 원인 식별, 예: GPU 코어는 한가하지만 VRAM이 부족한 경우[cite:53][cite:60]
- 모델 배치 및 멀티테넌시 환경에서 GPU 과점유, 메모리 단편화, 프로세스 충돌 탐지[cite:53][cite:60]
- 장시간 학습 중 ECC 오류, 온도 과열, 전력 제한, 클럭 저하(throttling) 탐지[cite:55][cite:60]
- Kubernetes 기반 GPU 워크로드의 운영 가시성 확보[cite:47][cite:59]

### GPU 모니터링 세부 기능 목록
- GPU utilization, SM occupancy 성격의 연산 활용률[cite:53][cite:60]
- VRAM total/used/free, memory utilization[cite:53][cite:60]
- GPU temperature, memory temperature(지원 제품), fan speed[cite:53][cite:60]
- Power draw, power limit, persistence mode[cite:53][cite:55]
- ECC single-bit/double-bit error count[cite:55][cite:60]
- Clocks(graphics/memory/video), PState[cite:53][cite:60]
- PCIe link 상태와 전송 특성[cite:53]
- 프로세스별 GPU 사용과 메모리 할당량[cite:60]
- XID 오류, 디바이스 헬스, 진단 정보[cite:54][cite:51]
- 컨테이너/노드별 GPU 할당량과 워크로드별 메트릭 연계[cite:47][cite:59]

### GPU 모니터링 수집 방식
- 단일 서버/워크스테이션: `nvidia-smi` 기반 주기 수집[cite:46][cite:53]
- 프로그래밍 통합: NVML API 기반 사용자 도구 또는 에이전트 개발[cite:60]
- 쿠버네티스/클러스터: NVIDIA DCGM Exporter + Prometheus + Grafana 조합[cite:47][cite:48][cite:59]
- 엔터프라이즈 통합 관제: Datadog, Dynatrace, New Relic, Instana 같은 상용 플랫폼에 GPU 메트릭을 연동[cite:17][cite:31][cite:35]

## 목적별 기능 매트릭스

| 대분류 | 주요 목적 | 핵심 기능 | 대표 오픈소스 | 대표 상용 |
|---|---|---|---|---|
| 하드웨어/서버 | 물리 장비 장애 예방, 자산 가시성 확보 | CPU, 메모리, 디스크, 팬, PSU, 온도, RAID, BMC/IPMI, SNMP[cite:69][cite:61] | Zabbix[cite:29], LibreNMS[cite:61][cite:70], Nagios/Icinga[cite:65] | Checkmk[cite:69], Datadog[cite:17], Dynatrace[cite:43] |
| GPU/AI 인프라 | 학습·추론 워크로드 안정성 및 비용 최적화 | GPU utilization, VRAM, ECC, power, clocks, process, XID[cite:47][cite:53][cite:60] | DCGM Exporter + Prometheus + Grafana[cite:47][cite:48][cite:59] | Datadog[cite:17], Instana[cite:31], New Relic[cite:35] |
| 시스템/OS | 호스트 운영 상태와 용량 감시 | 프로세스, 서비스, 파일시스템, 커널, 컨테이너[cite:19][cite:33] | Prometheus[cite:19], Zabbix[cite:29], Checkmk Raw[cite:63] | New Relic[cite:32], Datadog[cite:17] |
| APM | 서비스 성능 및 원인 분석 | 응답시간, 오류율, 트레이스, 의존성 맵[cite:31][cite:35] | OpenTelemetry + Jaeger/SigNoz | Dynatrace[cite:43], Instana[cite:31], Datadog[cite:24] |
| 로그/이벤트 | 장애 분석 및 포렌식 | 로그 수집, 검색, 상관분석[cite:12][cite:24] | OpenObserve[cite:12], Loki, ELK | Datadog[cite:24], New Relic[cite:33] |
| 네트워크 | 회선 품질 및 장비 상태 | SNMP, traps, flow, topology[cite:29][cite:70] | LibreNMS[cite:70], Zabbix[cite:29], Cacti | Checkmk[cite:69], Datadog[cite:25] |

## 주요 플랫폼 상세 비교

| 플랫폼 | 유형 | 강점 | 약점/유의점 | 적합한 환경 |
|---|---|---|---|---|
| Prometheus | 오픈소스 | 메트릭 중심 구조, exporter 생태계, Alertmanager 연동[cite:19][cite:21] | 장비 센서·자산 관리·네트워크 관제는 별도 조합 필요 | 클라우드 네이티브, 쿠버네티스, 개발조직 중심 |
| Zabbix | 오픈소스 | 서버·네트워크·하드웨어를 폭넓게 수집, 자동 발견, SNMP 강점[cite:28][cite:29] | 대규모 분산 환경에서 설계와 튜닝이 중요 | 온프레미스, 하이브리드, 네트워크 장비 많은 조직 |
| LibreNMS | 오픈소스 | 네트워크 장비와 센서 상태 시각화에 강함[cite:61][cite:70] | APM과 애플리케이션 관측성은 제한적 | 네트워크 중심, ISP, 장비 운영팀 |
| Nagios/Icinga | 오픈소스 | 플러그인 다양성, 특정 장비/스토리지 모니터링 확장성[cite:65] | 현대적 관측성 스택 대비 통합 경험이 약함 | 레거시 인프라, 플러그인 중심 운영 |
| Checkmk | 상용/오픈코어 | BMC/IPMI/SNMP 포함 서버 하드웨어 감시에 강함[cite:67][cite:69] | 기능 폭이 넓어 운영 표준화가 필요 | 데이터센터, 온프레미스 중심 엔터프라이즈 |
| Datadog | 상용 SaaS | 인프라, APM, 로그, RUM 통합[cite:17][cite:24] | 호스트/기능별 과금 누적 가능성 | 빠른 구축, 멀티클라우드, DevOps 조직 |
| Dynatrace | 상용 SaaS | 자동 발견, AI 분석, 엔드투엔드 풀스택[cite:40][cite:43] | 비용과 도입 설계가 무거울 수 있음 | 대규모 엔터프라이즈, 복잡한 서비스 의존성 |
| Instana | 상용 SaaS/하이브리드 | 자동 계측, 실시간성, 애플리케이션 맥락 연계[cite:31][cite:36] | 순수 장비 모니터링만 보면 과한 선택일 수 있음 | 마이크로서비스, 대형 애플리케이션 중심 |
| New Relic | 상용 SaaS | 호스트, 쿠버네티스, 로그, APM 통합[cite:32][cite:35] | 운영 모델에 따라 비용 관리 필요 | 클라우드 기반 제품 조직 |
| DCGM Exporter + Grafana | 오픈소스 조합 | GPU 메트릭 표준 수집과 시각화에 최적[cite:47][cite:48][cite:59] | GPU 외 영역은 별도 스택 필요 | AI 연구실, GPU 팜, ML 플랫폼 |

## 인프라 규모별 최적 툴 선정 기준

### 1) 소규모 인프라
소규모는 대체로 서버 수 1~20대, 네트워크 장비 수 제한적, 운영 담당자가 소수이며 예산이 제한된 환경을 의미한다. 이 구간에서는 기능의 절대량보다 설치 단순성, 운영 인력 부담, 기본 경보 품질이 더 중요하다.

권장 기준은 다음과 같다.
- 온프레미스/장비 위주면 Zabbix 또는 Checkmk Raw가 유리하다[cite:29][cite:63].
- 네트워크 장비 중심이면 LibreNMS가 빠르게 가치가 나온다[cite:61][cite:70].
- 쿠버네티스/클라우드 중심이면 Prometheus + Grafana가 효율적이다[cite:19][cite:21].
- GPU 연구 서버가 1~5대 수준이면 `nvidia-smi` 자동 수집 또는 DCGM Exporter 도입이 현실적이다[cite:47][cite:53].

소규모 최적 조합 예시는 다음과 같다.
- 일반 기업 서버/네트워크: Zabbix.
- 네트워크 운영 집중: LibreNMS.
- 연구실 GPU 서버: Prometheus + DCGM Exporter + Grafana.
- SaaS 스타트업: Datadog 또는 New Relic, 단 비용 관리 전제[cite:17][cite:35].

### 2) 중규모 인프라
중규모는 보통 서버 수 20~200대, 다수의 VM/컨테이너, 운영팀 분화, 서비스 중요도 상승이 특징이다. 이 구간부터는 메트릭만 보는 체계로는 부족하며 로그, 트레이스, 자동 발견, 권한 분리, 템플릿 표준화가 중요해진다.

권장 기준은 다음과 같다.
- 장비/서버/네트워크 자산 가시성이 중요하면 Zabbix 또는 Checkmk가 유리하다[cite:29][cite:69].
- 애플리케이션 분석까지 포함하면 Datadog, New Relic, Instana 같은 통합 플랫폼이 관리 효율이 높다[cite:17][cite:31][cite:35].
- GPU 노드가 10대 이상이면 DCGM Exporter를 표준 수집기로 채택하고, 노드/파드/잡 단위 메타데이터를 함께 저장하는 구조가 적합하다[cite:47][cite:59].
- 로그 분석 수요가 증가하면 OpenObserve, Loki, ELK 같은 로그 계층을 별도로 추가해야 한다[cite:12].

중규모 최적 조합 예시는 다음과 같다.
- 하이브리드 인프라: Zabbix + Grafana + OpenObserve.
- 클라우드 네이티브: Prometheus + Grafana + OpenTelemetry + Loki.
- AI 플랫폼: Prometheus + DCGM Exporter + Grafana + 로그 스택.
- 빠른 운영 내재화: Datadog 또는 New Relic.

### 3) 대규모 인프라
대규모는 수백~수천 대 호스트, 다수 리전/클러스터, 마이크로서비스, 다중 팀, 강한 SLA/SLO 요구사항이 있는 환경이다. 이 구간에서는 단순 모니터링 도구보다 데이터 모델, 라벨 체계, 멀티테넌시, 비용 통제, 자동 분석 기능이 중요하다.

권장 기준은 다음과 같다.
- 애플리케이션과 인프라를 함께 자동 상관분석해야 하면 Dynatrace 또는 Instana가 강력하다[cite:31][cite:40][cite:43].
- 엔터프라이즈 SaaS 기반 통합 운용이 필요하면 Datadog, New Relic이 적합하다[cite:17][cite:35].
- 비용 및 벤더 종속성 완화가 중요하면 Prometheus 계열을 기반으로 하되, 장기 저장, 연합(federation), 로그/트레이스 통합 설계를 별도로 해야 한다[cite:19][cite:21].
- GPU 클러스터는 DCGM Exporter를 표준 수집기로 두고, 스케줄러(Kubernetes/Slurm) 메타데이터와 연결하는 것이 필수적이다[cite:47][cite:59].

대규모 최적 조합 예시는 다음과 같다.
- 엔터프라이즈 통합 관측성: Dynatrace, Instana, Datadog.
- 대형 플랫폼 기업: Prometheus 생태계 + OpenTelemetry + 별도 로그/트레이스 백엔드.
- 대형 AI/HPC: Prometheus + DCGM Exporter + Grafana + 스케줄러/워크로드 메타데이터 + 로그 분석 스택.

## 최종 선정 프레임워크
도구 선정은 단순 기능 비교보다 운영 목표에 따라 판단해야 한다. 다음 질문에 대한 답으로 빠르게 좁힐 수 있다.

1. 주력 대상이 무엇인가: 서버/네트워크/스토리지인가, 애플리케이션인가, 둘 다인가[cite:29][cite:31].
2. 환경이 어디에 가까운가: 온프레미스, 하이브리드, 멀티클라우드, 쿠버네티스 중심인가[cite:17][cite:43].
3. GPU가 핵심 자원인가: VRAM, ECC, power, process 단위 추적이 필요한가[cite:47][cite:53][cite:60].
4. 운영팀 역량은 어느 정도인가: 오픈소스 조합을 직접 운영할 수 있는가, SaaS가 더 적합한가[cite:1][cite:17].
5. 예산과 라이선스 정책은 어떤가: 초기 CAPEX 절감이 중요한가, 운영 OPEX 예측 가능성이 중요한가[cite:1][cite:17].
6. 규제와 감사 요구가 있는가: 보존기간, 접근통제, 온프레미스 저장 요구가 있는가[cite:33][cite:43].

## 권고안
- 레거시 장비와 물리 인프라가 많으면 Zabbix 또는 Checkmk 계열이 기본축으로 적합하다[cite:29][cite:69].
- 클라우드 네이티브 서비스라면 Prometheus 생태계 또는 Datadog/New Relic 같은 통합 SaaS가 효율적이다[cite:17][cite:19][cite:35].
- AI 연구·컴퓨터비전·LLM 추론 환경이라면 GPU 모니터링을 별도 항목으로 설계하고, 최소한 VRAM, utilization, temperature, power, ECC, process별 점유를 수집해야 한다[cite:47][cite:53][cite:60].
- 장비 모니터링과 애플리케이션 모니터링을 별도 운영하지 말고, 장애 원인 분석 관점에서 상호 연계된 대시보드와 경보 체계를 만드는 것이 가장 중요하다[cite:17][cite:31][cite:35].
