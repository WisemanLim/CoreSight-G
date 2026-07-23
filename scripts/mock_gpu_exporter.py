"""Mock GPU/HW 메트릭 exporter — 로컬 개발용 (실 GPU 없는 환경).

DCGM Exporter 와 동일한 메트릭 이름으로 GPU 4장 + 서버 하드웨어 지표를 생성한다.
운영 환경에서는 이 컨테이너 대신 실제 DCGM Exporter / node_exporter / ipmi_exporter 를 사용.

실행: python scripts/mock_gpu_exporter.py  (PORT 기본 9400, MOCK_ANOMALY=1 시 GPU3 이상 신호)
의존성: 표준 라이브러리만 사용 (컨테이너에서 pip install 불필요).
"""
import os
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("PORT", "9400"))
HOSTNAME = os.getenv("MOCK_HOSTNAME", "gpu-node-01")
NUM_GPUS = int(os.getenv("MOCK_NUM_GPUS", "4"))
ANOMALY = os.getenv("MOCK_ANOMALY", "0") == "1"

FB_TOTAL_MIB = 81920  # A100 80GB 기준
_START = time.time()

# 워크로드 상관 (P2-7 workload-correlator): 고정 pid/job/user 목록 — GPU 0~2 에 프로세스 배치
_PROCESSES = [
    {"gpu": "0", "pid": "10231", "job_id": "job-7a1", "user": "alice"},
    {"gpu": "1", "pid": "10232", "job_id": "job-7a1", "user": "alice"},
    {"gpu": "2", "pid": "20450", "job_id": "job-9f3", "user": "bob"},
]


def _gpu_lines() -> list[str]:
    lines = [
        "# HELP DCGM_FI_DEV_GPU_UTIL GPU utilization (%).",
        "# TYPE DCGM_FI_DEV_GPU_UTIL gauge",
    ]
    metrics: list[tuple[str, str]] = []
    for i in range(NUM_GPUS):
        label = f'gpu="{i}",UUID="GPU-mock-{i:04d}",Hostname="{HOSTNAME}"'
        # GPU0~2: 정상 워크로드 흔들림, GPU3: ANOMALY 시 과열+XID
        util = random.uniform(55, 95) if i < 3 else random.uniform(5, 15)
        temp = random.uniform(55, 70) if not (ANOMALY and i == 3) else random.uniform(88, 95)
        power = random.uniform(250, 380)
        fb_used = random.uniform(0.5, 0.85) * FB_TOTAL_MIB
        xid = 0 if not (ANOMALY and i == 3) else int((time.time() - _START) // 60) + 1
        ecc_dbe = 0 if not (ANOMALY and i == 3) else 2
        # 고급 프로파일링 지표 (P2-3 gpu-profiler): SM/Tensor/DRAM/throttle/PCIe/MIG
        throttle = 0 if not (ANOMALY and i == 3) else 1  # bitmask: 1=thermal
        metrics += [
            (f"DCGM_FI_DEV_GPU_UTIL{{{label}}}", f"{util:.1f}"),
            (f"DCGM_FI_DEV_FB_USED{{{label}}}", f"{fb_used:.0f}"),
            (f"DCGM_FI_DEV_FB_TOTAL{{{label}}}", f"{FB_TOTAL_MIB}"),
            (f"DCGM_FI_DEV_GPU_TEMP{{{label}}}", f"{temp:.0f}"),
            (f"DCGM_FI_DEV_POWER_USAGE{{{label}}}", f"{power:.1f}"),
            (f"DCGM_FI_DEV_XID_ERRORS{{{label}}}", f"{xid}"),
            (f"DCGM_FI_DEV_ECC_DBE_VOL_TOTAL{{{label}}}", f"{ecc_dbe}"),
            (f"DCGM_FI_PROF_SM_OCCUPANCY{{{label}}}", f"{random.uniform(0.3, 0.85):.3f}"),
            (f"DCGM_FI_PROF_PIPE_TENSOR_ACTIVE{{{label}}}", f"{random.uniform(0.1, 0.7):.3f}"),
            (f"DCGM_FI_PROF_DRAM_ACTIVE{{{label}}}", f"{random.uniform(0.2, 0.9):.3f}"),
            (f"DCGM_FI_DEV_CLOCK_THROTTLE_REASONS{{{label}}}", f"{throttle}"),
            (f"DCGM_FI_PROF_PCIE_TX_BYTES{{{label}}}", f"{random.uniform(1e8, 8e8):.0f}"),
            (f"DCGM_FI_PROF_PCIE_RX_BYTES{{{label}}}", f"{random.uniform(1e8, 8e8):.0f}"),
        ]
    lines += [f"{k} {v}" for k, v in metrics]

    # 워크로드 상관: GPU 별 프로세스 메모리 점유 (job_id/user 라벨 포함)
    for p in _PROCESSES:
        mem = random.uniform(4000, 30000)
        lines.append(
            f'DCGM_FI_DEV_GPU_PROCESS_MEM_USED{{gpu="{p["gpu"]}",pid="{p["pid"]}",'
            f'job_id="{p["job_id"]}",user="{p["user"]}",Hostname="{HOSTNAME}"}} {mem:.0f}'
        )
    return lines


def _hw_lines() -> list[str]:
    node = f'Hostname="{HOSTNAME}"'
    mem_total = 512 * 1024**3
    mem_avail = random.uniform(0.3, 0.6) * mem_total
    return [
        f'hw_cpu_usage_percent{{{node}}} {random.uniform(20, 75):.1f}',
        f'hw_memory_total_bytes{{{node}}} {mem_total}',
        f'hw_memory_available_bytes{{{node}}} {mem_avail:.0f}',
        # 스토리지 (P2-1 storage-monitor): latency/IOPS/SMART/NVMe wear
        f'hw_disk_read_latency_ms{{{node},device="nvme0n1"}} {random.uniform(0.2, 2.5):.2f}',
        f'hw_disk_write_latency_ms{{{node},device="nvme0n1"}} {random.uniform(0.3, 3.0):.2f}',
        f'hw_disk_read_latency_ms{{{node},device="sda"}} '
        f'{random.uniform(4, 12) if not ANOMALY else random.uniform(80, 200):.2f}',
        f'hw_disk_write_latency_ms{{{node},device="sda"}} {random.uniform(5, 15):.2f}',
        f'hw_disk_iops{{{node},device="nvme0n1",op="read"}} {random.uniform(5000, 20000):.0f}',
        f'hw_disk_iops{{{node},device="nvme0n1",op="write"}} {random.uniform(2000, 9000):.0f}',
        f'hw_disk_iops{{{node},device="sda",op="read"}} {random.uniform(80, 250):.0f}',
        f'hw_disk_iops{{{node},device="sda",op="write"}} {random.uniform(40, 120):.0f}',
        f'hw_smart_healthy{{{node},device="nvme0n1"}} 1',
        f'hw_smart_healthy{{{node},device="sda"}} {0 if ANOMALY else 1}',
        f'hw_nvme_wear_level_percent{{{node},device="nvme0n1"}} {random.uniform(3, 8):.1f}',
        f'hw_raid_degraded{{{node},controller="megaraid0"}} {1 if ANOMALY else 0}',
        # BMC/IPMI (P2-2 bmc-monitor): 팬·전압·섀시 전력
        f'hw_fan_speed_rpm{{{node},fan="fan1"}} '
        f'{random.uniform(4000, 9000) if not ANOMALY else random.uniform(300, 800):.0f}',
        f'hw_fan_speed_rpm{{{node},fan="fan2"}} {random.uniform(4000, 9000):.0f}',
        f'hw_voltage_volts{{{node},rail="12V"}} '
        f'{random.uniform(11.9, 12.2) if not ANOMALY else random.uniform(10.8, 11.2):.2f}',
        f'hw_voltage_volts{{{node},rail="5V"}} {random.uniform(4.95, 5.08):.2f}',
        f'hw_voltage_volts{{{node},rail="3.3V"}} {random.uniform(3.28, 3.36):.2f}',
        f'hw_bmc_power_watts{{{node}}} {random.uniform(900, 1600):.0f}',
        f'hw_psu_status{{{node},psu="psu1"}} 1',
        f'hw_psu_status{{{node},psu="psu2"}} 1',
        f'hw_inlet_temp_celsius{{{node}}} {random.uniform(22, 30):.1f}',
        # 네트워크 (P2-6 net-monitor): 인터페이스 오류/드롭/처리량/링크상태
        f'hw_nic_errors_total{{{node},nic="eth0"}} {0 if not ANOMALY else int((time.time() - _START) // 10) + 1}',
        f'hw_nic_drops_total{{{node},nic="eth0"}} {0 if not ANOMALY else int((time.time() - _START) // 5) + 1}',
        f'hw_nic_errors_total{{{node},nic="eth1"}} 0',
        f'hw_nic_drops_total{{{node},nic="eth1"}} 0',
        f'hw_nic_link_up{{{node},nic="eth0"}} 1',
        f'hw_nic_link_up{{{node},nic="eth1"}} {0 if ANOMALY else 1}',
        f'hw_nic_rx_bytes_per_sec{{{node},nic="eth0"}} {random.uniform(1e7, 9e8):.0f}',
        f'hw_nic_tx_bytes_per_sec{{{node},nic="eth0"}} {random.uniform(1e7, 9e8):.0f}',
        f'hw_nic_rx_bytes_per_sec{{{node},nic="eth1"}} {random.uniform(1e6, 5e7):.0f}',
        f'hw_nic_tx_bytes_per_sec{{{node},nic="eth1"}} {random.uniform(1e6, 5e7):.0f}',
    ]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            return
        body = "\n".join(_gpu_lines() + _hw_lines() + [""]).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # 소음 억제
        pass


if __name__ == "__main__":
    print(f"mock exporter :{PORT} host={HOSTNAME} gpus={NUM_GPUS} anomaly={ANOMALY}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
