# Addon Agent 가이드

> **CoreSight-G Platform**의 확장 모듈 시스템입니다.  
> 관리자가 커스텀 Agent(게시판, 설문, 재고 등)를 zip 파일로 만들어 업로드하면, 앱을 재시작하지 않고 즉시 API·DB가 배포(핫 디플로이)됩니다.  
> 프론트엔드 컴포넌트(`-front.tsx`)가 포함된 경우, 프론트엔드 재빌드 후 사이드바 메뉴에 자동으로 표시됩니다.

---

## Agent 만들기 방법

두 가지 방법 중 선택할 수 있습니다.

| 방법 | 설명 | 진입 |
|------|------|------|
| **스캐폴딩 Wizard** | 9종 유형 중 선택 → 이름/설명/도메인 입력 → ZIP 자동 생성 | 에이전트 관리 → 새 Agent 만들기 → **스캐폴딩 만들기** 탭 |
| **ZIP 업로드** | 직접 개발한 ZIP 파일 업로드 | 에이전트 관리 → 새 Agent 만들기 → **ZIP 업로드 등록** 탭 |

스캐폴딩 Wizard는 서버 API `/api/addon-agents/scaffold`를 통해 ZIP을 생성하며, "바로 배포" 버튼으로 즉시 등록도 가능합니다.

---

## 디렉터리 구조

```
addon-agents/
├── _templates/              개발용 템플릿 (완성본 zip 포함)
│   ├── _Skeleton/           App Agent 최소 골격 (init 베이스)
│   │   ├── Skeleton-app.py
│   │   ├── Skeleton-front.tsx
│   │   ├── Skeleton-sql.sql
│   ├── RagAgent/            RAG Agent — 문서 임베딩 + 벡터 검색 Q&A
│   │   ├── RagAgent-app.py
│   │   ├── RagAgent-sql.sql
│   │   └── RagAgent-meta.json
│   ├── ServiceAgent/        Service Agent — 백엔드 비즈니스 로직
│   │   ├── ServiceAgent-app.py
│   │   └── ServiceAgent-meta.json
│   ├── ToolProxyAgent/      Tool Proxy Agent — 외부 API → MCP 어댑터
│   │   ├── ToolProxyAgent-app.py
│   │   └── ToolProxyAgent-meta.json
│   ├── RagAgent.zip
│   ├── ServiceAgent.zip
│   └── ToolProxyAgent.zip
└── deployed/                업로드 후 자동 생성 (내장 에이전트 제외: 직접 편집 금지)
    └── {agent_key}/
        ├── {AgentName}-app.py
        ├── {AgentName}-front.tsx   (선택)
        ├── {AgentName}-sql.sql     (선택)
        └── {AgentName}-meta.json
```

> **내장 에이전트** (`deployed/board/`)는 git에 포함되어 있으며 앱 시작 시 자동 로드됩니다.

---

## 파일 명명 규칙

| 구성 요소 | 파일명 패턴 | 역할 |
|-----------|-------------|------|
| 메타데이터 | `{AgentName}-meta.json` | Agent 유형·capability·거버넌스 정의 (권장) |
| API 라우터 | `{AgentName}-app.py` | FastAPI `router` 객체 export (선택) |
| 프론트 컴포넌트 | `{AgentName}-front.tsx` | React 컴포넌트 — 독립형 i18n·다크모드 (선택) |
| DB 스키마 | `{AgentName}-sql.sql` | 테이블 생성 DDL, 자동 적용 (선택) |
| 완성 패키지 | `{AgentName}.zip` | 위 파일들을 루트에 flat zip |

> **AgentName**: PascalCase 권장 (예: `SurveyForm`, `Inventory`)  
> `-app.py` 또는 `-front.tsx` 중 최소 하나 필요합니다.  
> zip 내부는 서브디렉터리 없이 파일만 포함해야 합니다.

---

## Agent 개발 절차 (Makefile 사용)

`addon-agents/` 디렉터리의 **Makefile**로 초기화·검증·패키징을 자동화합니다.

```bash
# addon-agents/ 디렉터리에서 실행
cd addon-agents/

make init    AGENT=Survey   # 템플릿 스캐폴딩
make test    AGENT=Survey   # 구조·문법 검증
make publish AGENT=Survey   # zip 패키징
make clean   AGENT=Survey   # 생성 파일 삭제
```

| 타겟 | 설명 |
|------|------|
| `make init AGENT=<name>` | _Skeleton 템플릿 복사 + `Skeleton` → `<name>` 치환 → `_templates/<name>/` 생성 |
| `make test AGENT=<name>` | 파일 존재·Python 문법·router export·SQL 구조·React export 검증 |
| `make publish AGENT=<name>` | `_templates/<name>.zip` 생성 (업로드 준비) |
| `make clean AGENT=<name>` | 생성된 디렉터리 및 zip 삭제 |

---

## 파일 작성 가이드

### `{AgentName}-sql.sql`

- SQLite/PostgreSQL 공통 문법 권장 (`NOT is_deleted`, `CURRENT_TIMESTAMP`)
- 테이블명 접두사 `tbl_` 권장
- 모든 DDL에 `CREATE TABLE IF NOT EXISTS` 사용

```sql
CREATE TABLE IF NOT EXISTS tbl_myfeature (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    is_deleted  INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

> PostgreSQL 전용 문법(`SERIAL`, `BOOLEAN`, `NOW()`)은 업로드 시 자동 변환됩니다.

### `{AgentName}-app.py`

**필수 규칙:**
- `router` 변수명으로 `APIRouter` 인스턴스 export
- Wise 앱 모듈 사용: `from app.core.deps import get_current_user`, `from app.db import fetch_all, fetch_one, execute_write, execute_insert, _PH`
- 마운트 최종 경로: `/api/addon/{agent_key}/{prefix}/...`

```python
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.db import _PH, execute_insert, fetch_all

router = APIRouter(prefix="/items", tags=["myfeature"])

@router.get("")
async def list_items(user: dict = Depends(get_current_user)):
    return {"items": await fetch_all("SELECT * FROM tbl_myfeature WHERE NOT is_deleted")}
```

### `{AgentName}-front.tsx`

- API 호출 경로: `/api/addon/{agent_key}/{prefix}/...`
- `import client from "../../../api/client"` 사용 (Wise axios 인스턴스)
- **독립형 i18n**: `localStorage.getItem("locale")` + `localeChanged` 이벤트 구독
- **다크모드**: Tailwind `dark:` 클래스 (앱 테마와 자동 동기화)

```tsx
const LOCALE = { ko: { title: "내 기능" }, en: { title: "My Feature" } };

function useLocale() {
  const [locale, setLocale] = useState(() => localStorage.getItem("locale") || "ko");
  useEffect(() => {
    const h = () => setLocale(localStorage.getItem("locale") || "ko");
    window.addEventListener("localeChanged", h);
    return () => window.removeEventListener("localeChanged", h);
  }, []);
  return (k: string) => LOCALE[locale]?.[k] ?? LOCALE.ko[k] ?? k;
}

export default function MyFeaturePage() {
  const t = useLocale();
  return <h1 className="text-gray-800 dark:text-gray-100">{t("title")}</h1>;
}
```

### `{AgentName}-meta.json`

Orchestrator의 capability-based routing과 거버넌스 게이트에서 사용됩니다.

**agent_type 지원 목록:**

| agent_type | 용도 |
|------------|------|
| `app` | UI + CRUD 앱 (게시판, 설문 등) |
| `service` | 백엔드 비즈니스 로직 |
| `rag` | 문서 임베딩 + 벡터 검색 Q&A |
| `tool-proxy` | 외부 REST API → MCP 어댑터 |
| `reviewer` | 응답 품질·위험도 리뷰 게이트 |
| `execution` | 코드·명령 실행 Agent |
| `hitl` | Human-in-the-Loop 승인 게이트 |
| `memory` | 장기 메모리·컨텍스트 저장 |
| `federation` | 다른 Agent 시스템 연결 |

**전체 스키마:**

```json
{
  "agent_type": "service",
  "version": "1.0.0",
  "display_name": "내 Agent",
  "description": "Agent 설명",
  "capabilities": [
    {
      "verb": "process",
      "domain": "service.myfeature",
      "description": "기능 설명",
      "input_schema": {
        "type": "object",
        "properties": { "input": { "type": "object" } },
        "required": ["input"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "output": { "type": "object" },
          "status": { "type": "string" }
        }
      },
      "qos": {
        "max_latency_ms": 10000,
        "supports_async": true,
        "supports_streaming": true
      }
    }
  ],
  "governance": {
    "data_classification": "internal",
    "human_approval_required": false,
    "audit_level": "standard"
  },
  "required_env": [],
  "optional_env": ["ANTHROPIC_API_KEY"],
  "min_platform_version": "2.0.0"
}
```

| 필드 | 설명 |
|------|------|
| `capabilities[].verb` | Orchestrator가 intent 라우팅에 사용 (`retrieve`, `process`, `proxy`, `manage` 등) |
| `capabilities[].domain` | `{category}.{subdomain}` 형식 |
| `governance.human_approval_required` | `true` 시 HITL 게이트 강제 |
| `required_env` | 미설정 시 배포 경고 (예: `TOOL_PROXY_BASE_URL`) |
| `optional_env` | 기능 향상 선택 환경변수 (예: `ANTHROPIC_API_KEY`) |
| `min_platform_version` | 하위 플랫폼 버전 호환성 체크 |

---

## zip 패키징 및 업로드

```bash
# Makefile 사용 (권장)
make publish AGENT=MyFeature
# → _templates/MyFeature.zip 생성

# 수동
zip -j _templates/MyFeature.zip \
    _templates/MyFeature/MyFeature-app.py \
    _templates/MyFeature/MyFeature-front.tsx \
    _templates/MyFeature/MyFeature-sql.sql
```

### 업로드 절차

1. **에이전트 관리** 페이지 → **새 Agent 만들기** 버튼 → **ZIP 업로드 등록** 탭
2. zip 파일 선택 (또는 제공된 템플릿 zip 다운로드 후 업로드)
3. 자동 처리:
   - `-sql.sql` 실행 → DB 테이블 생성
   - `-app.py` 동적 로드 → API 즉시 활성화
   - `-front.tsx` → `front/src/pages/addon/deployed/{key}.tsx` 복사
   - `tbl_addon_agents` + `tbl_agent_config` 등록
4. **프론트엔드 재빌드** → 사이드바 메뉴 자동 표시:
   ```bash
   cd front && npm run build
   pm2 restart wise-fe
   ```

---

## 핫 디플로이 메커니즘

```
zip 업로드
    │
    ▼
addon-agents/deployed/{agent_key}/ 에 파일 저장
    │
    ├─ {Name}-sql.sql 실행 → DB 테이블 생성
    │
    ├─ {Name}-app.py  importlib 동적 로드
    │   → module.router 추출
    │   → app.include_router(router, prefix="/api/addon/{agent_key}")
    │
    ├─ {Name}-front.tsx → front/src/pages/addon/deployed/{key}.tsx 복사
    │   → 프론트엔드 재빌드 후 /addon/{key} 라우트 자동 활성화
    │
    └─ tbl_addon_agents + tbl_agent_config INSERT

앱 재시작 시: addon_agent_loader._load_all_from_disk()
→ DB 활성 Addon 조회 → 모든 라우터 자동 재등록
```

---

## API 엔드포인트

| Method | 경로 | 설명 | 권한 |
|--------|------|------|------|
| `GET` | `/api/addon-agents/` | 등록된 Addon 목록 | 로그인 |
| `POST` | `/api/addon-agents/upload` | zip 업로드 + 핫 디플로이 | supervisor/admin |
| `POST` | `/api/addon-agents/scaffold` | 스캐폴딩 Wizard → zip 생성 (또는 바로 배포) | supervisor/admin |
| `PATCH` | `/api/addon-agents/{key}/toggle` | 활성/비활성 토글 | supervisor/admin |
| `DELETE` | `/api/addon-agents/{key}` | Agent 삭제 | supervisor/admin |
| `GET` | `/api/addon-agents/templates/list` | 템플릿 목록 | 로그인 |
| `GET` | `/api/addon-agents/templates/download/{file}` | 템플릿 zip 다운로드 | 로그인 |

---

## 제약 및 주의사항

| 항목 | 내용 |
|------|------|
| 보안 | 업로드된 Python 파일은 서버에서 실행됨 — supervisor/admin 권한 보호 필수 |
| 라우터 제거 | Agent 삭제 후 라우터 완전 제거는 **앱 재시작** 필요 |
| 프론트 반영 | `-front.tsx` 포함 시 `npm run build` + 서버 재시작 필요 |
| 파일 크기 | zip 최대 10MB |
| 내장 에이전트 | `deployed/board/` 은 직접 수정 가능 (git 추적됨) |

---

## 내장 에이전트

| Agent | 설명 | 경로 |
|-------|------|------|

---

## 템플릿 목록

| 템플릿 | agent_type | 설명 | 파일 |
|--------|------------|------|------|
| **RagAgent** | `rag` | 문서 임베딩·청킹·벡터 검색 + SSE 스트리밍 Q&A. 임베딩 함수 교체 포인트 포함 | `RagAgent.zip` |
| **ServiceAgent** | `service` | 백엔드 비즈니스 로직 뼈대. `process` capability, async/streaming 지원 | `ServiceAgent.zip` |
| **ToolProxyAgent** | `tool-proxy` | 외부 REST API를 MCP Tool로 노출하는 어댑터. `TOOL_PROXY_BASE_URL` 필수 | `ToolProxyAgent.zip` |

### RagAgent 주요 엔드포인트

| Method | 경로 | 설명 |
|--------|------|------|
| `POST` | `/api/addon/ragagent/ingest` | 문서 업로드 + 청킹 + 임베딩 저장 |
| `GET` | `/api/addon/ragagent/documents` | 업로드된 문서 목록 |
| `DELETE` | `/api/addon/ragagent/documents/{id}` | 문서 + 청크 삭제 (supervisor/admin) |
| `POST` | `/api/addon/ragagent/search` | 코사인 유사도 벡터 검색 |
| `POST` | `/api/addon/ragagent/qa` | RAG 기반 Q&A — SSE 스트리밍 응답 |

> `_embed()` 함수는 프로토타입 구현(해시 기반)입니다. 실제 서비스에서는 Ollama `nomic-embed-text` 또는 OpenAI `text-embedding-3-small`로 교체하세요.

---

_CoreSight-G Platform · Addon Agent Extension System_
