"""Mock 로그 생성기 — 로컬 개발용 (실 GPU 노드 없는 환경).

syslog/dmesg/BMC 스타일 로그를 Loki push API 로 주기 전송한다.
운영 환경에서는 이 컨테이너 대신 Promtail/Alloy 가 실 노드 로그를 수집.

실행: python scripts/mock_log_generator.py
환경: LOKI_URL(기본 http://loki:3100), MOCK_HOSTNAME, INTERVAL_SEC(기본 5),
      MOCK_ANOMALY=1 시 XID/RAID 오류 로그 주입.
의존성: 표준 라이브러리만 사용.
"""
import json
import os
import random
import time
import urllib.request

LOKI_URL = os.getenv("LOKI_URL", "http://loki:3100")
HOSTNAME = os.getenv("MOCK_HOSTNAME", "gpu-node-01")
INTERVAL = float(os.getenv("INTERVAL_SEC", "5"))
ANOMALY = os.getenv("MOCK_ANOMALY", "0") == "1"

_SYSLOG = [
    ("info", "systemd[1]: Started Session {n} of user mluser."),
    ("info", "sshd[{n}]: Accepted publickey for mluser from 10.0.0.{m}"),
    ("info", "containerd[812]: pulled image registry.local/train-job:{n}"),
    ("warning", "kernel: TCP: request_sock_TCP: Possible SYN flooding on port 8100."),
]
_DMESG = [
    ("info", "NVRM: GPU at PCI:0000:{m:02x}:00: GPU-mock-000{g}"),
    ("info", "nvidia {g}: firmware runtime services enabled"),
    ("warning", "pcieport 0000:{m:02x}:00.0: AER: Corrected error received"),
]
_BMC = [
    ("info", "IPMI: fan{g} speed {n} RPM within threshold"),
    ("info", "iDRAC: power supply psu1 status OK"),
]
_ANOMALY = [
    ("dmesg", "error", "NVRM: Xid (PCI:0000:0c:00): 79, GPU has fallen off the bus."),
    ("dmesg", "error", "EXT4-fs error (device sda1): ext4_find_entry: reading directory lblock 0"),
    ("bmc", "error", "iDRAC: RAID controller megaraid0 virtual disk 0 DEGRADED"),
    ("syslog", "error", "nvidia-dcgm[1201]: ECC double-bit error detected on GPU 3"),
]


def _push(job: str, level: str, line: str) -> None:
    payload = {
        "streams": [
            {
                "stream": {"job": job, "level": level, "Hostname": HOSTNAME},
                "values": [[str(time.time_ns()), line]],
            }
        ]
    }
    req = urllib.request.Request(
        f"{LOKI_URL}/loki/api/v1/push",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5).read()
    except Exception as exc:  # noqa: BLE001
        print(f"push 실패: {exc}", flush=True)


def _tick() -> None:
    n, m, g = random.randint(100, 9999), random.randint(2, 250), random.randint(0, 3)
    job, pool = random.choice([("syslog", _SYSLOG), ("dmesg", _DMESG), ("bmc", _BMC)])
    level, tmpl = random.choice(pool)
    _push(job, level, tmpl.format(n=n, m=m, g=g))
    if ANOMALY and random.random() < 0.5:
        ajob, alevel, aline = random.choice(_ANOMALY)
        _push(ajob, alevel, aline)


if __name__ == "__main__":
    print(f"mock log generator → {LOKI_URL} host={HOSTNAME} anomaly={ANOMALY}", flush=True)
    while True:
        _tick()
        time.sleep(INTERVAL)
