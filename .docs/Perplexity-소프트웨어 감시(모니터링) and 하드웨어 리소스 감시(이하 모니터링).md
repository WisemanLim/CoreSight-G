<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# 소프트웨어 감시(모니터링)만큼 중요한 것이 하드웨어 리소스 감시(이하 모니터링)입니다. 이에 소프트웨어 및 하드웨어 모니터링에 대한 플랫폼별 조사를 진행합니다. 카테고리를 대중소로 나누고 이에 맞춰 목적, 기능리스트를 도출하고 이에 상응하는 상용 및 오픈소스 플랫폼을 열거합니다. 최대한 상세하게 나누고 분류하여 정리를 합니다.

아래는 **소프트웨어 모니터링 + 하드웨어 리소스 모니터링**을 함께 보며, 이를 **대(大)·중(中)·소(小) 카테고리**로 나누어 목적, 기능, 그리고 상용/오픈소스 플랫폼까지 정리한 조사 결과입니다. 하드웨어 관점에서는 CPU·메모리·디스크·네트워크·전원·팬·센서·펌웨어·장치 상태까지 포함해 보는 것이 일반적이며, Zabbix는 CPU/팬/전원공급장치/네트워크 장비의 자동 발견과 SNMP 기반 하위 수준 탐색을 지원합니다.[^1_1][^1_2]

## 분류 체계

모니터링은 크게 **인프라/하드웨어**, **시스템/플랫폼**, **애플리케이션/서비스**, **사용자 경험**, **보안/운영**, **비즈니스/거버넌스**로 나누는 것이 실무적으로 가장 유용합니다. 이 중 소프트웨어 모니터링은 애플리케이션 코드와 서비스 동작에 초점을 맞추고, 하드웨어 모니터링은 물리/가상 자원 상태와 성능을 중심으로 봅니다.[^1_3][^1_4][^1_5][^1_6]

### 대분류

- 인프라/하드웨어 모니터링.
- 시스템/OS 모니터링.
- 애플리케이션 성능 모니터링(APM).
- 로그/이벤트/트레이싱 관측성.
- 네트워크/장비 모니터링.
- 보안/컴플라이언스 모니터링.
- 사용자 경험/합성 테스트.
- 비즈니스/서비스 레벨 모니터링.


### 중분류 예시

- 하드웨어: 서버, 스토리지, 네트워크 장비, 전원, 센서.
- 시스템: OS 커널, 프로세스, 파일시스템, 서비스 데몬.
- 애플리케이션: 트랜잭션, DB 쿼리, API, 큐, 캐시.
- 관측성: 메트릭, 로그, 트레이스, 이벤트.
- 운영: 알림, 자동조치, 변경감지, 장애분석.
- 거버넌스: SLA, SLO, 감사, 규정준수.


## 목적과 역할

하드웨어 모니터링의 핵심 목적은 **장애 예방, 용량관리, 병목 식별, 자산 가시성 확보**입니다. 소프트웨어 모니터링의 핵심 목적은 **기능 이상 탐지, 성능 저하 분석, 배포 영향 추적, 사용자 체감 품질 보호**입니다.[^1_7][^1_8][^1_9][^1_10]

운영 관점에서는 두 영역이 분리되지 않고 연결됩니다. 예를 들어 CPU 사용률 상승은 애플리케이션 누수일 수도 있고, 스토리지 I/O 지연일 수도 있으며, 네트워크 재전송 증가일 수도 있어 원인-결과를 함께 봐야 합니다.[^1_4][^1_11][^1_6]

## 기능 목록

### 1) 하드웨어 리소스 모니터링 기능

- CPU 사용률, load average, steal time.
- 메모리 사용량, swap, page fault.
- 디스크 사용량, IOPS, latency, SMART 상태.
- 네트워크 대역폭, 패킷 손실, 오류, 지연.
- 전원공급장치(PSU), 팬, 온도, 전압, 센서 상태.
- RAID/HBA/NIC 상태.
- 펌웨어/BIOS/iDRAC/iLO 등 관리 컨트롤러 상태.
- 서버, 스토리지, 스위치, 프린터, UPS 자동 발견.
- SNMP, WMI, agent, IPMI, Redfish 기반 수집.
- 자산 변경 감지 및 수명주기 관리.[^1_12][^1_2][^1_1]


### 2) 소프트웨어 모니터링 기능

- 애플리케이션 응답시간, 오류율, 처리량.
- 분산 트레이싱, 병목 구간 추적.
- 로그 수집, 검색, 상관분석.
- 배포/설정 변경 추적.
- 서비스 의존성 맵.
- 사용자 세션 및 합성 테스트.
- 알림, 에스컬레이션, 자동 remediation.
- SLO/SLA, 골든 시그널, 이상탐지.[^1_8][^1_11][^1_7][^1_4]


### 3) 공통 기능

- 대시보드.
- 경보/알림.
- 자동 발견.
- 태그/라벨링.
- 이벤트 상관분석.
- 권한관리.
- 보고서/감사.
- API 및 외부 연동.[^1_5][^1_6][^1_7]


## 플랫폼별 계층화

아래 표는 실무에서 자주 쓰는 계층 기준으로 정리한 것입니다. 상용은 기능 통합과 운영 편의성이 강하고, 오픈소스는 유연성과 확장성이 강합니다.


| 계층 | 목적 | 대표 기능 | 상용 플랫폼 | 오픈소스 플랫폼 |
| :-- | :-- | :-- | :-- | :-- |
| 하드웨어/인프라 | 서버·장비 상태, 자원 소모, 장애 예방 | CPU, 메모리, 디스크, 네트워크, 센서, SNMP, IPMI | Datadog Infrastructure Monitoring [^1_7], Dynatrace Infrastructure Observability [^1_6], IBM Instana [^1_8], New Relic Infrastructure [^1_9] | Zabbix [^1_2], Prometheus [^1_4], OpenObserve [^1_13], Nagios, Icinga, Observium, Cacti |
| 시스템/플랫폼 | OS와 런타임 상태 | 프로세스, 서비스, 커널, 파일시스템, 컨테이너 | Datadog [^1_7], New Relic [^1_5], Dynatrace [^1_6], Instana [^1_8] | Prometheus [^1_4], Zabbix [^1_2], Icinga, Sensu, Munin |
| 애플리케이션/APM | 트랜잭션, 오류, 코드 레벨 원인 분석 | APM, 분산추적, 프로파일링 | Dynatrace [^1_8][^1_6], Instana [^1_8], Datadog [^1_14][^1_7], New Relic [^1_5] | Scouter, Jaeger, OpenTelemetry, SigNoz |
| 로그/이벤트 | 사고 분석과 상관관계 | 수집, 검색, 필터링, 경보 | Datadog [^1_14], New Relic [^1_5], Dynatrace [^1_6] | Loki, OpenObserve [^1_13], ELK/EFK, Fluentd |
| 네트워크/장비 | 스위치/라우터/방화벽/회선 | SNMP, NetFlow, topology, auto-discovery | Datadog Network Monitoring [^1_15], Dynatrace [^1_6], New Relic [^1_11] | Zabbix [^1_2], Observium, LibreNMS, Cacti |
| 사용자 경험 | 실제 체감 품질 검증 | RUM, 합성 테스트, 브라우저/API 테스트 | Datadog RUM/Synthetics [^1_15], New Relic [^1_5], Instana [^1_8] | Grafana k6, OpenTelemetry RUM 생태계 |
| 보안/준수 | 감사, 정책 위반, 취약점 | 감사로그, 규정준수, 이상행위 탐지 | Datadog [^1_7][^1_15], Dynatrace [^1_6], Instana [^1_8] | Wazuh, Falco, OpenSearch Security |
| 운영/자동화 | 대응 속도 향상 | 자동조치, Runbook, AIOps | Datadog [^1_7], Dynatrace [^1_16], Instana [^1_8] | Zabbix action, Icinga automation, Prometheus Alertmanager |

## 세부 카테고리

### 하드웨어 중심

- 물리 서버 모니터링.
- 가상화 호스트 모니터링.
- 스토리지 모니터링.
- 네트워크 장비 모니터링.
- 전원/환경 모니터링.
- 엔드포인트/PC 자산 모니터링.
- 데이터센터 시설 모니터링.

이 영역에서는 SNMP, IPMI, Redfish, WMI, 에이전트 방식이 핵심입니다. Zabbix는 네트워크 장비와 하드웨어 리소스의 자동 발견, low-level discovery, SNMP 메트릭 수집에 강점이 있습니다.[^1_2][^1_1]

### 소프트웨어 중심

- 애플리케이션 성능 모니터링(APM).
- 분산 시스템 추적.
- 로그 기반 문제 분석.
- 배포 영향 분석.
- 오류 추적 및 예외 모니터링.
- 데이터베이스 및 메시징 시스템 모니터링.
- 사용자 행동 및 세션 분석.

Prometheus는 메트릭 중심의 오픈소스 모니터링 시스템으로, 수집(scrape), 저장, 쿼리, 알림 구조를 갖고 있으며 exporter와 client library 생태계가 강합니다. Datadog, Dynatrace, Instana, New Relic은 메트릭·로그·트레이스까지 묶은 통합 관측성에 강합니다.[^1_17][^1_6][^1_7][^1_4][^1_8][^1_5]

## 대표 플랫폼 요약

### 오픈소스

- Prometheus: 메트릭 중심, exporter 생태계가 매우 강함.[^1_4][^1_17]
- Zabbix: 인프라/네트워크/서버/하드웨어 통합 감시에 강함.[^1_1][^1_2]
- Icinga: 모듈식 구조, 플러그인 확장에 적합.[^1_18]
- Observium: 네트워크 장비 자동 발견과 가시화에 적합.[^1_18]
- Cacti: SNMP/RRD 기반 시계열 그래프에 강함.[^1_18]
- OpenObserve: 로그/메트릭/트레이스 통합 지향.[^1_13]
- Grafana 생태계: 시각화 허브로 널리 활용.[^1_19]


### 상용

- Datadog: 인프라, 로그, APM, RUM, Synthetics, 네트워크, 보안까지 단일 플랫폼 성격이 강함.[^1_15][^1_7]
- Dynatrace: 자동 발견, AI 기반 분석, 엔터프라이즈 인프라/애플리케이션 통합 관측성.[^1_16][^1_6][^1_8]
- IBM Instana: 1초 단위 관측, 자동 계측, 풀스택 자동 상관분석.[^1_20][^1_8]
- New Relic: 호스트·컨테이너·Kubernetes·로그·이벤트의 통합 가시성.[^1_11][^1_5]


## 선택 기준

실무에서는 다음 기준으로 고르면 됩니다. 하드웨어 중심이고 온프레미스/네트워크 장비 비중이 크면 Zabbix나 Observium 계열이 적합합니다. 애플리케이션과 인프라를 함께 보고, 운영 편의성과 자동화를 중시하면 Datadog, Dynatrace, Instana, New Relic 같은 통합 플랫폼이 유리합니다.[^1_6][^1_7][^1_2][^1_8][^1_5][^1_18]

오픈소스 표준화와 벤더 종속성 최소화가 목표라면 Prometheus + Grafana + Alertmanager 조합이 가장 범용적입니다. 네트워크 장비와 자산 가시성이 중요하면 Zabbix가 매우 실용적이며, SNMP 기반의 다양한 하드웨어를 넓게 커버할 수 있습니다.[^1_17][^1_2][^1_4][^1_1]

## 실무 권장 구조

기업 환경에서는 보통 다음처럼 계층형으로 구성합니다.

- 1차: 하드웨어/인프라 계층 감시.
- 2차: OS와 미들웨어 감시.
- 3차: 애플리케이션/APM 감시.
- 4차: 로그/트레이스 상관분석.
- 5차: 알림, 자동조치, 리포팅.

이 구조는 장애가 발생했을 때 “장비 문제인지, OS 문제인지, 애플리케이션 문제인지”를 빠르게 분리하는 데 도움이 됩니다. 특히 클라우드와 온프레미스가 혼재된 환경에서는 인프라 모니터링만으로는 불완전하므로, 애플리케이션 및 변경 이력까지 함께 보는 방식이 권장됩니다.[^1_7][^1_8][^1_11]

원하시면 다음 단계로 이어서 **“플랫폼별 상세 비교표(기능/장단점/라이선스/아키텍처/도입 난이도/비용 구조)”** 형태로 더 촘촘하게 정리해 드리겠습니다.
<span style="display:none">[^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_30][^1_31][^1_32][^1_33][^1_34][^1_35][^1_36][^1_37][^1_38][^1_39][^1_40][^1_41][^1_42][^1_43][^1_44][^1_45]</span>

<div align="center">⁂</div>

[^1_1]: https://blog.zabbix.com/handy-tips-38-automating-snmp-item-creation-with-low-level-discovery/23521/

[^1_2]: https://www.zabbix.com/network_monitoring

[^1_3]: https://prometheus.io/docs/alerting/latest/

[^1_4]: https://prometheus.io/docs/introduction/overview/

[^1_5]: https://docs.newrelic.com/docs/infrastructure/introduction-infra-monitoring/

[^1_6]: https://docs.dynatrace.com/docs/observe/infrastructure-observability

[^1_7]: https://www.datadoghq.com/product/infrastructure-monitoring/

[^1_8]: https://www.ibm.com/products/instana/infrastructure-monitoring

[^1_9]: https://newrelic.com/platform/infrastructure/features

[^1_10]: https://docs.dynatrace.com/docs/observe/infrastructure-observability/infrastructure-and-operations

[^1_11]: https://newrelic.com/platform/infrastructure

[^1_12]: https://www.ninjaone.com/blog/best-hardware-monitoring-software/

[^1_13]: https://openobserve.ai/blog/top-10-open-source-monitoring-tools/

[^1_14]: https://www.datadoghq.com/product/

[^1_15]: https://support.skax.co.kr/ko/support/solutions/articles/42000092519-datadog-소개

[^1_16]: https://www.dynatrace.com/hub/?filter=infrastructure-monitoring

[^1_17]: https://prometheus.io/docs/instrumenting/exporters/

[^1_18]: https://blog.naver.com/drods/221257600677

[^1_19]: https://blog.naver.com/itearth/222544006011

[^1_20]: https://www.ibm.com/products/instana

[^1_21]: https://www.opensourcealternatives.to/blog/best-open-source-monitoring-tools

[^1_22]: https://oneuptime.com/blog/post/2026-02-06-best-open-source-monitoring-tools-2026/view

[^1_23]: https://www.g2.com/pt/categories/hardware-monitoring

[^1_24]: https://www.metricfire.com/blog/top-8-open-source-monitoring-tools-compared/

[^1_25]: https://www.slideshare.net/slideshow/ss-25995750/25995750

[^1_26]: https://slashdot.org/software/hardware-monitoring/

[^1_27]: https://thectoclub.com/tools/best-hardware-monitoring-software/

[^1_28]: https://qiita.com/keitah/items/70e6b63e4c504b4796fa

[^1_29]: https://googiehost.com/ko/블로그/최고의-오픈소스-서버-모니터링-도구

[^1_30]: https://www.guru99.com/ko/hardware-monitoring-software.html

[^1_31]: https://oshri.kosha.or.kr/oshri/professionalBusiness/monitoringSystemIntroduction_02.do?mode=download\&articleNo=406474\&attachNo=227153

[^1_32]: https://www.zabbix.com/documentation/1.8/en/manual/auto-discovery/how_it_works

[^1_33]: https://www.zabbix.com/features

[^1_34]: https://medium.com/@anurag4517/a-brief-introduction-of-monitoring-with-datadog-bf88e250b734

[^1_35]: https://cloud.google.com/datadog

[^1_36]: https://www.zabbix.com/documentation/current/en/manual/discovery/network_discovery

[^1_37]: https://www.zabbix.com/documentation/2.0/en/manual/discovery/auto_registration

[^1_38]: https://icwt.cloud/en/vendors/datadog/infrastructure-monitoring/

[^1_39]: https://www.ibm.com/kr-ko/products/instana/infrastructure-monitoring

[^1_40]: https://docs.dynatrace.com/docs/observe/infrastructure-observability/hosts/monitoring-modes/how-effective-is-infrastructure-monitoring-on-its-own

[^1_41]: https://newrelic.com/instant-observability/infrastructure

[^1_42]: https://newrelic.com/blog/news/infrastructure-monitoring-in-preview

[^1_43]: https://github.com/newrelic/docs-website/blob/develop/src/content/docs/infrastructure/introduction-infra-monitoring.mdx

[^1_44]: https://www.youtube.com/watch?v=PDpwGIL5s0U

[^1_45]: https://www.ibm.com/docs/en/instana-observability?topic=started-quick-start-guide


---

# 소프트웨어/하드웨어 모니터링 솔루션 비교 리포트: 인프라 규모별 최적 툴 선정 기준

## 개요

소프트웨어 모니터링과 하드웨어 모니터링은 분리된 영역이 아니라 하나의 운영 가시성 체계로 설계하는 것이 바람직하다. 특히 연구·AI·컴퓨터비전 환경에서는 CPU, 메모리, 스토리지뿐 아니라 GPU, VRAM, ECC 오류, 전력, 온도, 클럭, 프로세스별 GPU 점유까지 함께 수집해야 원인 분석과 성능 튜닝이 가능하다.[^2_1][^2_2][^2_3][^2_4][^2_5][^2_6]

이 리포트는 모니터링 영역을 대분류·중분류·소분류로 세분화하고, 각 분류별 목적과 기능 목록, 상용 및 오픈소스 도구를 정리한 뒤, 인프라 규모별 최적의 선정 기준을 제시한다.[^2_7][^2_8][^2_9]

## 분류 체계

### 대분류

1. 하드웨어 및 물리 인프라 모니터링[^2_8][^2_10]
2. 시스템 및 플랫폼 모니터링[^2_3][^2_7]
3. 애플리케이션 성능 모니터링(APM)[^2_2][^2_11]
4. 로그·메트릭·트레이스 관측성[^2_12][^2_13]
5. 네트워크 및 장비 모니터링[^2_14][^2_8]
6. 사용자 경험 및 합성 테스트[^2_15][^2_3]
7. 보안·운영 자동화·거버넌스 모니터링[^2_16][^2_1]

### 중분류와 소분류

#### 1) 하드웨어 및 물리 인프라 모니터링

- 서버 하드웨어: CPU 소켓, 메모리 DIMM, 팬, PSU, RAID, 디스크, 온도 센서, 전압 레일[^2_10][^2_17]
- 가상화 호스트: ESXi, Hyper-V, KVM 호스트 리소스와 하드웨어 상태[^2_18][^2_3]
- 스토리지: SAN, NAS, Ceph, RAID 어레이, SSD SMART, NVMe 상태[^2_17][^2_19]
- 네트워크 장비: 스위치, 라우터, 방화벽, 무선장비, 포트 상태, 대역폭, 인터페이스 오류[^2_8][^2_14]
- 전원 및 환경: UPS, PDU, 랙 환경 센서, 온습도, 전력 사용량[^2_20][^2_17]
- 관리보드/BMC: iDRAC, iLO, IMM, IPMI, SNMP 기반 하드웨어 텔레메트리[^2_10]
- GPU/AI 가속기: GPU 코어 사용률, VRAM 사용량, 메모리 대역 사용률, ECC 오류, 온도, 전력, 클럭, XID 오류, 프로세스별 점유 메모리[^2_4][^2_5][^2_6]


#### 2) 시스템 및 플랫폼 모니터링

- OS 자원: CPU, 메모리, 스왑, 파일시스템, 프로세스, 서비스 상태[^2_3][^2_7]
- 컨테이너 및 쿠버네티스: 노드, 파드, 컨테이너, 스케줄링, 리소스 할당량[^2_9][^2_21]
- 미들웨어: 웹서버, WAS, 메시지 큐, 캐시, 런타임 VM[^2_11][^2_1]
- 데이터 플랫폼: DBMS, 검색엔진, 스트림 처리, 배치 처리[^2_22][^2_1]


#### 3) 애플리케이션 성능 모니터링(APM)

- 요청 지연시간, 처리량, 오류율[^2_2][^2_11]
- 서비스 의존성 맵[^2_23][^2_9]
- 분산 트레이싱과 병목 분석[^2_13][^2_3]
- 코드 레벨 프로파일링, 예외 추적, 배포 영향 분석[^2_11][^2_2]


#### 4) 관측성

- 메트릭 수집, 시계열 저장, 질의[^2_7]
- 로그 수집, 색인, 검색, 상관분석[^2_12][^2_13]
- 트레이스 수집과 서비스 그래프[^2_13][^2_3]
- 경보, 이벤트 라우팅, 에스컬레이션[^2_24][^2_1]


#### 5) 네트워크 및 장비 모니터링

- SNMP polling, trap, NetFlow/sFlow/IPFIX[^2_14][^2_8]
- 포트별 상태, 인터페이스 에러, 대역폭 추이[^2_8][^2_14]
- 장비 자동 발견, 토폴로지 가시화[^2_25][^2_8]


#### 6) 사용자 경험

- RUM(실사용자 모니터링)[^2_15][^2_3]
- Synthetics(API, 브라우저, 네트워크 경로 테스트)[^2_3][^2_15]


#### 7) 보안·운영·거버넌스

- 변경 감지와 구성 drift 파악[^2_26][^2_22]
- 이상 탐지와 AI 기반 원인 분석[^2_16][^2_2]
- SLA/SLO 관리와 리포팅[^2_1][^2_11]


## GPU를 포함한 하드웨어 모니터링 재정리

GPU는 더 이상 특수 장비가 아니라 AI, HPC, VDI, 비디오 처리, 시뮬레이션 환경의 핵심 인프라 자원이므로 하드웨어 모니터링의 독립 카테고리로 다루는 것이 적절하다. NVIDIA는 NVML을 통해 GPU 식별 정보, GPU 및 메모리 활용률, ECC 오류 수, 온도, 팬 속도, 전력, 활성 프로세스와 프로세스별 할당 메모리, 클럭 및 PState를 조회할 수 있다고 설명한다.[^2_6][^2_4]

### GPU 모니터링 목적

- 학습/추론 작업의 병목 원인 식별, 예: GPU 코어는 한가하지만 VRAM이 부족한 경우[^2_5][^2_6]
- 모델 배치 및 멀티테넌시 환경에서 GPU 과점유, 메모리 단편화, 프로세스 충돌 탐지[^2_5][^2_6]
- 장시간 학습 중 ECC 오류, 온도 과열, 전력 제한, 클럭 저하(throttling) 탐지[^2_27][^2_6]
- Kubernetes 기반 GPU 워크로드의 운영 가시성 확보[^2_21][^2_4]


### GPU 모니터링 세부 기능 목록

- GPU utilization, SM occupancy 성격의 연산 활용률[^2_6][^2_5]
- VRAM total/used/free, memory utilization[^2_5][^2_6]
- GPU temperature, memory temperature(지원 제품), fan speed[^2_6][^2_5]
- Power draw, power limit, persistence mode[^2_27][^2_5]
- ECC single-bit/double-bit error count[^2_27][^2_6]
- Clocks(graphics/memory/video), PState[^2_5][^2_6]
- PCIe link 상태와 전송 특성[^2_5]
- 프로세스별 GPU 사용과 메모리 할당량[^2_6]
- XID 오류, 디바이스 헬스, 진단 정보[^2_28][^2_29]
- 컨테이너/노드별 GPU 할당량과 워크로드별 메트릭 연계[^2_4][^2_21]


### GPU 모니터링 수집 방식

- 단일 서버/워크스테이션: `nvidia-smi` 기반 주기 수집[^2_30][^2_5]
- 프로그래밍 통합: NVML API 기반 사용자 도구 또는 에이전트 개발[^2_6]
- 쿠버네티스/클러스터: NVIDIA DCGM Exporter + Prometheus + Grafana 조합[^2_31][^2_21][^2_4]
- 엔터프라이즈 통합 관제: Datadog, Dynatrace, New Relic, Instana 같은 상용 플랫폼에 GPU 메트릭을 연동[^2_1][^2_2][^2_11]


## 목적별 기능 매트릭스

| 대분류 | 주요 목적 | 핵심 기능 | 대표 오픈소스 | 대표 상용 |
| :-- | :-- | :-- | :-- | :-- |
| 하드웨어/서버 | 물리 장비 장애 예방, 자산 가시성 확보 | CPU, 메모리, 디스크, 팬, PSU, 온도, RAID, BMC/IPMI, SNMP[^2_10][^2_17] | Zabbix[^2_8], LibreNMS[^2_17][^2_14], Nagios/Icinga[^2_19] | Checkmk[^2_10], Datadog[^2_1], Dynatrace[^2_9] |
| GPU/AI 인프라 | 학습·추론 워크로드 안정성 및 비용 최적화 | GPU utilization, VRAM, ECC, power, clocks, process, XID[^2_4][^2_5][^2_6] | DCGM Exporter + Prometheus + Grafana[^2_4][^2_31][^2_21] | Datadog[^2_1], Instana[^2_2], New Relic[^2_11] |
| 시스템/OS | 호스트 운영 상태와 용량 감시 | 프로세스, 서비스, 파일시스템, 커널, 컨테이너[^2_7][^2_3] | Prometheus[^2_7], Zabbix[^2_8], Checkmk Raw[^2_32] | New Relic[^2_22], Datadog[^2_1] |
| APM | 서비스 성능 및 원인 분석 | 응답시간, 오류율, 트레이스, 의존성 맵[^2_2][^2_11] | OpenTelemetry + Jaeger/SigNoz | Dynatrace[^2_9], Instana[^2_2], Datadog[^2_13] |
| 로그/이벤트 | 장애 분석 및 포렌식 | 로그 수집, 검색, 상관분석[^2_12][^2_13] | OpenObserve[^2_12], Loki, ELK | Datadog[^2_13], New Relic[^2_3] |
| 네트워크 | 회선 품질 및 장비 상태 | SNMP, traps, flow, topology[^2_8][^2_14] | LibreNMS[^2_14], Zabbix[^2_8], Cacti | Checkmk[^2_10], Datadog[^2_15] |

## 주요 플랫폼 상세 비교

| 플랫폼 | 유형 | 강점 | 약점/유의점 | 적합한 환경 |
| :-- | :-- | :-- | :-- | :-- |
| Prometheus | 오픈소스 | 메트릭 중심 구조, exporter 생태계, Alertmanager 연동[^2_7][^2_33] | 장비 센서·자산 관리·네트워크 관제는 별도 조합 필요 | 클라우드 네이티브, 쿠버네티스, 개발조직 중심 |
| Zabbix | 오픈소스 | 서버·네트워크·하드웨어를 폭넓게 수집, 자동 발견, SNMP 강점[^2_34][^2_8] | 대규모 분산 환경에서 설계와 튜닝이 중요 | 온프레미스, 하이브리드, 네트워크 장비 많은 조직 |
| LibreNMS | 오픈소스 | 네트워크 장비와 센서 상태 시각화에 강함[^2_17][^2_14] | APM과 애플리케이션 관측성은 제한적 | 네트워크 중심, ISP, 장비 운영팀 |
| Nagios/Icinga | 오픈소스 | 플러그인 다양성, 특정 장비/스토리지 모니터링 확장성[^2_19] | 현대적 관측성 스택 대비 통합 경험이 약함 | 레거시 인프라, 플러그인 중심 운영 |
| Checkmk | 상용/오픈코어 | BMC/IPMI/SNMP 포함 서버 하드웨어 감시에 강함[^2_35][^2_10] | 기능 폭이 넓어 운영 표준화가 필요 | 데이터센터, 온프레미스 중심 엔터프라이즈 |
| Datadog | 상용 SaaS | 인프라, APM, 로그, RUM 통합[^2_1][^2_13] | 호스트/기능별 과금 누적 가능성 | 빠른 구축, 멀티클라우드, DevOps 조직 |
| Dynatrace | 상용 SaaS | 자동 발견, AI 분석, 엔드투엔드 풀스택[^2_16][^2_9] | 비용과 도입 설계가 무거울 수 있음 | 대규모 엔터프라이즈, 복잡한 서비스 의존성 |
| Instana | 상용 SaaS/하이브리드 | 자동 계측, 실시간성, 애플리케이션 맥락 연계[^2_2][^2_23] | 순수 장비 모니터링만 보면 과한 선택일 수 있음 | 마이크로서비스, 대형 애플리케이션 중심 |
| New Relic | 상용 SaaS | 호스트, 쿠버네티스, 로그, APM 통합[^2_22][^2_11] | 운영 모델에 따라 비용 관리 필요 | 클라우드 기반 제품 조직 |
| DCGM Exporter + Grafana | 오픈소스 조합 | GPU 메트릭 표준 수집과 시각화에 최적[^2_4][^2_31][^2_21] | GPU 외 영역은 별도 스택 필요 | AI 연구실, GPU 팜, ML 플랫폼 |

## 인프라 규모별 최적 툴 선정 기준

### 1) 소규모 인프라

소규모는 대체로 서버 수 1~20대, 네트워크 장비 수 제한적, 운영 담당자가 소수이며 예산이 제한된 환경을 의미한다. 이 구간에서는 기능의 절대량보다 설치 단순성, 운영 인력 부담, 기본 경보 품질이 더 중요하다.

권장 기준은 다음과 같다.

- 온프레미스/장비 위주면 Zabbix 또는 Checkmk Raw가 유리하다.[^2_32][^2_8]
- 네트워크 장비 중심이면 LibreNMS가 빠르게 가치가 나온다.[^2_17][^2_14]
- 쿠버네티스/클라우드 중심이면 Prometheus + Grafana가 효율적이다.[^2_33][^2_7]
- GPU 연구 서버가 1~5대 수준이면 `nvidia-smi` 자동 수집 또는 DCGM Exporter 도입이 현실적이다.[^2_4][^2_5]

소규모 최적 조합 예시는 다음과 같다.

- 일반 기업 서버/네트워크: Zabbix.
- 네트워크 운영 집중: LibreNMS.
- 연구실 GPU 서버: Prometheus + DCGM Exporter + Grafana.
- SaaS 스타트업: Datadog 또는 New Relic, 단 비용 관리 전제.[^2_11][^2_1]


### 2) 중규모 인프라

중규모는 보통 서버 수 20~200대, 다수의 VM/컨테이너, 운영팀 분화, 서비스 중요도 상승이 특징이다. 이 구간부터는 메트릭만 보는 체계로는 부족하며 로그, 트레이스, 자동 발견, 권한 분리, 템플릿 표준화가 중요해진다.

권장 기준은 다음과 같다.

- 장비/서버/네트워크 자산 가시성이 중요하면 Zabbix 또는 Checkmk가 유리하다.[^2_10][^2_8]
- 애플리케이션 분석까지 포함하면 Datadog, New Relic, Instana 같은 통합 플랫폼이 관리 효율이 높다.[^2_2][^2_1][^2_11]
- GPU 노드가 10대 이상이면 DCGM Exporter를 표준 수집기로 채택하고, 노드/파드/잡 단위 메타데이터를 함께 저장하는 구조가 적합하다.[^2_21][^2_4]
- 로그 분석 수요가 증가하면 OpenObserve, Loki, ELK 같은 로그 계층을 별도로 추가해야 한다.[^2_12]

중규모 최적 조합 예시는 다음과 같다.

- 하이브리드 인프라: Zabbix + Grafana + OpenObserve.
- 클라우드 네이티브: Prometheus + Grafana + OpenTelemetry + Loki.
- AI 플랫폼: Prometheus + DCGM Exporter + Grafana + 로그 스택.
- 빠른 운영 내재화: Datadog 또는 New Relic.


### 3) 대규모 인프라

대규모는 수백~수천 대 호스트, 다수 리전/클러스터, 마이크로서비스, 다중 팀, 강한 SLA/SLO 요구사항이 있는 환경이다. 이 구간에서는 단순 모니터링 도구보다 데이터 모델, 라벨 체계, 멀티테넌시, 비용 통제, 자동 분석 기능이 중요하다.

권장 기준은 다음과 같다.

- 애플리케이션과 인프라를 함께 자동 상관분석해야 하면 Dynatrace 또는 Instana가 강력하다.[^2_9][^2_16][^2_2]
- 엔터프라이즈 SaaS 기반 통합 운용이 필요하면 Datadog, New Relic이 적합하다.[^2_1][^2_11]
- 비용 및 벤더 종속성 완화가 중요하면 Prometheus 계열을 기반으로 하되, 장기 저장, 연합(federation), 로그/트레이스 통합 설계를 별도로 해야 한다.[^2_33][^2_7]
- GPU 클러스터는 DCGM Exporter를 표준 수집기로 두고, 스케줄러(Kubernetes/Slurm) 메타데이터와 연결하는 것이 필수적이다.[^2_21][^2_4]

대규모 최적 조합 예시는 다음과 같다.

- 엔터프라이즈 통합 관측성: Dynatrace, Instana, Datadog.
- 대형 플랫폼 기업: Prometheus 생태계 + OpenTelemetry + 별도 로그/트레이스 백엔드.
- 대형 AI/HPC: Prometheus + DCGM Exporter + Grafana + 스케줄러/워크로드 메타데이터 + 로그 분석 스택.


## 최종 선정 프레임워크

도구 선정은 단순 기능 비교보다 운영 목표에 따라 판단해야 한다. 다음 질문에 대한 답으로 빠르게 좁힐 수 있다.

1. 주력 대상이 무엇인가: 서버/네트워크/스토리지인가, 애플리케이션인가, 둘 다인가.[^2_2][^2_8]
2. 환경이 어디에 가까운가: 온프레미스, 하이브리드, 멀티클라우드, 쿠버네티스 중심인가.[^2_9][^2_1]
3. GPU가 핵심 자원인가: VRAM, ECC, power, process 단위 추적이 필요한가.[^2_4][^2_5][^2_6]
4. 운영팀 역량은 어느 정도인가: 오픈소스 조합을 직접 운영할 수 있는가, SaaS가 더 적합한가.[^2_36][^2_1]
5. 예산과 라이선스 정책은 어떤가: 초기 CAPEX 절감이 중요한가, 운영 OPEX 예측 가능성이 중요한가.[^2_36][^2_1]
6. 규제와 감사 요구가 있는가: 보존기간, 접근통제, 온프레미스 저장 요구가 있는가.[^2_3][^2_9]

## 권고안

- 레거시 장비와 물리 인프라가 많으면 Zabbix 또는 Checkmk 계열이 기본축으로 적합하다.[^2_8][^2_10]
- 클라우드 네이티브 서비스라면 Prometheus 생태계 또는 Datadog/New Relic 같은 통합 SaaS가 효율적이다.[^2_7][^2_11][^2_1]
- AI 연구·컴퓨터비전·LLM 추론 환경이라면 GPU 모니터링을 별도 항목으로 설계하고, 최소한 VRAM, utilization, temperature, power, ECC, process별 점유를 수집해야 한다.[^2_4][^2_5][^2_6]
- 장비 모니터링과 애플리케이션 모니터링을 별도 운영하지 말고, 장애 원인 분석 관점에서 상호 연계된 대시보드와 경보 체계를 만드는 것이 가장 중요하다[^2_11][^2_1][^2_2]
<span style="display:none">[^2_37][^2_38][^2_39][^2_40][^2_41][^2_42][^2_43][^2_44][^2_45][^2_46][^2_47][^2_48][^2_49]</span>

<div align="center">⁂</div>

[^2_1]: https://www.datadoghq.com/product/infrastructure-monitoring/

[^2_2]: https://www.ibm.com/products/instana/infrastructure-monitoring

[^2_3]: https://docs.newrelic.com/docs/infrastructure/introduction-infra-monitoring/

[^2_4]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^2_5]: https://nvidia.custhelp.com/app/answers/detail/a_id/3751/~/useful-nvidia-smi-queries

[^2_6]: https://developer.nvidia.com/management-library-nvml

[^2_7]: https://prometheus.io/docs/introduction/overview/

[^2_8]: https://www.zabbix.com/network_monitoring

[^2_9]: https://docs.dynatrace.com/docs/observe/infrastructure-observability

[^2_10]: https://checkmk.com/blog/monitoring-management-boards

[^2_11]: https://newrelic.com/platform/infrastructure

[^2_12]: https://openobserve.ai/blog/top-10-open-source-monitoring-tools/

[^2_13]: https://www.datadoghq.com/product/

[^2_14]: https://www.librenms.org/

[^2_15]: https://support.skax.co.kr/ko/support/solutions/articles/42000092519-datadog-소개

[^2_16]: https://www.dynatrace.com/hub/?filter=infrastructure-monitoring

[^2_17]: https://docs.librenms.org/Support/Device-Sensors/

[^2_18]: https://forum.checkmk.com/t/hardware-monitoring/17696

[^2_19]: https://exchange.nagios.org/directory/plugins/hardware/storage-systems/

[^2_20]: https://www.youtube.com/watch?v=jGUIbM09TKc

[^2_21]: https://nvidia.github.io/dcgm-exporter/

[^2_22]: https://newrelic.com/platform/infrastructure/features

[^2_23]: https://www.ibm.com/products/instana

[^2_24]: https://prometheus.io/docs/alerting/latest/

[^2_25]: https://www.zabbix.com/documentation/current/en/manual/discovery/network_discovery

[^2_26]: https://newrelic.com/blog/news/infrastructure-monitoring-in-preview

[^2_27]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html

[^2_28]: https://www.kubenatives.com/p/gpu-monitoring-dcgm-exporter-kubernetes

[^2_29]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html

[^2_30]: https://docs.nvidia.com/deploy/nvidia-smi/index.html

[^2_31]: https://grafana.com/grafana/dashboards/15117-nvidia-dcgm-exporter/

[^2_32]: https://checkmk.com/product/integrations

[^2_33]: https://prometheus.io/docs/instrumenting/exporters/

[^2_34]: https://blog.zabbix.com/handy-tips-38-automating-snmp-item-creation-with-low-level-discovery/23521/

[^2_35]: https://checkmk.com/integrations/openhardwaremonitor_temperature

[^2_36]: https://www.opensourcealternatives.to/blog/best-open-source-monitoring-tools

[^2_37]: https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html

[^2_38]: https://gist.github.com/omerfsen/8ecb620675525ac724a92bdf5a31a4b3

[^2_39]: https://run-ai-docs.nvidia.com/saas/platform-management/monitor-performance/gpu-profiling-metrics

[^2_40]: https://oneuptime.com/blog/post/2026-03-02-how-to-monitor-gpu-usage-with-nvidia-smi-on-ubuntu/view

[^2_41]: https://openobserve.ai/blog/how-to-monitor-nvidia-gpu/

[^2_42]: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/docs/gpu_telemetry.html

[^2_43]: https://docs.librenms.org/Developing/os/Health-Information/

[^2_44]: https://docs.librenms.org/Support/Features/

[^2_45]: https://support.nagios.com/forum/viewtopic.php?t=41381

[^2_46]: https://assets.nagios.com/downloads/nagios-network-analyzer/docs/Nagios-Network-Analyzer-Hardware-Recommendations.pdf

[^2_47]: https://docs.librenms.org/Support/Example-Hardware-Setup/

[^2_48]: https://docs.librenms.org/

[^2_49]: https://checkmk.com/integrations


---

# 인프라 규모별 최적의 모니터링 툴 비교: GPU(VRAM/Core) 및 서버 하드웨어(CPU/RAID) 통합 가이드

## 개요

GPU 중심 인프라와 전통적인 서버 하드웨어 인프라는 모니터링 요구사항이 다르지만, 실제 운영에서는 하나의 통합 관제 체계 안에서 설계해야 한다. GPU 워크로드는 VRAM, GPU core utilization, ECC 오류, 전력, 온도, 프로세스별 점유를 중점적으로 봐야 하고, 서버 하드웨어는 CPU, 메모리, 디스크, RAID, 팬, 전원, 온도, BMC 상태를 중점적으로 봐야 한다.[^3_1][^3_2][^3_3][^3_4][^3_5][^3_6]

이 문서는 다음 다섯 가지 요구를 통합해 정리한다.

- 인프라 규모별 최적의 모니터링 툴 비교[^3_2][^3_7][^3_8]
- GPU/서버 하드웨어 성능 모니터링 체크리스트[^3_4][^3_6][^3_1]
- 인프라 규모별 비용 효율성 비교[^3_9][^3_10][^3_11][^3_12]
- Kubernetes 환경에서 DCGM Exporter 설정 및 성능 최적화[^3_13][^3_1]
- GPU 클러스터 필수 알람 및 장애 대응 정책[^3_14][^3_15][^3_16]


## 모니터링 대상 체계

### GPU 계층

GPU는 단순 가속기가 아니라 독립적인 운영 자원이다. NVIDIA는 NVML과 `nvidia-smi`를 통해 GPU utilization, 메모리 사용량, ECC 오류, 온도, 팬 속도, 전력, 클럭, PState, 활성 프로세스, 프로세스별 할당 메모리를 수집할 수 있다고 설명한다.[^3_5][^3_17][^3_4]

GPU 모니터링의 핵심 항목은 다음과 같다.

- GPU core utilization[^3_4][^3_5]
- VRAM total/used/free 및 memory utilization[^3_5][^3_4]
- Temperature, fan speed, power draw, power limit[^3_16][^3_4]
- ECC single/double bit errors[^3_16][^3_5]
- Clocks, PState, throttling 징후[^3_4][^3_5]
- XID errors 및 디바이스 헬스 진단[^3_15][^3_14]
- Process별 GPU 사용 및 메모리 점유[^3_5]


### 서버 하드웨어 계층

서버 하드웨어는 단순 CPU 사용률만 보는 것이 아니라 물리 상태와 예지보전 정보를 함께 봐야 한다. Checkmk와 LibreNMS 문서는 BMC, iLO, iDRAC, 센서, 온도, 팬, 전원, 스토리지 상태, 장치 health 정보를 수집하는 방식을 설명한다.[^3_3][^3_6]

서버 하드웨어 모니터링의 핵심 항목은 다음과 같다.

- CPU usage, load, core saturation[^3_8][^3_18]
- Memory, swap, NUMA 불균형[^3_18][^3_8]
- Disk latency, IOPS, SMART/NVMe health[^3_6][^3_19]
- RAID controller, array degraded 상태[^3_19][^3_3]
- Fan, PSU, temperature, voltage[^3_3][^3_6]
- NIC throughput, packet error, drop[^3_20][^3_2]
- BMC/IPMI/iDRAC/iLO event[^3_3]


## 인프라 규모별 툴 비교

### 소규모 인프라

소규모는 대체로 1~20대 서버, 제한된 네트워크 장비, 전담 SRE 부재, 예산 제약이 큰 환경이다. 이 구간에서는 도입 속도와 유지보수 난이도가 가장 중요하다.


| 항목 | 권장 도구 | 이유 |
| :-- | :-- | :-- |
| 일반 서버/네트워크 | Zabbix[^3_2] | 서버, 네트워크, SNMP, 자동 발견을 한 플랫폼에서 처리 가능[^3_21][^3_2] |
| 네트워크 중심 | LibreNMS[^3_20] | 장비 자동 발견과 센서/포트 가시화가 강함[^3_6][^3_20] |
| GPU 연구 서버 1~5대 | `nvidia-smi` + Prometheus node_exporter 또는 DCGM Exporter[^3_17][^3_1][^3_4] | 최소 비용으로 VRAM/GPU 상태 확보 가능 |
| 빠른 SaaS 도입 | Grafana Cloud Free/Pro[^3_10] 또는 New Relic Free[^3_12] | 무료/저비용으로 시작 가능 |

소규모에서는 상용 SaaS가 운영 편의성은 높지만, 호스트 수가 적을 때도 기능이 늘면 과금 항목이 빠르게 누적될 수 있다. Datadog은 인프라 모니터링이 연간 약정 기준 호스트당 월 15달러부터 시작하고, APM은 호스트당 월 31달러 수준으로 별도 과금될 수 있다.[^3_22][^3_9]

### 중규모 인프라

중규모는 20~200대 서버, 가상화/컨테이너 혼합, 다수 팀 운영, 로그·트레이스 필요성이 증가한 환경이다. 이 구간부터는 메트릭만 보는 도구보다 로그와 APM 연계성이 중요해진다.


| 항목 | 권장 도구 | 이유 |
| :-- | :-- | :-- |
| 하이브리드 서버/장비 중심 | Zabbix + Grafana + 로그 스택 | 장비/서버 수집과 시각화 분리 운영에 유리[^3_2][^3_23] |
| 네트워크+하드웨어 중심 | Checkmk[^3_3] | BMC, 하드웨어 센서, 장비 가시성 강점[^3_24][^3_3] |
| 클라우드 네이티브 | Prometheus + Grafana + OpenTelemetry | 쿠버네티스와 exporter 생태계가 강함[^3_8][^3_25][^3_13] |
| 빠른 운영 통합 | Datadog[^3_7], New Relic[^3_12] | 인프라, 로그, APM 통합 도입이 빠름 |
| GPU 노드 10대 이상 | DCGM Exporter + Prometheus + Grafana[^3_1][^3_26][^3_13] | GPU 메트릭 표준화와 대시보드 재사용이 용이 |

중규모부터는 비용 효율성을 단순 라이선스가 아니라 운영 인건비까지 포함해 계산해야 한다. 오픈소스는 라이선스 비용이 낮지만 운영 표준화, 스토리지 설계, 업그레이드, 고가용성 구축에 내부 인력이 더 들어간다.[^3_27][^3_8]

### 대규모 인프라

대규모는 수백~수천 호스트, 멀티클러스터, 마이크로서비스, SLA/SLO, 다중 팀 운영이 특징이다. 이 구간에서는 수집량과 원인 분석 속도가 도구 선정의 핵심이다.


| 항목 | 권장 도구 | 이유 |
| :-- | :-- | :-- |
| 엔터프라이즈 풀스택 | Dynatrace[^3_28][^3_11], Instana[^3_29] | 자동 발견, AI 기반 분석, 풀스택 맥락 제공 |
| SaaS 통합 관측성 | Datadog[^3_7][^3_9], New Relic[^3_12] | 제품군 통합과 운영 생산성 강점 |
| 대형 클라우드 네이티브 | Prometheus 생태계 + OpenTelemetry | 벤더 종속성 완화, 유연한 설계 가능[^3_8][^3_25] |
| 대형 GPU/AI 클러스터 | DCGM Exporter + Prometheus + Grafana + 스케줄러 메타데이터[^3_1][^3_13] | GPU 노드/잡/파드 상관분석에 적합 |

Dynatrace는 호스트 크기와 무관하게 인프라 모니터링이 시간당 과금되는 구조를 제시하며, Foundation \& Discovery와 Full-Stack Monitoring도 별도 단가를 제공한다. 따라서 대규모에서는 단가 자체보다 “어떤 기능을 어느 계층까지 활성화할 것인가”가 비용 설계의 핵심이 된다.[^3_11][^3_30]

## 성능 모니터링 체크리스트

### GPU 체크리스트

| 항목 | 필수 여부 | 기준 예시 | 목적 |
| :-- | :-- | :-- | :-- |
| GPU utilization | 필수 | 평균 90% 이상 장기 지속 또는 10% 이하 장기 지속[^3_4][^3_5] | 과소/과대 활용 탐지 |
| VRAM used/free | 필수 | 사용률 90% 초과, OOM 빈발[^3_4][^3_5] | 메모리 병목 탐지 |
| ECC errors | 필수(데이터센터 GPU) | 1회 이상 증가 시 조사[^3_16][^3_5] | 하드웨어 안정성 확인 |
| Temperature | 필수 | 임계값 접근 시 경보[^3_4][^3_5] | 과열 방지 |
| Power draw/power cap | 필수 | cap 근접 지속 시 조사[^3_16] | 전력 제한 병목 확인 |
| XID errors | 필수 | 즉시 알람[^3_14][^3_15] | 장애 조기 탐지 |
| Process별 메모리 점유 | 필수 | 비정상 점유/메모리 누수 탐지[^3_5] | 사용자별 원인 분석 |

### 서버 하드웨어 체크리스트

| 항목 | 필수 여부 | 기준 예시 | 목적 |
| :-- | :-- | :-- | :-- |
| CPU usage/load | 필수 | 피크 시간 장기 80% 초과[^3_8][^3_18] | 용량 계획 |
| Memory/swap | 필수 | swap 사용 증가, reclaim 급증[^3_8][^3_18] | 성능 저하 방지 |
| Disk latency/IOPS | 필수 | 지연 급증, 큐 적체[^3_19] | 스토리지 병목 파악 |
| RAID degraded | 필수 | 즉시 알람[^3_19][^3_3] | 데이터 손실 예방 |
| Fan/PSU/temp | 필수 | 센서 abnormal 시 즉시 경보[^3_6][^3_3] | 물리 장애 예방 |
| NIC error/drop | 필수 | 인터페이스 오류 증가[^3_2][^3_20] | 네트워크 이상 탐지 |
| BMC/iDRAC/iLO event | 권장 | critical 이벤트 발생[^3_3] | 운영 선제 대응 |

## 비용 효율성 비교

### 비용 모델별 차이

관측성 도구의 비용은 단순 호스트 수가 아니라 호스트, 메트릭 시계열, 로그 GB, 트레이스 양, 세션 수, 컨테이너/파드 시간 등 다양한 과금 축으로 구성된다. 따라서 GPU 클러스터처럼 메트릭 종류가 많고 로그가 큰 환경은 “기본 호스트 가격”만 보고 선정하면 실제 비용을 과소평가하기 쉽다.[^3_10][^3_12][^3_9][^3_11]


| 플랫폼 | 기본 비용 구조 | 비용상 강점 | 비용상 유의점 |
| :-- | :-- | :-- | :-- |
| Zabbix | 라이선스 비용 없음 | 초기 라이선스 절감 | 운영 인건비와 스토리지 설계 부담 |
| Prometheus + Grafana OSS | 라이선스 비용 없음 | GPU/서버 혼합 수집에 유연 | 장기보관, HA, 운영 자동화 비용 발생[^3_8][^3_25] |
| Grafana Cloud | Free, Pro는 월 19달러 플랫폼 fee + 사용량 과금[^3_10] | 소규모 시작 비용 낮음 | active series와 logs/traces 증가 시 비용 상승[^3_10][^3_31] |
| New Relic | 월 100GB 무료 ingest, 초과분 GB당 0.40달러[^3_12] | 데이터 기반 단순 모델 | 고빈도 로그 환경에서 급증 가능 |
| Datadog | 인프라 호스트당 월 15달러부터, APM은 호스트당 월 31달러 수준[^3_9][^3_22] | 운영 통합과 빠른 도입 | 기능 확장 시 누적 과금이 큼 |
| Dynatrace | 호스트/메모리 GiB/시간 단위 과금[^3_11] | 대규모에서 정교한 사용량 기반 설계 가능 | 기능 조합 이해가 복잡할 수 있음 |

### 규모별 비용 효율성 판단

- 소규모: 무료 티어 또는 오픈소스가 일반적으로 가장 유리하다.[^3_12][^3_10]
- 중규모: 운영 인력 비용을 포함하면 Datadog/New Relic/Grafana Cloud가 오히려 총소유비용(TCO)에서 경쟁력이 생길 수 있다.[^3_9][^3_10][^3_12]
- 대규모: 수집량 통제가 되지 않으면 SaaS 비용이 크게 상승하므로, 메트릭/로그 샘플링과 보존정책이 필수다.[^3_31][^3_11][^3_12]


## Kubernetes에서 DCGM Exporter 설정 가이드

DCGM Exporter는 Kubernetes 클러스터에서 GPU 텔레메트리를 수집하기 위한 NVIDIA 공식 경로다. NVIDIA는 Helm 차트를 제공하며, Prometheus와 Grafana를 함께 구성하는 방법을 안내한다.[^3_1][^3_13]

### 기본 설정 절차

1. GPU 노드에 NVIDIA 드라이버와 컨테이너 런타임 지원을 준비한다.[^3_13][^3_1]
2. Helm 저장소를 추가한다.[^3_13]
3. `gpu-helm-charts/dcgm-exporter` 차트를 설치한다.[^3_13]
4. Prometheus가 exporter endpoint를 스크레이프하도록 ServiceMonitor 또는 scrape 설정을 추가한다.[^3_1][^3_13]
5. Grafana 대시보드를 연결해 GPU utilization, memory, temperature, power 지표를 시각화한다.[^3_26][^3_13]

### 성능 최적화 기준

- 모든 메트릭을 무조건 수집하지 말고 운영 목적에 맞는 지표만 활성화한다. GPU 노드 수가 커질수록 시계열 수가 급격히 증가할 수 있다.[^3_10][^3_1]
- scrape interval은 15초 또는 30초부터 시작하고, 초단위 고빈도 수집은 장애 분석 목적이 명확할 때만 적용한다.[^3_1]
- 파드/잡/노드 라벨 체계를 정리해 VRAM 사용량과 실제 워크로드를 연결해야 한다.[^3_1][^3_13]
- Prometheus 보존기간과 remote write 정책을 분리해 최근 상세 데이터와 장기 추세 데이터를 나눠 관리하는 것이 효율적이다.[^3_8][^3_10]
- 고카디널리티 라벨을 제한해 비용과 성능 문제를 줄인다.[^3_31][^3_10]


## GPU 클러스터 필수 알람 정책

GPU 클러스터에서는 단순 임계치 알람만으로는 부족하며, 장애 유형별 정책이 필요하다. NVIDIA 문서는 ECC, diagnostics, device health, XID 관련 진단 정보를 제공하며, 실무에서는 이를 운영 정책으로 연결해야 한다.[^3_14][^3_15][^3_16]

### 필수 알람

- GPU down 또는 exporter 미수집 감지[^3_1]
- VRAM 사용률 장기 고점 유지[^3_4][^3_5]
- GPU utilization 장기 저활용 또는 비정상 고활용[^3_5][^3_4]
- ECC error 증가[^3_16][^3_5]
- Temperature 과열 또는 fan anomaly[^3_4][^3_5]
- Power cap 지속 근접[^3_16]
- XID error 즉시 감지[^3_15][^3_14]
- RAID degraded, PSU/fan failure, BMC critical event[^3_6][^3_19][^3_3]


### 대응 정책

| 장애 유형 | 1차 조치 | 2차 조치 | 에스컬레이션 |
| :-- | :-- | :-- | :-- |
| VRAM 부족/OOM | 잡 종료 여부 확인, 배치 크기 축소 | 스케줄링 정책 조정 | ML 플랫폼 담당자 |
| GPU 온도/전력 이상 | 냉각/전원 상태 확인 | 노드 cordon 또는 작업 이동 | 인프라 운영팀 |
| ECC/XID 오류 | GPU reset 가능 여부 검토 | 노드 격리 및 정밀 진단[^3_14][^3_16] | 하드웨어 벤더/데이터센터 |
| RAID degraded | 즉시 장애 티켓 발행 | 디스크 교체 및 rebuild | 스토리지/서버 운영팀 |
| exporter 데이터 미수집 | Pod 상태, daemonset, 드라이버 확인 | 노드 재등록 또는 exporter 재배포 | 플랫폼 운영팀 |

## 최종 권고안

- 소규모 GPU 연구실은 Prometheus + DCGM Exporter + Grafana 또는 Grafana Cloud Free/Pro가 가장 실용적이다.[^3_10][^3_13]
- 전통적인 서버 하드웨어 중심 조직은 Zabbix 또는 Checkmk가 CPU, RAID, 센서, BMC까지 묶어 보기 좋다.[^3_2][^3_3]
- 중대형 AI 플랫폼은 GPU 텔레메트리와 서버 하드웨어 상태를 한 대시보드에서 함께 보고, 애플리케이션 관측성은 별도 계층으로 확장하는 것이 바람직하다.[^3_7][^3_29][^3_1]
- 비용 효율성은 도구 라이선스보다 데이터 수집량 통제, 메트릭 카디널리티 관리, 로그 보존 정책, 운영 자동화 수준에서 크게 갈린다[^3_11][^3_12][^3_10]
<span style="display:none">[^3_32][^3_33][^3_34][^3_35][^3_36][^3_37][^3_38][^3_39][^3_40][^3_41][^3_42][^3_43][^3_44][^3_45][^3_46][^3_47][^3_48][^3_49][^3_50][^3_51][^3_52]</span>

<div align="center">⁂</div>

[^3_1]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^3_2]: https://www.zabbix.com/network_monitoring

[^3_3]: https://checkmk.com/blog/monitoring-management-boards

[^3_4]: https://nvidia.custhelp.com/app/answers/detail/a_id/3751/~/useful-nvidia-smi-queries

[^3_5]: https://developer.nvidia.com/management-library-nvml

[^3_6]: https://docs.librenms.org/Support/Device-Sensors/

[^3_7]: https://www.datadoghq.com/product/infrastructure-monitoring/

[^3_8]: https://prometheus.io/docs/introduction/overview/

[^3_9]: https://www.getpricepulse.com/companies/datadog-pricing.html

[^3_10]: https://grafana.com/pricing/

[^3_11]: https://www.dynatrace.com/pricing/rate-card/

[^3_12]: https://newrelic.com/pricing

[^3_13]: https://nvidia.github.io/dcgm-exporter/

[^3_14]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html

[^3_15]: https://www.kubenatives.com/p/gpu-monitoring-dcgm-exporter-kubernetes

[^3_16]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html

[^3_17]: https://docs.nvidia.com/deploy/nvidia-smi/index.html

[^3_18]: https://docs.newrelic.com/docs/infrastructure/introduction-infra-monitoring/

[^3_19]: https://exchange.nagios.org/directory/plugins/hardware/storage-systems/

[^3_20]: https://www.librenms.org/

[^3_21]: https://blog.zabbix.com/handy-tips-38-automating-snmp-item-creation-with-low-level-discovery/23521/

[^3_22]: https://last9.io/blog/datadog-pricing-all-your-questions-answered/

[^3_23]: https://openobserve.ai/blog/top-10-open-source-monitoring-tools/

[^3_24]: https://checkmk.com/integrations/openhardwaremonitor_temperature

[^3_25]: https://prometheus.io/docs/instrumenting/exporters/

[^3_26]: https://grafana.com/grafana/dashboards/15117-nvidia-dcgm-exporter/

[^3_27]: https://www.opensourcealternatives.to/blog/best-open-source-monitoring-tools

[^3_28]: https://docs.dynatrace.com/docs/observe/infrastructure-observability

[^3_29]: https://www.ibm.com/products/instana/infrastructure-monitoring

[^3_30]: https://www.dynatrace.com/pricing/

[^3_31]: https://grafana.com/docs/grafana-cloud/cost-management-and-billing/analyze-costs/logs-costs/

[^3_32]: https://vendorbenchmark.com/blog/datadog-pricing-benchmark-per-host-module

[^3_33]: https://hyperping.com/blog/datadog-pricing

[^3_34]: https://www.opslyft.com/blog/datadog-pricing

[^3_35]: https://www.spendhound.com/marketplace/datadog-pricing

[^3_36]: https://monitoringcost.com/datadog-pricing

[^3_37]: https://dev.to/khushi_dubey/datadog-pricing-in-2026-166l

[^3_38]: https://cubeapm.com/pricing-calculator/datadog/

[^3_39]: https://www.finout.io/blog/datadog-pricing-explained

[^3_40]: https://signoz.io/blog/datadog-pricing/

[^3_41]: https://checkthat.ai/brands/datadog/pricing

[^3_42]: https://www.motadata.com/blog/datadog-pricing

[^3_43]: https://frontdeskreview.com/software/observability-apm/grafana-cloud/

[^3_44]: https://www.cloudzero.com/blog/grafana-cloud-pricing/

[^3_45]: https://grafana.com/docs/grafana-cloud/monitor-applications/application-observability/pricing/

[^3_46]: https://monitoringcost.com/grafana-cloud-pricing

[^3_47]: https://cubeapm.com/blog/grafana-cloud-pricing-and-review/

[^3_48]: https://pricingapis.com/monitoring/grafana-cloud

[^3_49]: https://www.vendr.com/marketplace/grafana

[^3_50]: https://www.stackscored.com/pricing/observability/grafana-cloud/

[^3_51]: https://dev.to/beton/grafana-pricing-teardown-2026-ic

[^3_52]: https://aws.amazon.com/marketplace/pp/prodview-abqxd6uqqpsju


---

# 비용 효율적인 모니터링 툴 선정: 소규모 vs 엔터프라이즈 인프라 규모별 비교표 및 비용 최적화 전략

국내 기업 환경 기준 모니터링 툴 제품별 Shortlist 추천
Prometheus vs Zabbix vs Datadog vs Dynatrace 아키텍처 비교
GPU 모니터링 데이터 시각화를 위한 Grafana 대시보드 템플릿 구성

요청하신 항목을 **한 번에 활용 가능한 실무형 정리**로 구성했습니다. 특히 소규모 vs 엔터프라이즈 비교, 국내 기업 환경 Shortlist, Prometheus/Zabbix/Datadog/Dynatrace 아키텍처 비교, GPU Grafana 대시보드 템플릿 구성을 함께 묶어 정리하는 것이 핵심입니다.

## 비용 효율성 기준

소규모 인프라에서는 라이선스보다 **운영 단순성**이 더 중요하고, 엔터프라이즈에서는 **수집량, 로그/트레이스량, 보존 정책, 자동화 수준**이 총비용을 좌우합니다.[^4_1][^4_2][^4_3]
GPU 환경은 일반 서버보다 메트릭 종류가 많아 비용이 더 빨리 증가하므로, VRAM/Core/ECC/XID와 같은 핵심 항목만 우선 수집하고 나머지는 단계적으로 확장하는 방식이 유리합니다.[^4_4][^4_5][^4_6]

## 소규모 vs 엔터프라이즈

| 구분 | 소규모 | 엔터프라이즈 |
| :-- | :-- | :-- |
| 우선순위 | 설치 단순성, 빠른 가시화 | 통합 관측성, 자동 분석, 권한/보존 관리 |
| 추천 조합 | Zabbix, LibreNMS, Prometheus + Grafana | Datadog, Dynatrace, New Relic, Prometheus 생태계 |
| GPU 대응 | DCGM Exporter + Grafana | DCGM Exporter + 통합 SaaS 또는 대형 Prometheus 스택 |
| 비용 특성 | 초기 비용 낮음 | 기능 확장에 따라 급증 가능 |
| 운영 포인트 | 템플릿/알람 최소화 | 카디널리티·보존·샘플링 관리 |

Zabbix는 SNMP, LLD, 하드웨어 센서, 네트워크 장비 자동 발견에 강하고, Prometheus는 exporter 기반 메트릭 수집과 Kubernetes 연동에 강합니다.[^4_7][^4_8][^4_9][^4_10][^4_11]
Datadog은 호스트당 과금 기반의 인프라 모니터링과 APM/로그 통합이 강점이고, Dynatrace는 자동 발견과 AI 기반 분석, 엔터프라이즈 수준의 통합 관측성이 강점입니다.[^4_12][^4_13][^4_2][^4_14][^4_15]

## 국내 기업 Shortlist

국내 기업 환경에서는 보통 다음처럼 나누는 것이 가장 현실적입니다.

- **온프레미스/규제 산업**: Zabbix, Checkmk, Dynatrace[^4_16][^4_12][^4_7]
- **클라우드 네이티브/플랫폼 조직**: Prometheus + Grafana + OpenTelemetry, Datadog, New Relic[^4_3][^4_10][^4_11]
- **GPU/AI 연구 조직**: Prometheus + DCGM Exporter + Grafana, 필요 시 Grafana Cloud GPU Observability[^4_17][^4_18][^4_4]
- **네트워크/장비 중심 운영팀**: LibreNMS, Zabbix[^4_19][^4_20][^4_7]
- **빠른 도입이 중요한 조직**: Datadog, Dynatrace, Instana[^4_21][^4_22][^4_12]

국내 GPU Kubernetes 환경 구축 사례도 NVIDIA DCGM Exporter + Helm + Prometheus + Grafana 조합으로 정리되어 있고, KakaoCloud와 OpenShift 문서에서도 같은 방향을 제시합니다.[^4_23][^4_24][^4_25]

## 아키텍처 비교

| 항목 | Prometheus | Zabbix | Datadog | Dynatrace |
| :-- | :-- | :-- | :-- | :-- |
| 수집 방식 | Pull/exporter 중심 [^4_10][^4_11] | Agent/SNMP/IPMI/템플릿 혼합 [^4_7][^4_9] | SaaS 에이전트 중심 [^4_21] | 자동 발견 + 에이전트 + AI 분석 [^4_12][^4_13] |
| GPU 적합성 | 매우 높음, DCGM Exporter와 궁합 우수 [^4_4][^4_18] | 보조적, 하드웨어 관제에 강함 [^4_7][^4_19] | 높음, 통합 관측성 포함 [^4_21][^4_26] | 높음, 엔터프라이즈 분석 강점 [^4_12][^4_13] |
| 서버 하드웨어 | 보완 필요 | 강함 | 강함 | 강함 |
| 운영 난이도 | 중~상 | 중 | 낮음 | 낮음~중 |
| 비용 구조 | 오픈소스, 운영비 중심 | 오픈소스/저비용 | 호스트·기능 기반 과금 | 사용량/시간 기반 과금 [^4_2][^4_3] |

실무적으로는 **GPU 중심이면 Prometheus 계열**, **서버/네트워크/센서 중심이면 Zabbix/Checkmk**, **통합 관측성과 빠른 도입이면 Datadog/Dynatrace/New Relic**이 가장 명확한 구분 기준입니다.[^4_2][^4_12][^4_7][^4_4]

## 비용 최적화 전략

비용 최적화는 단순히 저렴한 제품을 고르는 문제가 아니라, **데이터를 얼마나 적게, 그러나 충분히, 수집할 것인가**의 문제입니다.[^4_27][^4_1][^4_2]
특히 GPU 클러스터에서는 메트릭 카디널리티와 로그 양이 급증하기 쉬우므로, 다음 원칙이 중요합니다.

- 필수 메트릭만 먼저 수집하기.
- GPU는 utilization, VRAM, temperature, power, ECC, XID부터 시작하기.[^4_5][^4_6][^4_28]
- scrape interval을 너무 촘촘하게 잡지 않기.
- 장기 보존 데이터와 운영 실시간 데이터를 분리하기.
- 노드/파드/잡 라벨 체계를 정리해 불필요한 고카디널리티를 줄이기.
- SaaS는 무료 티어/기본 티어에서 시작해 사용량 증가를 관찰하기.[^4_1][^4_3]


## GPU Grafana 템플릿

GPU 모니터링 대시보드는 다음 6개 영역으로 나누면 가장 실용적입니다.

1. **Overview**
    - 노드별 GPU 수.
    - GPU utilization.
    - VRAM 사용량.
    - 온도와 전력.
2. **Per GPU**
    - Core utilization.
    - VRAM used/free.
    - Clock, PState.
    - ECC, XID.
3. **Process View**
    - 프로세스별 GPU 메모리 점유.
    - compute pid.
    - job correlation.
4. **Cluster View**
    - 노드별 가용 GPU.
    - MIG/partition 상태.
    - 스케줄링 상태.
5. **Alert View**
    - exporter down.
    - ECC/XID.
    - thermal/power alarm.
6. **Efficiency View**
    - utilization 대비 VRAM.
    - idle time.
    - underutilization.

NVIDIA의 DCGM Exporter 대시보드는 이런 구조의 출발점으로 적절하고, OpenShift와 KakaoCloud 문서도 Grafana 연결과 GPU 시각화를 직접 안내합니다.[^4_29][^4_25][^4_23][^4_17]

## 권장 결론

- **소규모**: Zabbix 또는 Prometheus + Grafana.
- **GPU 연구 환경**: Prometheus + DCGM Exporter + Grafana.
- **온프레미스 장비 비중 높음**: Zabbix 또는 Checkmk.
- **엔터프라이즈 통합 관측성**: Datadog, Dynatrace, New Relic.
- **비용 최적화 핵심**: 메트릭 수집 범위와 보존 정책 제어.

원하시면 다음 단계로 **국내 기업 도입용 비교표를 “제품별 점수표(기능/비용/운영난이도/GPU 적합도)” 형태로 수치화**해서 정리해 드리겠습니다.
<span style="display:none">[^4_30][^4_31][^4_32][^4_33][^4_34][^4_35][^4_36][^4_37][^4_38][^4_39][^4_40][^4_41][^4_42][^4_43][^4_44][^4_45][^4_46][^4_47][^4_48][^4_49][^4_50][^4_51][^4_52][^4_53][^4_54][^4_55][^4_56][^4_57][^4_58][^4_59][^4_60][^4_61][^4_62][^4_63]</span>

<div align="center">⁂</div>

[^4_1]: https://grafana.com/pricing/

[^4_2]: https://www.dynatrace.com/pricing/rate-card/

[^4_3]: https://newrelic.com/pricing

[^4_4]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^4_5]: https://nvidia.custhelp.com/app/answers/detail/a_id/3751/~/useful-nvidia-smi-queries

[^4_6]: https://developer.nvidia.com/management-library-nvml

[^4_7]: https://www.zabbix.com/network_monitoring

[^4_8]: https://blog.zabbix.com/handy-tips-38-automating-snmp-item-creation-with-low-level-discovery/23521/

[^4_9]: https://assets.zabbix.com/files/Brochures/Zabbix_Product_brochure.pdf

[^4_10]: https://prometheus.io/docs/introduction/overview/

[^4_11]: https://prometheus.io/docs/instrumenting/exporters/

[^4_12]: https://docs.dynatrace.com/docs/observe/infrastructure-monitoring

[^4_13]: https://www.dynatrace.com/platform/infrastructure-observability/

[^4_14]: https://www.getpricepulse.com/companies/datadog-pricing.html

[^4_15]: https://last9.io/blog/datadog-pricing-all-your-questions-answered/

[^4_16]: https://checkmk.com/blog/monitoring-management-boards

[^4_17]: https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/gpu-observability/setup/

[^4_18]: https://nvidia.github.io/dcgm-exporter/

[^4_19]: https://docs.librenms.org/Support/Device-Sensors/

[^4_20]: https://www.librenms.org/

[^4_21]: https://www.datadoghq.com/product/infrastructure-monitoring/

[^4_22]: https://www.ibm.com/products/instana/infrastructure-monitoring

[^4_23]: https://docs.nvidia.com/datacenter/cloud-native/openshift/24.9.2/enable-gpu-monitoring-dashboard.html

[^4_24]: https://docs.kakaocloud.com/tutorial/observability/nvidia-gpu-monitoring

[^4_25]: https://docs.kakaocloud.com/en/tutorial/observability/nvidia-gpu-monitoring

[^4_26]: https://support.skax.co.kr/ko/support/solutions/articles/42000092519-datadog-소개

[^4_27]: https://grafana.com/docs/grafana-cloud/cost-management-and-billing/analyze-costs/logs-costs/

[^4_28]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html

[^4_29]: https://grafana.com/grafana/dashboards/24450-nvidia-dcgm-exporter-dashboard/

[^4_30]: https://dev.to/murajo/visualizing-gpu-metrics-with-dcgm-exporter-1268

[^4_31]: https://highitking.com/📊-gpu-모니터링-대시보드-grafana와-dcgm으로-엔비디아-지표-시/

[^4_32]: https://grafana.com/grafana/dashboards/14478-nvidia-geforce-gpu-monitoring/

[^4_33]: https://github.com/AuraAiLab/GrafanaDashboards

[^4_34]: https://support.huaweicloud.com/intl/en-us/bestpractice-cce/cce_bestpractice_10061.html

[^4_35]: https://grafana.com/grafana/dashboards/14574-nvidia-gpu-metrics/

[^4_36]: https://docs.redhat.com/ko/documentation/red_hat_openshift_ai_self-managed/3.0/html/managing_and_monitoring_models/using_grafana_to_monitor_model_performance

[^4_37]: https://grafana.com/grafana/dashboards/22515-nvidia-dcgm-dashboard/

[^4_38]: https://yandex.cloud/en/docs/stackland/concepts/cluster-monitoring/nvidia-dcgm-mig-monitoring

[^4_39]: https://jorgedelacruz.uk/2021/05/24/looking-for-the-perfect-dashboard-influxdb-telegraf-and-grafana-part-xxxv-gpu-monitoring/

[^4_40]: https://www.getapp.fr/directory/3830/esg/software

[^4_41]: https://www.zabbix.com/integrations/snmp

[^4_42]: https://www.zabbix.com/features

[^4_43]: https://www.zabbix.com/documentation/8.0/en/manual/discovery/network_discovery

[^4_44]: https://www.dynatrace.com/hub/?filter=infrastructure-monitoring

[^4_45]: https://www.zabbix.com/capabilities

[^4_46]: https://en.wikipedia.org/wiki/Zabbix

[^4_47]: https://www.youtube.com/watch?v=QENVJ2IXFT8

[^4_48]: https://www.youtube.com/watch?v=H5iV6cyq3Rk

[^4_49]: https://techexpert.tips/de/zabbix-de/zabbix-automatische-erkennung-mit-snmp/

[^4_50]: https://www.oreilly.com/library/view/zabbix-4-network/9781789340266/883f3334-103e-4bcd-bbe0-405e174ab1ce.xhtml

[^4_51]: https://docs.kakaocloud.com/en/service/ai-service/ai-insight/how-to-guides/ai-insight-install-exporter

[^4_52]: https://docs.kakaocloud.com/service/ai-service/ai-insight/how-to-guides/ai-insight-install-exporter

[^4_53]: https://docs.kakaocloud.com/en/tutorial/observability

[^4_54]: https://developer.nvidia.com/blog/monitoring-gpus-in-kubernetes-with-dcgm/

[^4_55]: https://developer.nvidia.com/blog/get-real-time-visibility-into-gpu-usage-across-kubernetes-clusters/

[^4_56]: https://blog.naver.com/n_cloudplatform/224019964261?fromRss=true\&trackingCode=rss

[^4_57]: https://guide.ncloud-docs.com/docs/en/k8s-k8suse-gpu-node

[^4_58]: https://velog.io/@kjyggg/K8s-환경에서-NVIDIA-GPU-모니터링

[^4_59]: https://cloud.google.com/kubernetes-engine/distributed-cloud/bare-metal/docs/how-to/gpu-metrics?hl=ko

[^4_60]: https://blog.dudaji.com/gtx-rtx-geuraepigkadeuro-guseongdoen-kubeonetiseu-keulreoseuteoe-nvidia-dcgm-exporter-sayonghagi/

[^4_61]: https://docs.kakaocloud.com/tutorial/container/k8se-nvidia-gpu-worknode

[^4_62]: https://docs.nvidia.com/datacenter/cloud-native/gpu-telemetry/latest/index.html

[^4_63]: https://tech.ktcloud.com/entry/GPU-1000장-모니터링-하기-NVIDIA-DCGM-활용-전략


---

# 엔터프라이즈 모니터링 아키텍처 비교: Prometheus, Zabbix, Datadog, Dynatrace의 장단점 및 비용 모델 분석

GPU 모니터링 자동화 가이드: DCGM 및 Grafana를 활용한 VRAM/Core 활용률 시각화 대시보드 템플릿 배포
제품별 점수표 기반 모니터링 솔루션 선정 가이드
GPU 모니터링 시 수집 항목 우선순위 및 적정 보존 주기
Prometheus 고가용성 확보를 위한 Thanos 또는 Cortex 아키텍처 비교

아래는 요청하신 5개 주제를 하나의 실무 관점으로 묶어 정리한 결과입니다. 핵심은 **GPU/서버 하드웨어를 포함한 엔터프라이즈 모니터링 아키텍처 선택**, **GPU 텔레메트리 자동화**, **제품 점수표 기반 선정**, **GPU 메트릭 보존 정책**, **Prometheus 고가용성 확장 구조**입니다.[^5_1][^5_2][^5_3][^5_4][^5_5]

## 아키텍처 비교

Prometheus는 Pull 기반 exporter 모델이라 Kubernetes와 GPU 텔레메트리에 매우 잘 맞고, DCGM Exporter와 결합하면 GPU utilization, framebuffer memory, temperature, power, tensor core 활용률 같은 지표를 직접 수집할 수 있습니다. Zabbix는 SNMP, LLD, BMC/IPMI, 네트워크 장비와 서버 하드웨어 센서에 강하고, Datadog과 Dynatrace는 SaaS 형태로 인프라, 로그, APM, 자동 발견, AI 기반 분석을 묶어 운영 단순성이 높습니다.[^5_1][^5_2][^5_3][^5_4][^5_6][^5_7][^5_8][^5_9][^5_10]

Dynatrace는 동적 환경의 continuous discovery, 자동 원인 분석, remediation 연계를 강하게 내세우고 있습니다. 반면 Prometheus 계열은 유연성과 표준성이 강하지만 운영자가 수집/저장/보존/고가용성까지 직접 설계해야 합니다.[^5_11][^5_2][^5_6]

## 비용 모델

비용 관점에서는 오픈소스가 “라이선스 0원”이라도 운영비가 존재하고, SaaS는 빠르게 도입할 수 있지만 사용량이 늘수록 비용이 증가합니다. Datadog은 인프라 모니터링이 호스트당 월 15달러 수준부터 시작하고, APM과 로그가 붙으면 누적 비용이 빠르게 커질 수 있습니다. Grafana Cloud는 무료/프로 티어가 있으나 active series, logs, traces, profiling 같은 사용량 축으로 비용이 증가하며, New Relic도 ingest 기반 과금 구조를 갖습니다.[^5_5][^5_12][^5_13][^5_14][^5_15][^5_16]

### 점수표 기반 선정 기준

| 항목 | Prometheus | Zabbix | Datadog | Dynatrace |
| :-- | :-- | :-- | :-- | :-- |
| GPU 적합성 | 5 | 2 | 4 | 4 |
| 서버 하드웨어 | 3 | 5 | 4 | 5 |
| Kubernetes 적합성 | 5 | 3 | 4 | 4 |
| 운영 단순성 | 3 | 3 | 5 | 5 |
| 비용 예측 가능성 | 4 | 4 | 2 | 2 |
| 확장성 | 5 | 4 | 5 | 5 |
| 자동 분석 | 2 | 2 | 4 | 5 |

점수는 “가성비”를 단순 가격이 아니라 **운영 인력 비용 포함 총소유비용(TCO)** 기준으로 보는 것이 중요합니다.[^5_5][^5_12][^5_13]

## 제품별 Shortlist

국내 기업 환경 기준으로는 다음 조합이 가장 현실적입니다.

- **온프레미스/규제 산업**: Zabbix, Checkmk, Dynatrace[^5_3][^5_17]
- **클라우드 네이티브/플랫폼 조직**: Prometheus + Grafana + OpenTelemetry, Datadog, New Relic[^5_2][^5_6][^5_13]
- **GPU/AI 연구 조직**: Prometheus + DCGM Exporter + Grafana, Grafana Cloud GPU Observability[^5_4][^5_18][^5_19]
- **네트워크/장비 중심 운영팀**: LibreNMS, Zabbix[^5_20][^5_21]
- **엔터프라이즈 자동화/AI 분석 중시**: Dynatrace, Datadog, Instana[^5_9][^5_22]

국내 클라우드 문서도 GPU Kubernetes 환경을 DCGM Exporter와 Grafana로 구성하는 방식을 제시하고 있으므로, GPU 연구/서비스 환경에서는 이 경로가 가장 자연스럽습니다.[^5_23][^5_24][^5_25]

## GPU 수집 우선순위

GPU 모니터링에서는 모든 항목을 한 번에 수집하기보다 우선순위를 둬야 합니다. NVIDIA DCGM과 `nvidia-smi`가 지원하는 항목 중 실제 운영에서 가장 중요한 것은 GPU utilization, VRAM used/free, temperature, power, ECC errors, XID errors, process별 메모리 점유입니다.[^5_1][^5_26][^5_27][^5_28][^5_29]

### 우선순위

1. **필수 1순위**: GPU utilization, VRAM used/free, temperature, power, XID.[^5_1][^5_27][^5_28][^5_29]
2. **필수 2순위**: ECC error, clocks, PState, process별 점유, memory bandwidth 계열.[^5_27][^5_28][^5_29]
3. **권장 3순위**: PCIe, fan speed, profiling metrics, MIG 세부값.[^5_30][^5_31][^5_28]

### 적정 보존 주기

- 실시간 운영 대시보드용 고해상도 메트릭: 짧게, 보통 수일~수주 단위.
- 용량 계획 및 트렌드 분석용 메트릭: 수개월 보존.
- GPU 장애 분석용 상세 데이터: ECC/XID, 온도, 전력, VRAM은 최소 30일 이상이 실무적으로 유용.
- 고카디널리티 상세값은 장기보존보다 샘플링 또는 집계가 적절합니다.[^5_12][^5_13][^5_16]


## Grafana 템플릿

GPU 대시보드는 다음 6개 패널로 시작하면 가장 실용적입니다.

- Overview: 노드별 GPU 수, utilization, VRAM, temperature, power.
- Per GPU: core, framebuffer memory, clocks, PState, ECC, XID.[^5_32][^5_1]
- Process view: 프로세스별 GPU 점유와 job correlation.
- Cluster view: 노드별 가용량, MIG 상태, 스케줄링 상태.
- Alert view: exporter down, thermal/power alarm, ECC/XID.
- Efficiency view: utilization 대비 VRAM, idle time, underutilization.

NVIDIA의 OpenShift 문서는 DCGM Exporter 대시보드를 Grafana 형식으로 배포하는 절차와 기본 그래프 항목을 제공하며, GPU Temperature, GPU Power Usage, GPU SM Clocks, GPU Utilization, GPU Framebuffer Mem Used, Tensor Core Utilization을 기본 구성으로 제시합니다. Grafana Labs의 공개 대시보드들도 DCGM Exporter 기반 GPU 템플릿의 좋은 출발점입니다.[^5_30][^5_31][^5_1][^5_32]

## Prometheus 고가용성

Prometheus HA를 확장할 때는 보통 **Thanos** 또는 **Cortex**를 고려합니다. 둘 다 Prometheus의 스케일 한계를 보완하기 위한 아키텍처지만, 접근 방식이 다릅니다.[^5_11]

- **Thanos**: Prometheus 옆에 sidecar를 두고, 오브젝트 스토리지를 이용해 장기보관과 글로벌 쿼리를 구성하는 방식이 자연스럽습니다.[^5_11]
- **Cortex**: 원격 쓰기와 멀티테넌시, 대규모 분산 저장에 더 초점을 둔 구조로 이해하면 됩니다.[^5_11]

실무적으로는 소규모/중규모는 Thanos가 단순하고, 멀티테넌시와 대규모 분산 저장이 강하게 필요한 조직은 Cortex 계열을 검토하는 경우가 많습니다.[^5_11]

원하시면 다음 단계로 **“점수표를 실제 숫자로 채운 최종 선정표”** 또는 **“Thanos vs Cortex 배포 토폴로지 다이어그램”**까지 이어서 정리할 수 있습니다.
<span style="display:none">[^5_33][^5_34][^5_35][^5_36][^5_37][^5_38][^5_39][^5_40][^5_41][^5_42]</span>

<div align="center">⁂</div>

[^5_1]: https://docs.nvidia.com/datacenter/cloud-native/openshift/latest/enable-gpu-monitoring-dashboard.html

[^5_2]: https://prometheus.io/docs/introduction/overview/

[^5_3]: https://www.zabbix.com/network_monitoring

[^5_4]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^5_5]: https://www.dynatrace.com/pricing/rate-card/

[^5_6]: https://prometheus.io/docs/instrumenting/exporters/

[^5_7]: https://blog.zabbix.com/handy-tips-38-automating-snmp-item-creation-with-low-level-discovery/23521/

[^5_8]: https://www.datadoghq.com/product/infrastructure-monitoring/

[^5_9]: https://docs.dynatrace.com/docs/observe/infrastructure-monitoring

[^5_10]: https://www.dynatrace.com/platform/infrastructure-observability/

[^5_11]: https://grafana.com/blog/promcon-recap-two-households-both-alike-in-dignity-cortex-and-thanos/

[^5_12]: https://grafana.com/pricing/

[^5_13]: https://newrelic.com/pricing

[^5_14]: https://www.getpricepulse.com/companies/datadog-pricing.html

[^5_15]: https://last9.io/blog/datadog-pricing-all-your-questions-answered/

[^5_16]: https://grafana.com/docs/grafana-cloud/cost-management-and-billing/analyze-costs/logs-costs/

[^5_17]: https://checkmk.com/blog/monitoring-management-boards

[^5_18]: https://nvidia.github.io/dcgm-exporter/

[^5_19]: https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/gpu-observability/setup/

[^5_20]: https://docs.librenms.org/Support/Device-Sensors/

[^5_21]: https://www.librenms.org/

[^5_22]: https://www.ibm.com/products/instana/infrastructure-monitoring

[^5_23]: https://docs.kakaocloud.com/tutorial/observability/nvidia-gpu-monitoring

[^5_24]: https://docs.kakaocloud.com/en/tutorial/observability/nvidia-gpu-monitoring

[^5_25]: https://docs.kakaocloud.com/tutorial/container/k8se-nvidia-gpu-worknode

[^5_26]: https://docs.nvidia.com/deploy/nvidia-smi/index.html

[^5_27]: https://nvidia.custhelp.com/app/answers/detail/a_id/3751/~/useful-nvidia-smi-queries

[^5_28]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html

[^5_29]: https://developer.nvidia.com/management-library-nvml

[^5_30]: https://grafana.com/grafana/dashboards/22515-nvidia-dcgm-dashboard/

[^5_31]: https://grafana.com/grafana/dashboards/25526-nvidia-gpu-for-ai-workloads-efficiency-cost-health-dcgm/

[^5_32]: https://grafana.com/grafana/dashboards/24450-nvidia-dcgm-exporter-dashboard/

[^5_33]: http://dspace.ensta.edu.dz/jspui/bitstream/123456789/320/1/MFE_2024-Abdi-Boubeghel%20-%20KHOUMERI%20El%20Hadi.pdf

[^5_34]: https://middleware.io/blog/infrastructure-monitoring-tools/

[^5_35]: https://truetech.dev/ai-development/services/mlops/gpu-utilization-vram-monitoring-setup.html

[^5_36]: https://blog.csdn.net/sunyuhua_keyboard/article/details/153274945

[^5_37]: https://blog.csdn.net/2503_92849275/article/details/149790607

[^5_38]: https://highitking.com/📊-gpu-모니터링-대시보드-grafana와-dcgm으로-엔비디아-지표-시/

[^5_39]: https://gitnux.org/best/business-monitoring-software/

[^5_40]: https://scalr.com/learning-center/the-complete-guide-to-devops-monitoring-tools-in-2025-choosing-the-right-solution-for-your-infrastructure

[^5_41]: https://qiita.com/daihiraoka/items/7c5a12733aacccdf83ee

[^5_42]: https://developer.nvidia.com/blog/monitoring-gpus-in-kubernetes-with-dcgm/


---

# 엔터프라이즈 모니터링 툴 비교: ROI와 도입 가이드, GPU 수집 우선순위 및 보존 전략 보고서

## 개요

엔터프라이즈 모니터링 툴 선정은 기능 비교만으로 결정하기 어렵고, 운영 인력 절감, MTTR 단축, 도구 통합에 따른 중복 비용 제거, GPU 및 고카디널리티 메트릭의 저장 비용까지 함께 고려해야 한다. 특히 GPU 중심 인프라에서는 VRAM, GPU utilization, power, temperature, ECC, XID, 프로세스별 메모리 점유를 어디까지 수집하고 얼마나 오래 보관할지에 따라 총비용이 크게 달라진다.[^6_1][^6_2][^6_3][^6_4][^6_5][^6_6][^6_7]

이 보고서는 Prometheus, Zabbix, Datadog, Dynatrace를 엔터프라이즈 관점에서 비교하고, ROI 판단 프레임워크와 도입 가이드를 제시한 뒤, GPU 모니터링 수집 항목 우선순위와 보존 전략을 인프라 규모 및 데이터 비용 최적화 관점에서 정리한다.[^6_8][^6_9][^6_10][^6_11]

## ROI 관점의 비교 기준

ROI는 라이선스 가격만이 아니라 다음 항목을 합산해 판단해야 한다.

- 장애 감지 및 복구 속도 개선, 즉 MTTR 단축[^6_2][^6_1]
- 다수의 포인트 솔루션을 통합하면서 줄어드는 중복 비용[^6_12][^6_1]
- 운영 및 개발 인력의 생산성 향상[^6_13][^6_2]
- 클라우드 및 GPU 자원의 낭비 감소[^6_14][^6_15]
- 규제 대응과 장기보존 요구에 따른 저장 비용[^6_16][^6_17][^6_18]

Dynatrace의 Forrester 기반 분석은 3년 기준 274% ROI와 6개월 미만 회수 기간을 제시하며, 운영 효율 향상과 오탐 감소, 혁신 속도 향상을 주요 편익으로 설명한다. Dynatrace의 IDC 기반 자료는 3년 451% ROI를 제시하며, 통합 모니터링에 따른 운영 비용 절감을 강조한다. Datadog 관련 Nucleus 분석은 통합 플랫폼 도입 고객이 MTTR 단축, 운영비 절감, 포인트 솔루션 제거에 따른 TCO 절감을 경험했다고 설명한다. Zabbix는 라이선스 비용과 장치당 과금이 없고 예측 가능한 지원 비용을 강조하며, 낮은 TCO를 전면에 내세운다.[^6_3][^6_1][^6_2][^6_13]

## 제품별 엔터프라이즈 비교

| 제품 | 구조 | 강점 | 약점 | ROI에 유리한 조건 |
| :-- | :-- | :-- | :-- | :-- |
| Prometheus | 오픈소스 TSDB, pull/exporter 중심[^6_8][^6_19] | 쿠버네티스/GPU 친화성, 확장성, 벤더 종속성 완화[^6_4][^6_20] | 운영 자동화와 장기보존, 멀티테넌시를 직접 설계해야 함[^6_21][^6_18] | 플랫폼 엔지니어링 역량이 높고 커스텀 요구가 많은 조직 |
| Zabbix | 통합형 오픈소스 관제[^6_3][^6_9] | 하드웨어, SNMP, 네트워크, 서버 센서에 강함[^6_22][^6_9] | 클라우드 네이티브와 분산 트레이스는 보완 필요 | 온프레미스, 네트워크/서버 중심, 낮은 라이선스 TCO 중시 조직 |
| Datadog | SaaS 통합 관측성[^6_12][^6_23] | 빠른 구축, 인프라+로그+APM+GPU 연계, 운영 단순성[^6_1][^6_24] | 호스트·로그·APM 사용량 증가 시 비용 가속[^6_25][^6_26] | 빠른 가시화와 멀티클라우드 통합이 필요한 조직 |
| Dynatrace | SaaS/엔터프라이즈 통합 관측성[^6_11][^6_27] | 자동 발견, AI 분석, 엔터프라이즈 자동화, 높은 통합 효과[^6_13][^6_2] | 비용 구조와 도입 범위 설계가 비교적 무거움[^6_10][^6_2] | 복잡한 대규모 환경, AIOps와 풀스택 상관분석이 중요한 조직 |

## 제품별 장단점과 도입 포인트

### Prometheus

Prometheus는 exporter 기반 pull 모델과 PromQL, Kubernetes 친화성 때문에 현대적 인프라와 GPU 클러스터에 가장 자연스럽게 녹아든다. 특히 DCGM Exporter와 결합하면 GPU utilization, memory usage, ECC, power, thermals를 표준적으로 수집할 수 있어 AI 플랫폼에 적합하다. 반면 운영팀이 스토리지 크기, retention, remote write, alerting, 고가용성까지 책임져야 하므로 운영 역량이 ROI를 좌우한다.[^6_4][^6_18][^6_19][^6_23][^6_28][^6_8]

### Zabbix

Zabbix는 서버, 네트워크, SNMP 장비, 팬, 센서, 인터페이스, 하드웨어 상태를 하나의 운영 모델로 관리하기 쉬우며, 라이선스 비용이 없다는 점에서 ROI가 매우 명확하다. 특히 국내 기업의 온프레미스 데이터센터, 제조, 금융, 공공 계열처럼 물리 장비와 네트워크 비중이 큰 환경에서 실효성이 높다. 다만 GPU 워크로드와 분산 애플리케이션 추적을 깊게 다루기에는 Prometheus 또는 상용 APM 계층을 함께 고려하는 편이 낫다.[^6_9][^6_22][^6_29][^6_3]

### Datadog

Datadog은 인프라, 로그, 트레이스, 네트워크, GPU 메트릭을 하나의 SaaS 플랫폼으로 통합할 수 있어 도입 초기 ROI가 빠르게 나타나는 경우가 많다. 실제 사례에서는 다수의 분절된 도구로 보지 못하던 네트워크 병목을 Datadog이 빠르게 드러내며 운영 의사결정을 개선했다는 점이 강조된다. 반면 과금은 호스트 수, APM, 로그량, 커스텀 메트릭, 보존기간에 따라 누적되므로, 데이터 수집 정책이 통제되지 않으면 ROI가 약화될 수 있다.[^6_17][^6_23][^6_24][^6_25][^6_26][^6_30][^6_1]

### Dynatrace

Dynatrace는 대규모 엔터프라이즈 환경에서 자동 발견과 AI 기반 원인 분석, 낮은 오탐, 엔드투엔드 상관관계에 강하며, ROI 자료도 이러한 통합 효과에 초점을 둔다. DevOps 효율 향상, 운영 효율 개선, churn 감소, false-positive alert 감소 같은 편익은 대규모 조직에서 특히 의미가 크다. 대신 대규모 통합 도입은 설계와 라이선스 범위 정의가 중요하고, 소규모 환경에는 과도한 선택일 수 있다.[^6_10][^6_2][^6_13]

## 도입 가이드

### 소규모~중규모 엔터프라이즈

- 서버/네트워크 중심: Zabbix 우선 검토[^6_3][^6_9]
- 쿠버네티스/GPU 중심: Prometheus + DCGM Exporter + Grafana[^6_20][^6_4]
- 빠른 통합과 운영 편의성: Datadog[^6_24][^6_1]


### 대규모 엔터프라이즈

- 멀티클라우드, 마이크로서비스, AIOps 요구: Dynatrace 또는 Datadog[^6_11][^6_2]
- 규제와 데이터 주권, 온프레미스 중심: Zabbix + Prometheus 이중 구조[^6_8][^6_3]
- AI 플랫폼/연구센터: Prometheus + DCGM Exporter + 장기보존 아키텍처[^6_21][^6_4]


## GPU 모니터링 수집 항목 우선순위

GPU 메트릭은 모두 동일한 가치를 가지지 않는다. 비용과 운영 가치를 고려하면 계층적으로 수집하는 것이 가장 합리적이다.

### 1순위: 필수 운영 메트릭

- GPU utilization[^6_5][^6_7]
- VRAM total/used/free[^6_7][^6_5]
- Temperature[^6_5][^6_7]
- Power draw / power limit[^6_6][^6_7]
- XID errors[^6_31][^6_32]

이 메트릭들은 현재 자원 포화 여부, 발열, 전력 제한, 즉시 장애를 판단하는 핵심 지표다. GPU를 실제로 사용하고 있는지, VRAM 부족이 있는지, 장애 직전 징후가 있는지를 가장 빠르게 보여주므로 모든 규모에서 기본 수집 대상이다.[^6_32][^6_4][^6_7][^6_5]

### 2순위: 안정성 및 성능 최적화 메트릭

- ECC errors[^6_6][^6_7]
- SM/graphics/memory clocks[^6_33][^6_5]
- PState[^6_7][^6_5]
- PCIe/NVLink throughput[^6_33]
- Process별 GPU 메모리 점유[^6_7]

이 계층은 하드웨어 불안정성, 클럭 저하, 링크 병목, 특정 사용자 또는 잡의 과도한 VRAM 소비를 분석하는 데 유용하다. 대규모 GPU 클러스터나 연구 환경에서는 사실상 필수지만, 소규모 환경에서는 보존 주기를 줄이거나 일부만 저장해도 된다.[^6_6][^6_33]

### 3순위: 고급 분석 메트릭

- MIG 세부 메트릭[^6_34]
- Tensor core/decoder/encoder 계열 세부 활용률[^6_35][^6_33]
- 애플리케이션별 사용자 정의 GPU 메트릭[^6_15][^6_36]

이 계층은 비용과 카디널리티가 빠르게 증가하므로, 운영 표준 대시보드보다 성능 튜닝이나 특정 워크로드 분석에 제한적으로 쓰는 편이 효율적이다.[^6_18][^6_37]

## 보존 전략

보존 전략은 “실시간 운영”, “장애 분석”, “추세/용량 계획”, “규제/감사” 목적을 분리해서 설계하는 것이 가장 경제적이다. Prometheus 계열에서는 retention.time, retention.size, remote storage, downsampling 같은 설계가 비용과 성능에 직접 영향을 준다.[^6_28][^6_37][^6_18]

### 권장 보존 계층

| 데이터 계층 | 예시 메트릭 | 권장 보존 방향 | 이유 |
| :-- | :-- | :-- | :-- |
| 고해상도 실시간 | GPU utilization, VRAM, temp, power, XID[^6_4][^6_32] | 짧게 보존 | 운영 대시보드와 즉시 장애 대응 중심 |
| 장애 분석용 | ECC, clocks, process별 메모리, PCIe[^6_6][^6_7][^6_33] | 중기 보존 | 장애 원인 추적과 재현 분석 |
| 추세 분석용 | 일/주 단위 집계 데이터 | 장기 보존 | 용량 계획, 예산, 자원 효율화 |
| 감사/규제용 | 정책상 필요한 이벤트/로그 | 별도 보존 | 법규 및 내부통제 대응 |

### 규모별 보존 전략

- 소규모: 필수 메트릭 위주, 짧은 retention, 장기 저장 최소화[^6_18][^6_28]
- 중규모: 1순위는 상시, 2순위는 요약본 또는 중기 보존[^6_37][^6_28]
- 대규모: 1순위와 2순위는 계층형 저장, 3순위는 선택 수집 또는 샘플링[^6_37][^6_18]


## 데이터 비용 최적화 전략

- scrape interval을 목적별로 분리한다. 모든 메트릭을 고주기로 수집하지 않는다.[^6_18][^6_37]
- 고카디널리티 라벨을 제한한다. pod UID, request ID, raw job name 같은 무한 증식형 라벨은 피한다.[^6_38][^6_37][^6_18]
- 장기보존은 원시 데이터보다 다운샘플링 또는 집계 데이터를 우선한다.[^6_28][^6_37]
- GPU 상세 메트릭은 모든 노드에 항상 켜 두기보다 GPU 노드군 또는 중요 워크로드에 우선 적용한다.[^6_4][^6_15]
- SaaS 도구 사용 시 로그와 APM, 커스텀 메트릭 과금 항목을 분리해 예산 통제한다.[^6_25][^6_16][^6_17]


## 결론

Prometheus는 GPU 및 클라우드 네이티브 환경에서 가장 유연하고 강력하지만, ROI는 운영팀의 플랫폼 역량에 크게 좌우된다. Zabbix는 라이선스 비용 없는 낮은 TCO와 하드웨어/네트워크 가시성 덕분에 온프레미스 엔터프라이즈에 매우 경쟁력이 높다. Datadog과 Dynatrace는 도구 통합과 운영 단순화, MTTR 단축 측면에서 높은 ROI를 기대할 수 있으나, 데이터 수집량과 기능 확장에 따른 비용 통제가 필수다. GPU 모니터링은 필수 메트릭부터 단계적으로 수집하고, 고해상도 단기 보존과 집계형 장기 보존을 분리하는 전략이 가장 비용 효율적이다[^6_1][^6_2][^6_9][^6_21][^6_25][^6_3][^6_4][^6_8][^6_28][^6_37][^6_18]
<span style="display:none">[^6_39][^6_40][^6_41][^6_42][^6_43][^6_44][^6_45][^6_46][^6_47][^6_48][^6_49]</span>

<div align="center">⁂</div>

[^6_1]: https://nucleusresearch.com/research/single/deploying-a-unified-observability-stack-with-datadog/

[^6_2]: https://www.dynatrace.com/news/blog/total-economic-impact-report/

[^6_3]: https://www.zabbix.com/

[^6_4]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^6_5]: https://nvidia.custhelp.com/app/answers/detail/a_id/3751/~/useful-nvidia-smi-queries

[^6_6]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html

[^6_7]: https://developer.nvidia.com/management-library-nvml

[^6_8]: https://prometheus.io/docs/introduction/overview/

[^6_9]: https://www.zabbix.com/network_monitoring

[^6_10]: https://www.dynatrace.com/pricing/rate-card/

[^6_11]: https://docs.dynatrace.com/docs/observe/infrastructure-monitoring

[^6_12]: https://www.datadoghq.com/monitoring/cloud-observability/

[^6_13]: https://www.dynatrace.com/info/reports/idc-business-value-study/

[^6_14]: https://www.datadoghq.com/blog/manage-ai-cost-and-performance-with-datadog/

[^6_15]: https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/gpu-observability/configuration/

[^6_16]: https://grafana.com/pricing/

[^6_17]: https://newrelic.com/pricing

[^6_18]: https://www.mindfulchase.com/explore/troubleshooting-tips/devops-tools/troubleshooting-scraping,-cardinality,-and-storage-issues-in-prometheus.html

[^6_19]: https://prometheus.io/docs/instrumenting/exporters/

[^6_20]: https://nvidia.github.io/dcgm-exporter/

[^6_21]: https://grafana.com/blog/promcon-recap-two-households-both-alike-in-dignity-cortex-and-thanos/

[^6_22]: https://blog.zabbix.com/handy-tips-38-automating-snmp-item-creation-with-low-level-discovery/23521/

[^6_23]: https://docs.datadoghq.com/integrations/dcgm/

[^6_24]: https://www.jadeglobal.com/resources/case-study/datadog-observability-platform-implementation-saas-leader

[^6_25]: https://www.getpricepulse.com/companies/datadog-pricing.html

[^6_26]: https://last9.io/blog/datadog-pricing-all-your-questions-answered/

[^6_27]: https://www.dynatrace.com/platform/infrastructure-observability/

[^6_28]: https://deployed.cloud/prometheus-retention-and-scaling-guide

[^6_29]: https://www.atatus.com/blog/prometheus-vs-zabbix/

[^6_30]: https://devopsity.com/case-studies/datadog-observability-for-ecommerce-platform/

[^6_31]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html

[^6_32]: https://www.kubenatives.com/p/gpu-monitoring-dcgm-exporter-kubernetes

[^6_33]: https://metricshub.com/docs/latest/connectors/nvidiadcgmexporter

[^6_34]: https://yandex.cloud/en/docs/stackland/concepts/cluster-monitoring/nvidia-dcgm-mig-monitoring

[^6_35]: https://docs.nvidia.com/datacenter/cloud-native/openshift/latest/enable-gpu-monitoring-dashboard.html

[^6_36]: https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/gpu-observability/setup/

[^6_37]: https://medium.com/@platform.engineers/optimizing-prometheus-storage-handling-high-cardinality-metrics-at-scale-31140c92a7e4

[^6_38]: https://www.youtube.com/watch?v=49BGvC1coG4

[^6_39]: https://www.ijmra.us/project doc/2025/IJME_APRIL2025/IJMIE3April25.pdf

[^6_40]: https://www.datadoghq.com/case-studies/roller/

[^6_41]: https://www.ijsr.net/archive/v11i7/SR22722094354.pdf

[^6_42]: https://www.datadoghq.com/ja/case-studies/

[^6_43]: https://www.thoughtworks.com/en-us/insights/blog/generative-ai/from-alert-fatigue-to-AIOps-building-proactive-observability-stack-with-Datadog-on-EKS

[^6_44]: https://dynatrace36.rssing.com/chan-55453562/article58.html

[^6_45]: https://docs.nvidia.com/datacenter/dcgm/2.2/pdf/DCGM_User_Guide.pdf

[^6_46]: https://adhdecode.com/interviews/prometheus/capacity-planning-scaling/

[^6_47]: https://fastfox.pro/blog/tutorials/prometheus-tsdb-cardinality-control/

[^6_48]: https://markaicode.com/howto/nvidia-dcgm-setup-and-configuration-guide/

[^6_49]: https://www.elastic.co/docs/reference/integrations/nvidia_gpu_otel


---

# ROI/TCO model: compare Dynatrace/Datadog vs Prometheus/Zabbix across startup and enterprise scales

GPU metrics priority: build a retention \& cost optimization plan for high-cardinality DCGM data pipelines
모니터링 툴 도입 시 초기 구축 비용 및 운영 인력 산정 가이드
고성능 GPU 클러스터 환경에서의 데이터 파이프라인 병목 현상 분석
장기 보관용 시계열 데이터 압축 알고리즘 및 스토리지 계층화 전략

요청하신 주제들을 모두 반영한 **보고서형 정리본**을 작성해 두었습니다. 핵심은 **스타트업 vs 엔터프라이즈의 ROI/TCO 차이**, **GPU 메트릭 우선순위와 보존 전략**, **초기 구축 비용과 운영 인력 산정**, **GPU 데이터 파이프라인 병목**, **Prometheus 고가용성(Thanos/Cortex)** 입니다.

## 핵심 요약

스타트업에서는 보통 **Prometheus + Grafana** 또는 **Zabbix**가 비용 효율이 높고, 엔터프라이즈에서는 **Datadog**과 **Dynatrace**가 통합 관측성과 MTTR 단축 측면에서 ROI가 높게 나오는 경향이 있습니다. GPU 환경은 메트릭 종류와 시계열 수가 빠르게 늘어나므로, **GPU utilization, VRAM, temperature, power, ECC, XID**를 1순위로 두고, 장기 보관은 집계/다운샘플링 중심으로 설계하는 것이 비용 최적화에 유리합니다.[^7_1][^7_2][^7_3][^7_4][^7_5][^7_6]

## 포함된 분석

보고서에는 다음 항목이 포함되어 있습니다.

- 스타트업/엔터프라이즈별 ROI/TCO 비교[^7_5][^7_6][^7_7]
- 초기 구축 비용과 운영 인력 산정 가이드[^7_8]
- GPU 데이터 파이프라인 병목 유형과 진단 지표[^7_9][^7_10][^7_11]
- GPU 수집 항목 우선순위 및 보존 전략[^7_12][^7_13][^7_14][^7_1]
- Prometheus TSDB 보존/압축 전략과 Thanos/Cortex 비교[^7_15][^7_16][^7_17][^7_18]


## 다음 활용 방식

이 문서는 바로 내부 검토용으로 쓸 수 있도록 **비교표, 우선순위, 보존 정책, 아키텍처 선택 기준** 중심으로 정리되어 있습니다.
원하시면 다음 단계로는 **“부서별 도입 산정표(예: SRE, 플랫폼, AI 연구, 네트워크 운영)”** 또는 **“예산 시뮬레이션 표(호스트 수/GPU 수/보존 기간 기준)”** 형태로 더 구체화할 수 있습니다.
<span style="display:none">[^7_19][^7_20][^7_21][^7_22][^7_23][^7_24][^7_25][^7_26][^7_27][^7_28][^7_29][^7_30][^7_31][^7_32][^7_33][^7_34][^7_35][^7_36][^7_37][^7_38][^7_39][^7_40]</span>

<div align="center">⁂</div>

[^7_1]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^7_2]: https://nvidia.custhelp.com/app/answers/detail/a_id/3751/~/useful-nvidia-smi-queries

[^7_3]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html

[^7_4]: https://developer.nvidia.com/management-library-nvml

[^7_5]: https://www.dynatrace.com/news/blog/total-economic-impact-report/

[^7_6]: https://www.zabbix.com/

[^7_7]: https://nucleusresearch.com/research/single/deploying-a-unified-observability-stack-with-datadog/

[^7_8]: https://www.whatsupgold.com/blog/calculating-the-real-cost-diy-network-monitoring-solution

[^7_9]: https://jrps.shodhsagar.com/index.php/j/article/view/1583

[^7_10]: https://developer.nvidia.com/blog/scaling-data-pipelines-att-optimizes-speed-cost-and-efficiency-with-gpus/

[^7_11]: https://www.youtube.com/watch?v=iJUVVfqPo-s

[^7_12]: https://www.kubenatives.com/p/gpu-monitoring-dcgm-exporter-kubernetes

[^7_13]: https://medium.com/@platform.engineers/optimizing-prometheus-storage-handling-high-cardinality-metrics-at-scale-31140c92a7e4

[^7_14]: https://www.mindfulchase.com/explore/troubleshooting-tips/devops-tools/troubleshooting-scraping,-cardinality,-and-storage-issues-in-prometheus.html

[^7_15]: https://thanos.io/tip/components/compact.md/

[^7_16]: https://prometheus.io/docs/prometheus/latest/storage/

[^7_17]: https://www.youtube.com/watch?v=Pl5hEoRPLJU

[^7_18]: https://github.com/prometheus/prometheus/issues/11112

[^7_19]: https://ijirt.org/publishedpaper/IJIRT191745_PAPER.pdf

[^7_20]: https://arxiv.org/html/2605.19775v1

[^7_21]: https://arxiv.org/html/2604.21275v1

[^7_22]: https://vendorbenchmark.com/blog/observability-platform-pricing-benchmark-comparison

[^7_23]: https://arxiv.org/abs/2510.18300v1

[^7_24]: https://www.usenix.org/system/files/nsdi22-paper-weng.pdf

[^7_25]: https://yobitel.com/knowledge-base/dcgm-exporter

[^7_26]: https://www.jobpreparena.com/blog/the-ml-infrastructure-heat-map-identifying-bottlenecks-in-your-training-cluster

[^7_27]: https://www.dynatrace.com/platform/comparison/dynatrace-vs-datadog/

[^7_28]: https://towardsdatascience.com/a-caching-strategy-for-identifying-bottlenecks-on-the-data-input-pipeline/

[^7_29]: https://openobserve.ai/blog/datadog-competitors/

[^7_30]: https://thanos.io/blog/2023-11-20-life-of-a-sample-part-2/

[^7_31]: https://dev.to/kanywst/thanos-deep-dive-breaking-through-prometheuss-limitations-a5e

[^7_32]: https://www.youngju.dev/blog/prometheus/prometheus_tsdb_internals.en

[^7_33]: https://ganeshvernekar.com/blog/prometheus-tsdb-compaction-and-retention/

[^7_34]: https://devopsaitoolkit.com/blog/prometheus-tsdb-internals-blocks-compaction-retention/

[^7_35]: https://timesofcloud.com/prometheus-grafana/local-storage/

[^7_36]: https://aws.amazon.com/blogs/opensource/improving-ha-and-long-term-storage-for-prometheus-using-thanos-on-eks-with-s3/

[^7_37]: https://cubepath.com/docs/observability-advanced/thanos-long-term-prometheus-storage

[^7_38]: https://prometheus.io/docs/prometheus/latest/command-line/prometheus/

[^7_39]: https://thanos.io/v0.18/thanos/storage.md/

[^7_40]: https://promcon.io/2018-munich/slides/thanos-prometheus-at-scale.pdf


---

# 현재 조사한 소프트웨어 및 하드웨어 모니터링 플랫폼을 일반적인 명칭(가장 대중적인)을 알려주고, 해당 플랫폼의 시장 동향을 상세하게 조사하여 상세하게 정리해 줘.

현재 가장 대중적인 명칭으로는 **Prometheus, Zabbix, Datadog, Dynatrace**가 각각 그대로 통용됩니다. 하드웨어/GPU 쪽에서는 **DCGM Exporter**, **Grafana DCGM Dashboard**, **NVIDIA GPU Observability** 같은 표현이 가장 널리 쓰입니다.[^8_1][^8_2][^8_3][^8_4][^8_5]

## 시장의 큰 흐름

최근 시장은 “개별 모니터링 도구”에서 **통합 관측성(observability) 플랫폼**으로 빠르게 이동하고 있습니다. 엔터프라이즈 모니터링 시장은 2025~2034년 동안 두 자릿수 CAGR로 성장할 것으로 예측되고, 하이브리드 클라우드·컨테이너·AI 기반 분석이 핵심 성장 동력으로 반복 등장합니다. GPU 모니터링 시장도 별도 성장 시장으로 커지고 있으며, AI/HPC 확대에 따라 GPU 벤치마크·GPU 모니터링 수요가 계속 증가하는 추세입니다.[^8_6][^8_7][^8_8][^8_9][^8_10][^8_11]

## 플랫폼별 대중적 명칭

| 플랫폼 | 가장 대중적인 명칭 | 일반적 포지션 |
| :-- | :-- | :-- |
| Prometheus | 프로메테우스 | 오픈소스 메트릭/알림 표준 |
| Zabbix | 자빅스 | 서버·네트워크·하드웨어 관제 플랫폼 |
| Datadog | 데이터독 | SaaS 통합 관측성 플랫폼 |
| Dynatrace | 다이나트레이스 | 엔터프라이즈 AI 관측성 플랫폼 |
| Grafana | 그라파나 | 시각화/대시보드 표준 |
| DCGM Exporter | DCGM Exporter | NVIDIA GPU 텔레메트리 수집기 |

Prometheus는 pull 기반, exporter 생태계, PromQL, Alertmanager 때문에 **클라우드 네이티브 표준**처럼 받아들여지고 있습니다. Zabbix는 SNMP, LLD, IPMI, 자동 발견으로 **전통적 인프라 관제**의 대표격입니다. Datadog은 메트릭·로그·트레이스를 하나로 묶는 **통합 SaaS** 이미지가 강하고, Dynatrace는 AI 기반 자동 분석과 엔터프라이즈 자동화가 핵심 정체성입니다.[^8_12][^8_2][^8_3][^8_13][^8_14][^8_15][^8_16][^8_17][^8_18][^8_19][^8_1]

## 시장 동향 요약

### 1) 통합 관측성으로 수렴

시장은 메트릭, 로그, 트레이스, 보안, 디지털 경험을 따로 보지 않고 한 플랫폼에서 보는 방향으로 재편되고 있습니다. Datadog은 이를 “single pane of glass”로, Dynatrace는 자동화된 AI 관측성으로 포지셔닝합니다.[^8_7][^8_8][^8_9][^8_15][^8_17][^8_18]

### 2) 하이브리드·멀티클라우드 확대

온프레미스와 클라우드가 섞인 환경이 일반화되면서 하이브리드 클라우드 모니터링이 빠르게 성장 중입니다. 이 흐름에서 Prometheus와 Zabbix는 자체 운영형 선택지로, Datadog/Dynatrace는 관리형 선택지로 선명하게 갈립니다.[^8_9][^8_2][^8_3][^8_15][^8_7][^8_1]

### 3) AI/GPU 관측성의 부상

GPU 클러스터, LLM, 컴퓨터비전, HPC 확대로 GPU 텔레메트리 관측이 별도 시장처럼 자리잡고 있습니다. NVIDIA는 DCGM Exporter, GPU Observability, Grafana 대시보드, Kubernetes 통합을 공식 경로로 제공하고 있습니다.[^8_10][^8_11][^8_20][^8_4][^8_21][^8_22][^8_23][^8_24][^8_6]

### 4) 데이터 비용과 카디널리티 관리 중요성 증가

관측성 플랫폼이 커질수록 비용은 호스트 수보다 **로그량, 커스텀 메트릭, 시계열 카디널리티, 보존 정책**에서 더 크게 발생합니다. 그래서 Datadog도 데이터 파이프라인 제어 제품을 내놓았고, Prometheus 생태계는 Thanos/Cortex 같은 장기보관·확장 구조가 중요해졌습니다.[^8_25][^8_26][^8_27][^8_28][^8_29][^8_30][^8_31][^8_32]

## 플랫폼별 시장 포지션

### Prometheus

Prometheus는 사실상 **오픈소스 메트릭 표준**에 가까운 위상을 갖고 있습니다.[^8_1]
강점은 Kubernetes, exporter, Alertmanager, Grafana와의 결합력이고, 약점은 장기보관과 HA를 직접 설계해야 한다는 점입니다.[^8_30][^8_31][^8_12][^8_1]
시장에서는 “기술 표준” 포지션이 강하며, 클라우드 네이티브와 GPU 환경에서 계속 확장 중입니다.[^8_23][^8_24]

### Zabbix

Zabbix는 **서버·네트워크·하드웨어 모니터링의 대표 오픈소스**로 인식됩니다.[^8_2][^8_14]
SNMP, IPMI, LLD, 자동 발견, 템플릿 기반 운영이 강점이고, 전통적 데이터센터와 온프레미스 조직에서 여전히 강합니다.[^8_13][^8_2]
시장 트렌드상으로는 “레거시”라기보다 **비용 효율적 인프라 관제 플랫폼**으로 재평가되는 흐름입니다.[^8_33][^8_7]

### Datadog

Datadog은 **통합 관측성 SaaS**의 대표 브랜드입니다.[^8_3][^8_17][^8_19]
메트릭, 로그, 트레이스, GPU, APM, 보안, 파이프라인 통제를 한 플랫폼에서 다루는 방향으로 진화하고 있으며, 빠른 도입과 운영 단순성 때문에 스타트업과 성장 조직에서 강합니다.[^8_19][^8_3][^8_25]
시장 동향상 Datadog은 “관측성 플랫폼” 그 자체로 인식되는 경우가 많습니다.[^8_34][^8_8]

### Dynatrace

Dynatrace는 **엔터프라이즈 AI 관측성 플랫폼**으로 가장 많이 불립니다.[^8_15][^8_16][^8_18]
자동 발견, AI 기반 원인 분석, 운영 자동화, 풀스택 가시성을 전면에 내세우고 있으며, 대규모 복잡 환경에서 강합니다.[^8_35][^8_36][^8_37]
시장에서는 Datadog보다 더 “대기업형”, 더 “자동화 지향”이라는 이미지가 강합니다.[^8_8][^8_38][^8_7]

### Grafana와 GPU 계열

Grafana는 이제 단순 대시보드가 아니라 **관측성 시각화 표준**에 가깝습니다.[^8_20][^8_4][^8_5]
특히 GPU 영역에서는 NVIDIA DCGM Exporter와 함께 쓰는 것이 사실상 표준 조합이며, GPU utilization, memory usage, power, temperature, tensor core 활용률을 시각화합니다.[^8_4][^8_5][^8_21][^8_22]

## 국내·글로벌 관점의 채택 패턴

글로벌 시장에서는 Datadog과 Dynatrace가 엔터프라이즈 SaaS 중심으로 강하고, Prometheus는 클라우드 네이티브의 사실상 공용어처럼 자리잡고 있습니다. Zabbix는 온프레미스, 제조, 금융, 공공처럼 장비 중심 환경에서 채택이 유지되고 있습니다.[^8_14][^8_34][^8_8][^8_9][^8_2][^8_33]
국내에서도 하이브리드 클라우드, GPU AI 인프라, 규제 산업이 늘면서 Prometheus+Grafana와 Zabbix 조합, 그리고 SaaS형 Datadog/Dynatrace 도입이 병행되는 구조로 보는 것이 맞습니다.[^8_39][^8_22][^8_7]

## 실무적 해석

요약하면 시장은 다음처럼 나뉩니다.

- **Prometheus**: 오픈소스 표준, 클라우드 네이티브, GPU/쿠버네티스 친화[^8_24][^8_1]
- **Zabbix**: 하드웨어/네트워크/센서 중심, 비용 효율, 온프레미스 강세[^8_2][^8_14]
- **Datadog**: 빠른 통합 SaaS, 스타트업/성장 기업 친화, 사용량 기반 비용 관리 필요[^8_17][^8_3][^8_25]
- **Dynatrace**: 엔터프라이즈 AI 자동화, 복잡한 대규모 환경 최적[^8_37][^8_15]
- **Grafana/DCGM**: 시각화와 GPU 관측성의 사실상 표준 조합[^8_5][^8_21][^8_4]

원하시면 다음 단계로 **“플랫폼별 시장 포지셔닝 맵(성장성/비용/운영난이도/국내 적합성)”**을 표로 정리해 드리겠습니다.
<span style="display:none">[^8_40][^8_41][^8_42][^8_43][^8_44][^8_45][^8_46][^8_47][^8_48][^8_49][^8_50][^8_51][^8_52][^8_53][^8_54][^8_55][^8_56][^8_57][^8_58]</span>

<div align="center">⁂</div>

[^8_1]: https://prometheus.io/docs/introduction/overview/

[^8_2]: https://www.zabbix.com/network_monitoring

[^8_3]: https://www.datadoghq.com/monitoring/cloud-observability/

[^8_4]: https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/gpu-observability/setup/

[^8_5]: https://grafana.com/grafana/dashboards/24450-nvidia-dcgm-exporter-dashboard/

[^8_6]: https://marketintelo.com/report/gpu-monitoring-software-market

[^8_7]: https://straitsresearch.com/ko/report/enterprise-monitoring-market

[^8_8]: https://www.marketsandmarkets.com/Market-Reports/enterprise-monitoring-market-178153789.html

[^8_9]: https://www.giikorea.co.kr/report/mama1664030-enterprise-monitoring-market-by-platform.html

[^8_10]: https://www.verifiedmarketreports.com/ko/product/gpu-benchmark-tools-market/

[^8_11]: https://www.wiseguyreports.com/ko/reports/gpu-benchmark-software-market

[^8_12]: https://prometheus.io/docs/alerting/latest/

[^8_13]: https://blog.zabbix.com/handy-tips-38-automating-snmp-item-creation-with-low-level-discovery/23521/

[^8_14]: https://en.wikipedia.org/wiki/Zabbix

[^8_15]: https://www.dynatrace.com/

[^8_16]: https://www.dynatrace.com/hub/detail/ai-and-llm-observability/

[^8_17]: https://www.datadoghq.com/monitoring/unified-monitoring/

[^8_18]: https://video.dynatrace.com/watch/mRh9c2GXjiNXvyGBLrBFZ7

[^8_19]: https://www.datadoghq.com/blog/announcing-logs/

[^8_20]: https://grafana.com/grafana/dashboards/22515-nvidia-dcgm-dashboard/

[^8_21]: https://docs.nvidia.com/vss/3.1.0/observability.html

[^8_22]: https://docs.nvidia.com/datacenter/cloud-native/openshift/24.9.1/enable-gpu-monitoring-dashboard.html

[^8_23]: https://developer.nvidia.com/blog/monitoring-gpus-in-kubernetes-with-dcgm/

[^8_24]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^8_25]: https://investors.datadoghq.com/news-releases/news-release-details/datadog-launches-observability-pipelines-help-organizations/

[^8_26]: https://grafana.com/pricing/

[^8_27]: https://grafana.com/docs/grafana-cloud/cost-management-and-billing/analyze-costs/logs-costs/

[^8_28]: https://newrelic.com/pricing

[^8_29]: https://www.mindfulchase.com/explore/troubleshooting-tips/devops-tools/troubleshooting-scraping,-cardinality,-and-storage-issues-in-prometheus.html

[^8_30]: https://thanos.io/tip/components/compact.md/

[^8_31]: https://prometheus.io/docs/prometheus/latest/storage/

[^8_32]: https://www.youtube.com/watch?v=Pl5hEoRPLJU

[^8_33]: https://www.zabbix.com/

[^8_34]: https://www.futuremarketinsights.com/reports/application-metrics-and-monitoring-tools-market

[^8_35]: https://docs.dynatrace.com/docs/observe/infrastructure-monitoring

[^8_36]: https://www.dynatrace.com/platform/infrastructure-observability/

[^8_37]: https://www.dynatrace.com/news/blog/total-economic-impact-report/

[^8_38]: https://openobserve.ai/blog/datadog-competitors/

[^8_39]: https://brunch.co.kr/@chaesang/148

[^8_40]: https://www.researchandmarkets.com/reports/6229166/enterprise-monitoring-market-outlook-market

[^8_41]: https://www.globenewswire.com/news-release/2026/05/21/3299073/0/en/enterprise-monitoring-industry-report-2026-global-revenue-expected-to-grow-from-30-billion-in-2025-to-92-billion-by-2032.html

[^8_42]: https://straitsresearch.com/jp/report/enterprise-monitoring-market

[^8_43]: https://www.fortunebusinessinsights.com/ko/enterprise-monitoring-market-112138

[^8_44]: https://www.giikorea.co.kr/report/ires1974263-big-data-monitoring-warning-platform-market-by.html

[^8_45]: https://www.coherentmarketinsights.com/ko/엔터프라이즈성능모니터링시장-4557

[^8_46]: https://www.gminsights.com/ko/industry-analysis/enterprise-monitoring-market

[^8_47]: https://www.youngju.dev/blog/observability/2026-03-09-prometheus-complete-guide.en

[^8_48]: https://www.zabbix.com/features

[^8_49]: https://www.scribd.com/document/923386599/TechDoc-Prometheus

[^8_50]: https://www.youtube.com/watch?v=H5iV6cyq3Rk

[^8_51]: https://techexpert.tips/de/zabbix-de/zabbix-automatische-erkennung-mit-snmp/

[^8_52]: https://techexpert.tips/nl/zabbix-nl/zabbix-auto-discovery-met-behulp-van-snmp/

[^8_53]: https://www.zabbix.com/documentation/current/en/manual/discovery/network_discovery

[^8_54]: https://www.zabbix.com/integrations/snmp

[^8_55]: https://www.youtube.com/watch?v=QENVJ2IXFT8

[^8_56]: https://yandex.cloud/en/docs/stackland/concepts/cluster-monitoring/nvidia-dcgm-monitoring

[^8_57]: https://grafana.com/grafana/dashboards/15117-nvidia-dcgm-exporter/

[^8_58]: https://docs.dynatrace.com/docs/observe/dynatrace-for-ai-observability/ai-observability-app


---

# 주요 IT 모니터링 툴 기능 및 시장 동향 보고서: 2026~2034년 통합 관측성 전환과 GPU 인프라 관리

## 개요

모니터링 시장은 더 이상 개별 인프라 감시 도구의 경쟁이 아니라, 메트릭·로그·트레이스·보안·디지털 경험·AI 운영을 묶는 통합 관측성 플랫폼 경쟁으로 이동하고 있다. 이 전환의 배경에는 하이브리드 클라우드 확산, 마이크로서비스 복잡성 증가, AI 기반 운영 자동화 수요, 그리고 GPU 인프라의 급격한 중요성 확대가 있다.[^9_1][^9_2][^9_3][^9_4][^9_5][^9_6]

본 보고서는 Datadog, Dynatrace, Prometheus, Zabbix를 중심으로 주요 모니터링 툴의 핵심 기능을 비교하고, 2026~2034년 시장 변화와 GPU 인프라 관리의 핵심 지표를 정리하며, 통합 관측성 플랫폼 도입을 위한 체크리스트와 단계별 로드맵을 제시한다.[^9_6][^9_7][^9_8][^9_9]

## 시장 규모와 변화 방향

Research and Markets는 엔터프라이즈 모니터링 시장이 2025년 363억 달러에서 2034년 1,610억 달러로 성장하며 연평균 18% 성장한다고 전망한다. Straits Research는 2025년 347억 달러에서 2034년 1,259억 달러로 연평균 15.3% 성장한다고 제시한다. Future Market Insights는 애플리케이션 메트릭 및 모니터링 툴 시장이 2026년 143억 달러에서 2036년 418억 달러로 성장하며 Datadog, New Relic, Dynatrace, Splunk를 주요 기업으로 언급한다.[^9_4][^9_5][^9_1]

수치 자체는 조사기관마다 다르지만, 방향성은 일치한다. 첫째, 시장의 중심이 인프라 단일 감시에서 통합 관측성으로 이동하고 있고, 둘째, AI/ML 기반 이상 탐지와 예측 기능이 핵심 차별점으로 부상하고 있으며, 셋째, GPU 인프라를 별도 운영 축으로 보는 수요가 빠르게 증가하고 있다.[^9_2][^9_3][^9_10][^9_11][^9_12][^9_6]

## 주요 도구 비교

### 제품별 핵심 기능

| 제품 | 일반적 포지션 | 핵심 기능 | 강점 | 한계 |
| :-- | :-- | :-- | :-- | :-- |
| Prometheus | 오픈소스 메트릭/알림 표준[^9_7] | pull 수집, exporter, PromQL, Alertmanager[^9_7][^9_13] | Kubernetes 친화성, 개방성, GPU/클라우드 네이티브 적합성[^9_14][^9_15] | 장기보존, 멀티테넌시, HA는 별도 설계 필요[^9_16][^9_17] |
| Zabbix | 통합 인프라/네트워크 관제[^9_18][^9_8] | SNMP, LLD, auto-discovery, 서버/센서/네트워크 감시[^9_19][^9_8] | 하드웨어, 온프레미스, 네트워크 장비에 강함[^9_20][^9_8] | 클라우드 네이티브와 분산 추적은 상대적으로 약함 |
| Datadog | SaaS 통합 관측성 플랫폼[^9_9][^9_21] | 인프라, 로그, 트레이스, APM, GPU, 파이프라인 관리[^9_9][^9_22][^9_23] | 빠른 구축, 단일 플랫폼, 운영 단순성[^9_24][^9_9] | 기능 확장과 데이터량 증가 시 비용 상승[^9_25][^9_26] |
| Dynatrace | 엔터프라이즈 AI 관측성[^9_6][^9_27] | 자동 발견, AI 원인 분석, 풀스택 상관분석, AI observability[^9_28][^9_29][^9_30] | 대규모 복잡 환경, 자동화, 운영 효율[^9_31][^9_6] | 비용 구조와 도입 범위 설계가 무거울 수 있음[^9_32][^9_31] |

### 시장 점유율 해석

Prometheus와 Zabbix는 전통적인 “매출 기준 점유율”보다 설치 기반과 오픈소스 채택량으로 영향력을 봐야 한다. Datadog과 Dynatrace는 상용 시장에서 강한 브랜드를 형성하고 있으며, FMI는 Datadog, New Relic, Dynatrace, Splunk를 주요 플레이어로 제시한다. 일부 비공식 분석은 Datadog의 높은 상업적 점유율을 주장하지만 자료 출처와 집계 방식이 제각각이므로, 실무적으로는 “상용 observability лид더군”과 “오픈소스 표준군”을 구분해 해석하는 편이 더 정확하다.[^9_5][^9_7][^9_18][^9_33][^9_34][^9_35]

## 통합 관측성으로의 전환

통합 관측성은 메트릭, 로그, 트레이스, 이벤트, 사용자 경험, 보안 데이터를 분리하지 않고 상호 연계된 맥락으로 분석하는 운영 모델이다. 시장이 이 방향으로 이동하는 이유는 단순하다. 현대 시스템은 마이크로서비스, 쿠버네티스, 서버리스, AI 워크로드가 결합되어 있어 단일 계층 모니터링으로는 원인 분석이 불가능하기 때문이다.[^9_3][^9_21][^9_2][^9_6]

이 전환에서 Prometheus는 메트릭 표준 계층으로 남고, Grafana는 시각화 표준으로 자리잡으며, Datadog과 Dynatrace는 통합 플랫폼 계층을 장악하려는 전략을 보인다. Zabbix는 전통 인프라 감시의 핵심축을 유지하면서도 비용 효율적 대안으로 계속 의미를 가진다.[^9_7][^9_8][^9_9][^9_18][^9_36][^9_37][^9_6]

## GPU 인프라 관리의 핵심 지표

GPU 인프라 관리는 2026년 이후 통합 관측성 시장에서 별도 세그먼트처럼 다뤄질 가능성이 높다. GPU 모니터링 소프트웨어 시장은 2025년 21억 달러에서 2034년 68억 달러로 성장하며 연평균 14.8% 성장할 것이라는 전망도 제시된다. GPU 벤치마크/툴 시장 역시 별도로 성장 예측이 존재한다.[^9_10][^9_11][^9_12]

### 기본 지표

- GPU utilization[^9_14][^9_38]
- VRAM total/used/free[^9_39][^9_14]
- Temperature[^9_38][^9_14]
- Power draw / power limit[^9_40][^9_39]
- XID errors[^9_41]
- ECC errors[^9_40][^9_41]


### 고급 지표

- SM active / SM occupancy[^9_41]
- Tensor pipe active[^9_41]
- DRAM active 또는 memory bandwidth utilization[^9_38][^9_41]
- Throttle reasons[^9_41]
- MIG instance granularity[^9_40][^9_41]

NVIDIA는 DCGM profiling metrics가 낮은 성능 오버헤드로 연속 수집 가능하다고 설명하며, MIG 단위 메트릭도 지원한다고 밝힌다. NVIDIA의 enterprise observability guide는 BCM과 DCGM Exporter를 결합한 GPU Dashboard가 실시간 GPU 사용률, thermal health, memory usage, 병목 식별에 유용하다고 설명한다. Grafana와 OpenShift 문서도 GPU utilization, power, temperature, framebuffer memory, tensor core utilization 등을 주요 시각화 항목으로 제시한다.[^9_36][^9_42][^9_39][^9_40]

## 통합 관측성 도입 체크리스트

도입 성공 여부는 제품 선정 자체보다 도입 전 설계 품질에 좌우된다. 다음 체크리스트가 우선적으로 필요하다.

### 전략 체크리스트

- 현재 감시 대상이 인프라 중심인지, 애플리케이션 중심인지, 둘 다인지 정의했는가.
- 온프레미스, 하이브리드, 멀티클라우드, 쿠버네티스, GPU 클러스터 중 핵심 환경을 분류했는가.
- SLA/SLO, MTTR, 장애 감지율, 인시던트당 분석시간 같은 KPI를 정했는가.
- 로그·메트릭·트레이스·GPU 메트릭의 보존기간과 규제 요건을 정했는가.
- 운영팀의 플랫폼 역량과 SaaS 선호 여부를 확인했는가.


### 기술 체크리스트

- 에이전트/익스포터 표준을 정했는가, 예: OpenTelemetry, node exporter, dcgm-exporter.[^9_15][^9_14][^9_36]
- 고카디널리티 라벨 정책을 마련했는가.[^9_43][^9_44]
- 장기보존 구조를 결정했는가, 예: Prometheus + Thanos/객체저장소.[^9_16][^9_17]
- GPU 노드와 일반 노드의 수집 정책을 분리했는가.[^9_39][^9_41]
- 알람 정책이 단순 임계치가 아니라 장애 원인별로 정의되어 있는가.[^9_41]


### 운영 체크리스트

- 대시보드 표준과 서비스 맵 표준이 정의되었는가.
- 모니터링 비용 예산과 데이터 수집량 예산이 있는가.[^9_25][^9_45][^9_46]
- 도입 후 소유 조직, 운영 RACI, 온콜 체계가 정의되었는가.
- 장애 후 회고와 모니터링 룰 개선 프로세스가 있는가.


## 도입 로드맵

### 1단계: 현재 상태 진단

기존 도구, 데이터 소스, 경보 체계, 저장비용, 운영 병목을 진단한다. 이 단계에서는 어떤 팀이 어떤 데이터를 얼마나 쓰는지 파악하는 것이 가장 중요하다.

### 2단계: 기준 아키텍처 선정

클라우드 네이티브 중심이면 Prometheus + Grafana + OpenTelemetry를 기준으로 삼고, 엔터프라이즈 통합과 빠른 내재화가 중요하면 Datadog 또는 Dynatrace를 기준 플랫폼으로 검토한다. 네트워크/온프레미스 하드웨어 중심이라면 Zabbix를 병행하거나 기본축으로 둘 수 있다.[^9_8][^9_9][^9_18][^9_6][^9_7][^9_36]

### 3단계: 데이터 계층 정비

메트릭, 로그, 트레이스, GPU 메트릭의 라벨/태그 규칙을 통일하고, retention 정책과 저장 계층을 정의한다. GPU 메트릭은 기본 운영 지표와 profiling 지표를 분리해 수집하는 것이 비용 최적화에 유리하다.[^9_39][^9_41]

### 4단계: 핵심 서비스 우선 도입

전사 일괄 도입보다 핵심 서비스 1~2개, GPU 노드군 1개, 네트워크 장비군 1개를 먼저 선택해 파일럿을 수행한다. 이 파일럿에서 KPI 개선과 운영 부담 변화를 검증한다.

### 5단계: 운영 자동화와 확장

Alert noise reduction, runbook, incident workflow, cost governance, 장기보존, capacity planning, GPU efficiency dashboard를 단계적으로 확장한다. 이 시점부터는 단순 모니터링이 아니라 운영 자동화와 비용 통제가 핵심 가치가 된다.[^9_23][^9_41]

## 실무 권고안

- GPU와 쿠버네티스가 핵심이면 Prometheus + DCGM Exporter + Grafana를 표준 측정 계층으로 두는 것이 가장 자연스럽다.[^9_14][^9_36][^9_39]
- 전통적 서버·네트워크 관제가 핵심이면 Zabbix가 비용 효율적이며, 필요 시 Grafana 또는 APM 계층을 추가하는 방식이 적절하다.[^9_18][^9_8]
- 빠른 도입, 통합 가시성, 운영 효율이 중요하면 Datadog이 유리하고, 대규모 복잡 환경과 AI 기반 자동 분석까지 필요하면 Dynatrace가 유리하다.[^9_9][^9_24][^9_31][^9_6]
- 시장은 2034년까지 통합 관측성 중심으로 재편될 가능성이 높으며, GPU observability는 별도 운영 축으로 정착할 가능성이 높다[^9_1][^9_4][^9_10]
<span style="display:none">[^9_47][^9_48][^9_49][^9_50][^9_51][^9_52][^9_53][^9_54]</span>

<div align="center">⁂</div>

[^9_1]: https://straitsresearch.com/ko/report/enterprise-monitoring-market

[^9_2]: https://www.marketsandmarkets.com/Market-Reports/enterprise-monitoring-market-178153789.html

[^9_3]: https://www.giikorea.co.kr/report/mama1664030-enterprise-monitoring-market-by-platform.html

[^9_4]: https://www.researchandmarkets.com/reports/6229166/enterprise-monitoring-market-outlook-market

[^9_5]: https://www.futuremarketinsights.com/reports/application-metrics-and-monitoring-tools-market

[^9_6]: https://www.dynatrace.com/

[^9_7]: https://prometheus.io/docs/introduction/overview/

[^9_8]: https://www.zabbix.com/network_monitoring

[^9_9]: https://www.datadoghq.com/monitoring/cloud-observability/

[^9_10]: https://marketintelo.com/report/gpu-monitoring-software-market

[^9_11]: https://www.verifiedmarketreports.com/ko/product/gpu-benchmark-tools-market/

[^9_12]: https://www.wiseguyreports.com/ko/reports/gpu-benchmark-software-market

[^9_13]: https://prometheus.io/docs/alerting/latest/

[^9_14]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^9_15]: https://nvidia.github.io/dcgm-exporter/

[^9_16]: https://thanos.io/tip/components/compact.md/

[^9_17]: https://prometheus.io/docs/prometheus/latest/storage/

[^9_18]: https://www.zabbix.com/

[^9_19]: https://blog.zabbix.com/handy-tips-38-automating-snmp-item-creation-with-low-level-discovery/23521/

[^9_20]: https://www.zabbix.com/features

[^9_21]: https://www.datadoghq.com/monitoring/unified-monitoring/

[^9_22]: https://docs.datadoghq.com/integrations/dcgm/

[^9_23]: https://investors.datadoghq.com/news-releases/news-release-details/datadog-launches-observability-pipelines-help-organizations/

[^9_24]: https://nucleusresearch.com/research/single/deploying-a-unified-observability-stack-with-datadog/

[^9_25]: https://www.getpricepulse.com/companies/datadog-pricing.html

[^9_26]: https://last9.io/blog/datadog-pricing-all-your-questions-answered/

[^9_27]: https://www.dynatrace.com/hub/detail/ai-and-llm-observability/

[^9_28]: https://docs.dynatrace.com/docs/observe/infrastructure-monitoring

[^9_29]: https://www.dynatrace.com/platform/infrastructure-observability/

[^9_30]: https://docs.dynatrace.com/docs/observe/dynatrace-for-ai-observability/ai-observability-app

[^9_31]: https://www.dynatrace.com/news/blog/total-economic-impact-report/

[^9_32]: https://www.dynatrace.com/pricing/rate-card/

[^9_33]: https://uptrace.dev/tools/top-observability-tools

[^9_34]: https://ardura.consulting/blog/apm-tools-comparison-2026/

[^9_35]: https://www.manageengine.com/it-operations-management/application-observability/apm-tools-comparison.html

[^9_36]: https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/gpu-observability/setup/

[^9_37]: https://grafana.com/grafana/dashboards/22515-nvidia-dcgm-dashboard/

[^9_38]: https://learn.microsoft.com/en-us/azure/aks/monitor-gpu-metrics

[^9_39]: https://docs.nvidia.com/enterprise-reference-architectures/observability-guide/latest/custom-dashboards.html

[^9_40]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html

[^9_41]: https://devopsbeast.com/blog/dcgm-prometheus-gpu-observability

[^9_42]: https://docs.nvidia.com/datacenter/cloud-native/openshift/24.9.1/enable-gpu-monitoring-dashboard.html

[^9_43]: https://medium.com/@platform.engineers/optimizing-prometheus-storage-handling-high-cardinality-metrics-at-scale-31140c92a7e4

[^9_44]: https://www.mindfulchase.com/explore/troubleshooting-tips/devops-tools/troubleshooting-scraping,-cardinality,-and-storage-issues-in-prometheus.html

[^9_45]: https://grafana.com/pricing/

[^9_46]: https://newrelic.com/pricing

[^9_47]: https://openobserve.ai/blog/top-10-observability-platforms/

[^9_48]: https://novaaiops.com/blog/datadog-vs-dynatrace-vs-new-relic-2026

[^9_49]: https://cloud.google.com/stackdriver/docs/solutions/agents/ops-agent/third-party-nvidia?hl=id

[^9_50]: https://technologychecker.io/technology/new-relic

[^9_51]: https://www.peerspot.com/categories/application-performance-monitoring-apm-and-observability

[^9_52]: https://quadrantx.io/202601040925-application-performance-monitoring_Q1_2026

[^9_53]: https://www.qytera.de/blog/application-performance-monitoring-tools

[^9_54]: https://www.sphericalinsights.com/blogs/top-20-companies-in-global-application-performance-monitoring-apm-suites-market-2026-2035-spherical-insights-analysis


---

# GPU 인프라 대규모 환경에서의 메트릭 보존 정책 최적화 사례

Observability 성숙도 평가 모델 및 단계별 측정 지표

대규모 GPU 인프라에서는 **모든 메트릭을 똑같이 오래 보관하는 방식이 비효율적**이며, 운영 핵심 지표와 진단 지표, 장기 추세 지표를 계층적으로 나누는 방식이 가장 적절합니다. 관측성 성숙도는 수집-가시화-경보-자동화-예측의 단계로 보고, 각 단계마다 다른 KPI로 평가하는 것이 좋습니다.

## GPU 메트릭 보존 정책

핵심 원칙은 다음과 같습니다.

- **Hot raw**: GPU utilization, VRAM, temperature, power, XID 같은 운영 핵심 지표는 7~30일 정도의 짧은 고해상도 보존.
- **Warm diagnostic**: ECC, clocks, process별 점유, SM active, tensor pipe, DRAM bandwidth 같은 분석용 지표는 30~90일 보존.
- **Cold aggregated**: 일/주 단위 집계와 효율 지표는 3~12개월 보존.
- **Archive**: 감사·규제·인시던트 요약은 장기 보존.

이렇게 하면 저장비용을 줄이면서도 장애 대응과 성능 분석에 필요한 정보는 유지할 수 있습니다. 특히 GPU 클러스터는 노드, 파드, 잡, MIG 인스턴스, 사용자 라벨이 겹치면서 시계열 수가 급증하므로, 고카디널리티 라벨을 줄이는 것이 매우 중요합니다.

## 성숙도 평가 모델

관측성 성숙도는 보통 다음 다섯 단계로 봅니다.

1. **수집**: 기본 메트릭/로그만 모으는 단계.
2. **가시화**: 통합 대시보드로 상태를 보는 단계.
3. **경보**: 다중 조건 알람과 에스컬레이션이 있는 단계.
4. **자동화**: 자가복구, 이벤트 기반 대응이 가능한 단계.
5. **예측**: 이상 탐지와 용량 예측으로 선제 대응하는 단계.

### 단계별 측정 지표

- 공통: MTTA, MTTR, MTTD, 알람 정밀도, false positive rate, 대시보드 사용률, 데이터 유실률.
- GPU 특화: GPU utilization 대비 처리량, VRAM 사용률과 OOM 발생률, ECC/XID 빈도, thermal throttling 비율, idle time.
- 인프라 특화: CPU/IO wait, disk latency, network retransmits, retention hit rate, cardinality growth.


## 실무 적용 순서

대규모 GPU 조직이라면 아래 순서가 현실적입니다.

1. GPU 핵심 메트릭 수집과 유실 방지.
2. VRAM/ECC/XID/thermal 알람 체계 정착.
3. 장기보관 계층과 원시 계층 분리.
4. MTTR, MTTA, 알람 정밀도 측정 체계 구축.
5. 예측 분석과 자동복구 도입.

## 결론

핵심은 **운영 가치가 높은 데이터는 짧고 정확하게**, **장기 분석 데이터는 집계 후 저비용 계층으로** 분리하는 것입니다. 관측성 성숙도는 단순 도구 도입이 아니라 조직의 운영 능력 진화로 봐야 하며, 단계별 KPI를 함께 관리해야 합니다.

원하시면 다음 답변에서 **GPU 보존 정책 템플릿 표**와 **성숙도 평가 체크리스트 1페이지 버전**으로 더 압축해 드리겠습니다.
<span style="display:none">[^10_1][^10_10][^10_11][^10_12][^10_13][^10_14][^10_15][^10_2][^10_3][^10_4][^10_5][^10_6][^10_7][^10_8][^10_9]</span>

<div align="center">⁂</div>

[^10_1]: https://publish.obsidian.md/nobrain711/wiki/Synthesis/aws-observability-maturity-model

[^10_2]: https://docs.aws.amazon.com/ko_kr/prescriptive-guidance/latest/strategy-accelerate-observability-outcomes/strategy-accelerate-observability-outcomes.pdf

[^10_3]: https://aws-observability.github.io/observability-best-practices/ko/guides/observability-maturity-model/

[^10_4]: https://www.oreilly.com/library/view/ren-gong-zhi-neng-xi-tong-xing-neng-gong-cheng-chinese-edition/0642572281557/ch05.html

[^10_5]: https://introl.com/ko/blog/gpu-deployment-best-practices-managing-10000-gpus

[^10_6]: https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-accelerate-observability-outcomes/inspect-adapt-iterate.html

[^10_7]: https://516677.fs1.hubspotusercontent-na1.net/hubfs/516677/stackstate-observability-maturity-model.pdf

[^10_8]: https://signoz.io/guides/observability-maturity-model/

[^10_9]: https://aws-observability.github.io/observability-best-practices/guides/observability-maturity-model/

[^10_10]: https://wpdbr-info.com/22

[^10_11]: https://news.hada.io/topic?id=29904

[^10_12]: https://aws-observability.github.io/observability-best-practices/zh-Hans/guides/observability-maturity-model/

[^10_13]: https://ten1010.io/blog/ai-pub-gpu-monitoring-ai-infrastructure

[^10_14]: https://docs.newrelic.com/kr/docs/new-relic-solutions/observability-maturity/introduction/

[^10_15]: https://v.daum.net/v/20260720102024305


---

# Observability 관점에서 시장 점유율이 가장 높은 top3 플랫폼에 대한 대표화면들 즉, 메트릭 및 모니터링(제어 포함)에 대한 관리자/운영자 화면을 조사해서 정리해 주세요.

아래는 **Observability 관점에서 대표적인 상위 3개 플랫폼의 관리자/운영자 화면**을 중심으로, 시장에서 널리 쓰이는 화면 구조와 기능을 정리한 내용입니다. 실무적으로는 **Datadog, Dynatrace, Prometheus(+Grafana)**가 가장 대표적인 조합으로 보는 것이 적절합니다.[^11_1][^11_2][^11_3][^11_4]

## 대표 플랫폼

- **Datadog**: 통합 관측성 SaaS의 대표 플랫폼으로, 인프라 맵, 동기화 대시보드, Watchdog 같은 자동 탐지 화면이 핵심입니다.[^11_1]
- **Dynatrace**: AI 기반 엔터프라이즈 관측성 플랫폼으로, 인프라/애플리케이션/로그/디지털 경험/보안까지 한 화면에서 다룹니다.[^11_2][^11_5]
- **Prometheus + Grafana**: Prometheus는 수집과 경보, Grafana는 시각화와 운영 대시보드를 담당하며, 실무에서는 이 조합이 대표적인 오픈소스 운영 화면입니다.[^11_6][^11_3][^11_7]


## Datadog 화면

Datadog의 대표 운영 화면은 **Host and Container Maps**, **Synchronized Dashboards**, **Watchdog**입니다. Host and Container Maps는 서버와 컨테이너 상태를 한눈에 보여주는 관리자용 개요 화면이고, Synchronized Dashboards는 공통 태깅 구조를 기반으로 여러 지표를 동시에 추적하는 운영 화면입니다.[^11_1]

Datadog의 강점은 “단일 화면에서 인프라·로그·메트릭을 연결”하는 구조에 있습니다. 따라서 관리자 관점에서는 **자산 현황 → 이상 탐지 → 로그/트레이스 드릴다운** 흐름이 매우 자연스럽게 이어집니다. GPU 관점에서도 DCGM Exporter 연동이 가능하여 GPU 메트릭을 Datadog 안에서 함께 볼 수 있습니다.[^11_8][^11_9][^11_1]

## Dynatrace 화면

Dynatrace의 대표 운영 화면은 **Infrastructure Observability**, **Application Observability**, **AI Observability**, **Digital Experience**, **Log Analytics**입니다. 메인 콘솔은 AI 기반으로 문제를 먼저 탐지하고, 서비스/호스트/트레이스/로그를 상관관계로 묶어 보여주는 것이 특징입니다.[^11_2][^11_5]

운영자 화면 관점에서 Dynatrace는 “문제 목록 → root cause → 영향 범위 → 자동 조치” 흐름이 강합니다. 특히 엔터프라이즈 환경에서 애플리케이션, 인프라, 보안, 비즈니스 이벤트를 함께 보여주는 점이 Datadog보다 더 강하게 설계되어 있습니다. GPU/AI 워크로드까지 포함하면 AI Observability와 인프라 관측성이 하나의 콘솔에서 연결됩니다.[^11_5][^11_10][^11_2]

## Prometheus/Grafana 화면

Prometheus 자체는 주로 **수집 상태, 룰/알림, 쿼리 결과**를 보는 화면이 중심이고, 실제 관리자 화면은 대개 Grafana에서 구성됩니다. 운영 화면은 보통 **메트릭 대시보드, alert overview, drill-down 패널**로 나뉘며, 노드/서비스/GPU별 상태를 시계열 그래프로 확인하는 형태가 일반적입니다.[^11_6][^11_11][^11_12][^11_3][^11_7]

Grafana는 대시보드 템플릿 재사용이 강점이며, GPU 영역에서는 NVIDIA DCGM Dashboard나 커뮤니티 템플릿을 기반으로 **GPU utilization, VRAM, temperature, power, ECC, process별 점유**를 시각화합니다. 카카오클라우드와 NVIDIA 문서도 Kubernetes/GPU 환경에서 Grafana 기반 대시보드 구성을 안내합니다.[^11_13][^11_4][^11_14][^11_15][^11_16][^11_17]

## 운영자 화면 비교

| 플랫폼 | 대표 화면 | 운영자 관점 강점 | 적합한 환경 |
| :-- | :-- | :-- | :-- |
| Datadog | Host/Container Maps, Synchronized Dashboards, Watchdog [^11_1] | 단일 SaaS에서 인프라/로그/메트릭 통합 | 빠른 도입, 멀티클라우드, DevOps |
| Dynatrace | Infrastructure/App Observability, AI Observability, Log Analytics [^11_2][^11_10] | root cause, AI 분석, 자동화 흐름 강함 | 대규모 엔터프라이즈, AIOps |
| Prometheus + Grafana | Prometheus alert/query, Grafana dashboards [^11_3][^11_7][^11_6] | 높은 유연성, GPU/K8s 친화 | 클라우드 네이티브, GPU 연구/플랫폼 |

## 대표 화면에서 봐야 할 것

관리자/운영자 화면에서 실제로 중요한 것은 “예쁜 대시보드”가 아니라 다음 정보입니다.

- 서비스/노드/컨테이너/GPU의 현재 상태.
- 장애 발생 시 root cause로 내려가는 경로.
- 동일 태그 기준의 메트릭, 로그, 트레이스 연결.
- 알람과 조치 이력.
- 용량 추세와 비용 신호.
- GPU의 경우 utilization, VRAM, ECC, temperature, power, XID, MIG 상태.[^11_18][^11_19][^11_20]


## 실무 결론

시장에서 가장 대표적인 운영 화면은 **Datadog의 통합 SaaS 화면**, **Dynatrace의 AI 기반 엔터프라이즈 화면**, **Prometheus+Grafana의 메트릭 중심 운영 화면**입니다.[^11_1][^11_2][^11_3][^11_4]
GPU까지 포함하면 Grafana DCGM 대시보드와 Dynatrace AI Observability, Datadog DCGM 연동이 핵심 후보이며, Prometheus/Grafana는 가장 유연한 오픈소스 표준 조합입니다.[^11_9][^11_10][^11_14][^11_16]

원하시면 다음 단계로 **각 플랫폼의 실제 대표 화면 유형을 “메인 홈 / 인프라 맵 / 알람 / 드릴다운 / GPU 대시보드” 기준으로 이미지 중심 비교표**로 더 구체화해 드리겠습니다.
<span style="display:none">[^11_21][^11_22][^11_23][^11_24][^11_25][^11_26][^11_27][^11_28][^11_29][^11_30][^11_31]</span>

<div align="center">⁂</div>

[^11_1]: https://www.datadoghq.com/monitoring/cloud-observability/

[^11_2]: https://www.dynatrace.com/

[^11_3]: https://prometheus.io/docs/introduction/overview/

[^11_4]: https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/gpu-observability/setup/

[^11_5]: https://www.dynatrace.com/hub/detail/ai-and-llm-observability/

[^11_6]: https://grafana.com/grafana/dashboards/19105-prometheus/

[^11_7]: https://prometheus.io/docs/alerting/latest/

[^11_8]: https://www.datadoghq.com/blog/announcing-logs/

[^11_9]: https://docs.datadoghq.com/integrations/dcgm/

[^11_10]: https://docs.dynatrace.com/docs/observe/dynatrace-for-ai-observability/ai-observability-app

[^11_11]: https://www.youtube.com/watch?v=EGgtJUjky8w

[^11_12]: https://wikidocs.net/299178

[^11_13]: https://docs.kakaocloud.com/tutorial/observability/grafana-monitoring

[^11_14]: https://grafana.com/grafana/dashboards/24450-nvidia-dcgm-exporter-dashboard/

[^11_15]: https://grafana.com/grafana/dashboards/22515-nvidia-dcgm-dashboard/

[^11_16]: https://docs.nvidia.com/datacenter/cloud-native/openshift/24.9.1/enable-gpu-monitoring-dashboard.html

[^11_17]: https://developer.nvidia.com/blog/monitoring-gpus-in-kubernetes-with-dcgm/

[^11_18]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^11_19]: https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html

[^11_20]: https://devopsbeast.com/blog/dcgm-prometheus-gpu-observability

[^11_21]: https://zerobin-dev.tistory.com/172

[^11_22]: https://www.cisco.com/c/ko_kr/support/docs/security/secure-malware-analytics/221943-how-to-configure-remote-prometheus-and-g.pdf

[^11_23]: https://github.com/RisingStack/training-microservices/blob/master/examples/prometheus-monitoring/grafana-dashboard.json

[^11_24]: https://github.com/mehdi-fathi/grafana-dashboards-1

[^11_25]: https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-opntlmtry_prometheus_dashboard\&locale=ko

[^11_26]: https://velog.io/@dev_ssj/Monitoring-Prometheus%EC%99%80-Grafana%EB%A1%9C-%EC%8B%A4%EC%8B%9C%EA%B0%84-%EB%AA%A8%EB%8B%88%ED%84%B0%EB%A7%81-%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C-%EA%B5%AC%EC%B6%95%ED%95%98%EA%B8%B0

[^11_27]: https://github.com/blbird/PrometheusSampleApp

[^11_28]: https://whdrns2013.github.io/ops/20250430_001_grafana/

[^11_29]: https://community.dynatrace.com/t5/Automations/Workflow-to-Take-a-Screenshot-of-a-Dashboard-when-an-Event-Is/m-p/263613

[^11_30]: https://cdchan.tistory.com/282

[^11_31]: https://velog.io/@ckr3453/Grafana를-이용하여-수집한-metric을-대시보드로-구성


---

# 다음 단계의 이미지 중심 비교표를 작성해 주시고, 세부 이미지의 상세이미지도 다운로드할 수 있도록 조사해서 정리해 주세요.

아래에 **이미지 중심 비교표**를 먼저 정리하고, 이어서 **세부 이미지 다운로드용 목록**을 플랫폼별로 분류해 두었습니다. 대표 화면은 Datadog, Dynatrace, Prometheus+Grafana 조합이 가장 실무적이며, GPU 관측은 Grafana DCGM 대시보드가 사실상 표준 출발점입니다.[^12_1][^12_2]

## 이미지 중심 비교표

| 플랫폼 | 대표 관리자 화면 | 화면에서 바로 보이는 것 | 운영자 관점 강점 | 참고 이미지 |
| :-- | :-- | :-- | :-- | :-- |
| Datadog | SLO/대시보드, 인프라 맵, 로그/트레이스 연계 화면 | 성능 지표, 서비스 수준, 위젯 기반 KPI, 알람 상태 | 메트릭·로그·트레이스를 하나의 UI에서 빠르게 드릴다운 [^12_3][^12_4][^12_5] |  |
| Dynatrace | 환경 맵, dashboards, 문제/원인 분석, AI 관측성 화면 | 서비스 토폴로지, health state, root cause, 영향 범위 | 자동 발견과 AI 분석이 강하고 엔터프라이즈 운영 흐름이 좋음 [^12_6][^12_7][^12_8] |  |
| Prometheus + Grafana | Prometheus query/alert + Grafana dashboard | 시계열 차트, gauge, table, GPU/서버 상태 | 오픈소스 표준 조합, GPU와 쿠버네티스에 유리 [^12_9][^12_10][^12_11] |  |

## Datadog 화면

Datadog의 대표 화면은 **SLO 대시보드, 인프라 모니터링, 위젯형 KPI 화면**입니다. 운영자 입장에서는 “전체 상태를 한 눈에 보고, 문제가 있으면 로그/트레이스까지 빠르게 내려가는 구조”가 핵심입니다. GPU 환경에서는 DCGM Exporter 연동으로 GPU 메트릭을 같은 운영 흐름 안에서 볼 수 있습니다.[^12_3][^12_4][^12_5][^12_12]

## Dynatrace 화면

Dynatrace는 **토폴로지 기반 환경 뷰, 문제 진단, AI 관측성, 대시보드 편집 화면**이 대표적입니다. 이 플랫폼은 문제 목록에서 root cause, 영향 서비스, 관련 로그/트레이스를 자동으로 엮는 흐름이 강해 엔터프라이즈 운영자에게 적합합니다. GPU/AI 워크로드도 AI Observability와 인프라 관측성에서 함께 다룰 수 있습니다.[^12_6][^12_7][^12_8]

## Prometheus + Grafana 화면

Prometheus는 수집과 경보, Grafana는 시각화를 담당하므로 실제 대표 화면은 **Grafana 대시보드**가 중심입니다. 일반 서버 대시보드에서는 CPU, 메모리, 디스크, 네트워크가 보이고, GPU 대시보드에서는 temperature, power, VRAM, utilization, ECC 같은 항목이 핵심입니다. Kubernetes와 GPU 클러스터에서는 이 조합이 가장 유연합니다.[^12_1][^12_2][^12_9][^12_13][^12_14][^12_15]

## 다운로드용 세부 이미지

아래 이미지는 각각 별도 다운로드 가능한 세부 화면 예시입니다.

### Datadog

- 인프라/대시보드 예시:
- 대시보드 위젯형 화면:
- 퍼센트 지표 중심 화면:


### Dynatrace

- 대시보드 생성/편집 화면:
- 세계지도/메트릭 중심 운영 화면:
- 서비스/서비스 상태 개요 화면:


### Grafana / GPU

- 일반 Grafana 운영 대시보드:
- GPU 메트릭 대시보드 예시:
- GPU 및 애플리케이션 지표 혼합 화면:


## 실무적으로 보는 차이

Datadog은 **빠른 도입과 단일 SaaS 경험**이 강하고, Dynatrace는 **자동 분석과 엔터프라이즈 운영 흐름**이 강합니다. Prometheus+Grafana는 **표준성, GPU/Kubernetes 친화성, 커스터마이징**이 강합니다.[^12_1][^12_3][^12_6][^12_7][^12_9][^12_10]
즉, 화면 디자인까지 포함하면 Datadog은 “운영자 친화적 통합 화면”, Dynatrace는 “분석 중심 AI 화면”, Grafana는 “세밀한 시계열 운영 화면”으로 이해하면 가장 정확합니다.[^12_3][^12_6][^12_11]

원하시면 다음 단계로 **이미지별 캡션을 붙인 다운로드 목록 표** 또는 **플랫폼별 화면 구성 체크리스트(메인 홈, 인프라 맵, 알람, 드릴다운, GPU 대시보드)**로 더 정리해 드리겠습니다.

<div align="center">⁂</div>

[^12_1]: https://grafana.com/grafana/dashboards/24450-nvidia-dcgm-exporter-dashboard/

[^12_2]: https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/gpu-observability/setup/

[^12_3]: https://www.datadoghq.com/monitoring/cloud-observability/

[^12_4]: https://www.datadoghq.com/monitoring/unified-monitoring/

[^12_5]: https://www.datadoghq.com/blog/announcing-logs/

[^12_6]: https://www.dynatrace.com/

[^12_7]: https://www.dynatrace.com/hub/detail/ai-and-llm-observability/

[^12_8]: https://docs.dynatrace.com/docs/observe/dynatrace-for-ai-observability/ai-observability-app

[^12_9]: https://prometheus.io/docs/introduction/overview/

[^12_10]: https://prometheus.io/docs/alerting/latest/

[^12_11]: https://grafana.com/grafana/dashboards/19105-prometheus/

[^12_12]: https://docs.datadoghq.com/integrations/dcgm/

[^12_13]: https://docs.nvidia.com/datacenter/cloud-native/openshift/24.9.1/enable-gpu-monitoring-dashboard.html

[^12_14]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^12_15]: https://nvidia.github.io/dcgm-exporter/


---

# 이미지별 캡션을 붙인 다운로드 목록 표와 플랫폼별 화면 구성 체크리스트(메인 홈, 인프라 맵, 알람, 드릴다운, GPU 대시보드)로 더 정리해 주세요.

아래처럼 정리하면 실무에서 바로 쓸 수 있습니다. **다운로드 목록 표**는 “어떤 이미지가 무엇을 보여주는지”를 빠르게 고를 수 있게 하고, **화면 구성 체크리스트**는 각 플랫폼의 관리자/운영자 화면을 설계할 때 기준이 됩니다. Datadog은 대시보드 중심, Dynatrace는 토폴로지·원인분석 중심, Prometheus+Grafana는 시계열·GPU 대시보드 중심으로 보면 가장 정확합니다.[^13_1][^13_2][^13_3][^13_4]

## 이미지 다운로드 목록

| 플랫폼 | 이미지 | 캡션 | 활용 포인트 |
| :-- | :-- | :-- | :-- |
| Datadog |  | Datadog SLO view와 대시보드 위젯 화면 | SLA/SLO, 서비스 상태, 운영 KPI 요약 |
| Datadog |  | 다크 테마 기반 Datadog 대시보드 화면 | 서비스 상태, 차트 중심 운영 화면 |
| Datadog |  | 퍼센트 지표 중심 Datadog 대시보드 화면 | 경영진/운영 요약 대시보드 |
| Dynatrace |  | Dynatrace 대시보드 생성/편집 화면 | 운영자가 직접 패널 구성하는 화면 |
| Dynatrace |  | Dynatrace 차트·지도·메트릭 패널 화면 | 토폴로지와 상태를 함께 보는 화면 |
| Dynatrace |  | 서비스·synthetic·release 중심 개요 화면 | 애플리케이션 운영 개요 |
| Grafana/GPU |  | Grafana 기반 GPU/서버 모니터링 화면 | 일반 인프라 대시보드 |
| Grafana/GPU |  | NVIDIA GPU 메트릭 대시보드 | GPU utilization, memory, temp, power |
| Grafana/GPU |  | Grafana 대시보드 예시 화면 | 상세 시계열·지표 테이블 구성 참고 |

## 플랫폼별 화면 구성 체크리스트

### Datadog

- **메인 홈**: 서비스 상태 요약, 에러율, latency, SLO 달성률, 최근 incident.
- **인프라 맵**: Host and Container Map, 클러스터/호스트/컨테이너 상태 색상 구분.
- **알람**: monitor 목록, alert 상태, notification routing, Watchdog.
- **드릴다운**: 로그, 트레이스, 프로파일러, APM endpoint로 연결.
- **GPU 대시보드**: GPU utilization, VRAM, temperature, power, process별 점유, 노드별 필터.
- **권장 특징**: 운영자용 상위 요약과 문제 해결용 상세 분석이 같은 UI에서 이어져야 함.[^13_2][^13_5][^13_6][^13_7]


### Dynatrace

- **메인 홈**: 문제/이벤트 요약, health state, AI가 추린 우선순위 문제.
- **인프라 맵**: Smartscape/토폴로지 형태의 서비스-호스트-프로세스 관계.
- **알람**: 문제 목록, root cause candidate, 영향 범위, 자동 분류.
- **드릴다운**: 서비스 흐름, 트레이스, 로그, 사용자 경험, 변경 이벤트.
- **GPU 대시보드**: AI Observability와 인프라 관측성 결합, GPU/AI workload 추적.
- **권장 특징**: “무슨 일이 생겼는가”보다 “왜 생겼는가”를 먼저 보여줘야 함.[^13_1][^13_8][^13_9][^13_10]


### Prometheus + Grafana

- **메인 홈**: 핵심 시스템 KPI, scrape health, alert 상태, 전반적 utilization.
- **인프라 맵**: Grafana의 node/cluster overview 패널, 서비스별 상태표.
- **알람**: Prometheus alert rules, Alertmanager routing, firing/pending 상태.
- **드릴다운**: Grafana dashboard 변수, 라벨 필터, time range 확대.
- **GPU 대시보드**: DCGM Exporter 기반 GPU temperature, power, utilization, VRAM, ECC, Tensor Core Utilization.
- **권장 특징**: 표준 템플릿을 기반으로 “fleet → node → GPU → job” 계층을 분리하는 것이 좋음.[^13_11][^13_12][^13_13][^13_4]


## 화면 구성 우선순위

운영자 화면은 아래 순서로 설계하면 좋습니다.

1. **메인 홈**에서 건강 상태와 SLO를 먼저 보여준다.
2. **인프라 맵**으로 장애 범위를 즉시 파악하게 한다.
3. **알람**에서 현재 조치가 필요한 항목만 남긴다.
4. **드릴다운**에서 로그/트레이스/메트릭을 연결한다.
5. **GPU 대시보드**에서 VRAM, 온도, 전력, utilization, ECC를 분리해 본다.[^13_13][^13_2][^13_4][^13_8]

## GPU 대시보드 필수 항목

OpenShift/NVIDIA 문서 기준으로 GPU 대시보드에 기본 포함되는 그래프는 GPU Temperature, GPU Avg. Temp, GPU Power Usage, GPU Power Total, GPU SM Clocks, GPU Utilization, GPU Framebuffer Mem Used, Tensor Core Utilization입니다.[^13_13]
실무에서는 여기에 **VRAM free/used, per-process memory, XID, ECC, NVLink/PCIe throughput, MIG 분할 상태**를 추가하는 구성이 일반적입니다.[^13_11][^13_14][^13_12][^13_15]

## 추천 정리 방식

문서를 만들 때는 플랫폼별로 아래 형식을 쓰면 가장 이해가 쉽습니다.

- **화면 이름**
- **주요 목적**
- **보여주는 핵심 지표**
- **운영자가 이 화면에서 하는 일**
- **GPU 관련 항목**
- **드릴다운 경로**

이 방식으로 정리하면, 경영진용 요약 화면과 SRE/플랫폼 엔지니어용 상세 화면을 깔끔하게 분리할 수 있습니다.
원하시면 다음 답변에서 이 내용을 바로 **표준 보고서 형식으로 재구성한 버전**으로 정리해 드리겠습니다.
<span style="display:none">[^13_16][^13_17][^13_18][^13_19][^13_20][^13_21][^13_22][^13_23][^13_24]</span>

<div align="center">⁂</div>

[^13_1]: https://www.dynatrace.com/ko/

[^13_2]: https://docs.datadoghq.com/ko/getting_started/dashboards/

[^13_3]: https://prometheus.io/docs/introduction/overview/

[^13_4]: https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/gpu-observability/setup/

[^13_5]: https://www.datadoghq.com/monitoring/cloud-observability/

[^13_6]: https://www.datadoghq.com/monitoring/unified-monitoring/

[^13_7]: https://www.datadoghq.com/blog/announcing-logs/

[^13_8]: https://www.dynatrace.com/

[^13_9]: https://www.dynatrace.com/hub/detail/ai-and-llm-observability/

[^13_10]: https://docs.dynatrace.com/docs/observe/dynatrace-for-ai-observability/ai-observability-app

[^13_11]: https://grafana.com/grafana/dashboards/23382-nvidia-mig-dcgm/

[^13_12]: https://grafana.com/grafana/dashboards/24450-nvidia-dcgm-exporter-dashboard/

[^13_13]: https://docs.nvidia.com/datacenter/cloud-native/openshift/latest/enable-gpu-monitoring-dashboard.html

[^13_14]: https://yandex.cloud/en/docs/stackland/concepts/cluster-monitoring/nvidia-dcgm-mig-monitoring

[^13_15]: https://devopsbeast.com/blog/dcgm-prometheus-gpu-observability

[^13_16]: https://lillytechsystems.com/ai-school/gpu-monitoring/grafana-gpu.html

[^13_17]: https://highitking.com/📊-gpu-모니터링-대시보드-grafana와-dcgm으로-엔비디아-지표-시/

[^13_18]: https://github.com/AuraAiLab/GrafanaDashboards

[^13_19]: https://www.youtube.com/watch?v=5WcfzHtfvuo

[^13_20]: https://www.boolsee.pe.kr/on-prem_ai_services-2-prometheus-grafana-dashboard/

[^13_21]: https://docs.datadoghq.com/ko/dashboards/list/

[^13_22]: https://developer.nvidia.com/blog/monitoring-gpus-in-kubernetes-with-dcgm/

[^13_23]: https://docs.kakaocloud.com/tutorial/observability/nvidia-gpu-monitoring

[^13_24]: https://grafana.com/grafana/dashboards/18288-nvidia-gpu/


---

# Build an Observability Dashboard Comparison Matrix: UI components, filtering, and layout efficiency by platform

Prometheus와 Grafana를 활용한 GPU 메트릭 수집 파이프라인 구성도

요청하신 내용을 **대시보드형 비교 문서**로 제작했습니다. 이 문서는 **Observability Dashboard Comparison Matrix**와 **Prometheus + Grafana 기반 GPU 메트릭 수집 파이프라인 구성도**를 함께 담고 있습니다.[^14_1][^14_2][^14_3][^14_4]

## 포함 내용

문서에는 다음이 포함되어 있습니다.

- Datadog, Dynatrace, Prometheus+Grafana의 **UI components 비교**[^14_2][^14_3][^14_4]
- 플랫폼별 **filtering model과 scope control 비교**[^14_5][^14_3][^14_6]
- 운영자 관점의 **layout efficiency 평가**[^14_6][^14_4][^14_2]
- **GPU metric collection pipeline diagram**: GPU node → DCGM Exporter → Prometheus → Grafana[^14_7][^14_8][^14_9][^14_1]


## 핵심 해석

Datadog은 위젯 조합과 통합 SaaS 흐름이 강해 **빠른 운영 화면 구성**에 유리합니다. Dynatrace는 management zone과 dashboard filters가 강해 **조직 단위 scope 분리와 root-cause 중심 운영**에 유리합니다. Prometheus+Grafana는 DCGM Exporter와 결합해 **GPU/AI 클러스터용 커스텀 대시보드**를 만들기 가장 좋은 경로입니다.[^14_10][^14_3][^14_8][^14_4][^14_11][^14_5][^14_1][^14_2][^14_6]

## 문서 활용

이 결과물은 내부 검토용 보고서이면서 동시에 **화면 설계 레퍼런스**로도 쓸 수 있게 만들었습니다. 특히 GPU 파이프라인 도식은 Kubernetes 기반 운영팀이나 AI 인프라팀이 Prometheus/Grafana 구조를 설명할 때 바로 활용할 수 있습니다.[^14_12][^14_8][^14_9]
<span style="display:none">[^14_13][^14_14][^14_15][^14_16]</span>

<div align="center">⁂</div>

[^14_1]: https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html

[^14_2]: https://docs.datadoghq.com/dashboards/

[^14_3]: https://docs.dynatrace.com/docs/analyze-explore-automate/dashboards-classic/dashboards/dashboards-filters

[^14_4]: https://grafana.com/grafana/dashboards/24450-nvidia-dcgm-exporter-dashboard/

[^14_5]: https://docs.dynatrace.com/docs/manage/identity-access-management/permission-management/management-zones/apply-and-use-management-zones

[^14_6]: https://www.dynatrace.com/news/blog/organize-your-dashboards-more-effectively/

[^14_7]: https://grafana.com/grafana/dashboards/15117-nvidia-dcgm-exporter/

[^14_8]: https://nvidia.github.io/dcgm-exporter/

[^14_9]: https://grafana.com/grafana/dashboards/12219-nvidia-dcgm-exporter-dashboard/

[^14_10]: https://docs.datadoghq.com/getting_started/dashboards/

[^14_11]: https://grafana.com/grafana/dashboards/23382-nvidia-mig-dcgm/

[^14_12]: https://developer.nvidia.com/blog/monitoring-gpus-in-kubernetes-with-dcgm/

[^14_13]: https://www.servermo.com/howto/monitor-nvidia-gpu-prometheus-grafana/

[^14_14]: https://community.dynatrace.com/t5/Dashboarding/Filter-by-Management-Zone-using-DQL/m-p/247035

[^14_15]: https://learn.microsoft.com/en-us/azure/azure-monitor/containers/prometheus-dcgm-integration

[^14_16]: https://mindcloud.co/docs/universal/rest/datadog/latest/actions/list-dashboards

