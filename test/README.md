# 시험 표준 / Testing Standard

> **wise-dev-standard / python-fastapi** 시험 규칙 준수  
> Runner: `pytest + httpx` (backend) · `Vitest + Playwright` (frontend)

## 디렉터리 구조

```
test/
├── README.md          ← 이 파일
├── dev-env/           ← 표준 환경 검증 (최초 1회)
│   ├── scenario.md
│   └── logs/          ← git 미추적 (.gitignore)
└── impl/              ← 구현마다 /wise-dev-standard:implement 가 <Nth>/ 생성
```

## 시험 사이클

```
시나리오 작성 → 시험 진행 → 오류 시 수정·재시험 → 시험결과 작성
```

## 실행

```bash
make test           # pytest 전체
uv run pytest test/dev-env/   # 환경 검증만
uv run pytest test/impl/1/    # 1번째 구현 시험
```
