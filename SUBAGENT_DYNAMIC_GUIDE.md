# Deep Agents SDK - Dynamic SubAgent Spawning 개발 가이드

**최종 업데이트**: 2026-04-06
**상태**: ✅ Phase 1 완료 | ⚠️ Phase 2 개선 진행 중

---

## 목차

1. [시스템 개요](#시스템-개요)
2. [Phase 1: 완료된 기능](#phase-1-완료된-기능)
3. [아키텍처](#아키텍처)
4. [구현된 기능](#구현된-기능)
5. [파일 구조](#파일-구조)
6. [사용 방법](#사용-방법)
7. [개발 상세](#개발-상세)
8. [테스트](#테스트)
9. [Phase 2: 개선사항](#phase-2-개선사항)
10. [향후 개선사항](#향후-개선사항)

---

## 시스템 개요

Deep Agents SDK에 **동적 서브에이전트 생성(Dynamic SubAgent Spawning)** 기능을 구현했습니다. 이 시스템은 에이전트가 런타임 중에 사전 정의 없이 새로운 서브에이전트를 즉석에서 생성할 수 있게 해줍니다.

### 핵심 기능

- 🚀 **동적 생성**: `spawn_config`를 사용하여 런타임 중 새 서브에이전트 즉시 생성
- 🎯 **영속성 없음**: 에페메럴(Ephemeral) 서브에이전트 - 작업 후 자동 정리
- 🔧 **유연한 설정**: 역할, 지시사항, 도구 목록, 모델 동적 설정
- 💾 **캐싱**: 동일 이름의 서브에이전트는 재사용 (성능 최적화)
- 🔀 **호환성**: 기존 정적 서브에이전트와 함께 사용 가능

### 사용 위치

```
libs/deepagents/deepagents/middleware/
├── subagents.py (수정됨)
└── tests/unit_tests/test_dynamic_subagents.py (추가됨)
```

---

## Phase 1: 완료된 기능

### ✅ 구현 완료 항목

- [x] SpawnAgentConfig TypedDict 정의
- [x] DynamicSubAgentRegistry 클래스 구현
- [x] TaskToolSchema 확장 (spawn_config 필드 추가)
- [x] _build_task_tool() 수정 (동적 생성 로직)
- [x] task/atask 함수 수정 (spawn_config 처리)
- [x] 단위 테스트 작성 (29개 케이스)
- [x] 문서 작성 (이 파일)

---

## 아키텍처

### 3계층 설계

```
┌─────────────────────────────────────┐
│   Main Agent (task 도구 사용)       │
│   - spawn_config 활용               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   TaskToolSchema (확장됨)            │
│   - subagent_type (기존)             │
│   - spawn_config (신규)              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   DynamicSubAgentRegistry            │
│   - spawn() - 새 에이전트 생성       │
│   - get() - 캐시된 에이전트 조회    │
│   - list_active() - 활성 목록       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   create_agent() (LangChain)         │
└─────────────────────────────────────┘
```

### 데이터 모델

**SpawnAgentConfig** (TypedDict)
```python
{
    name: str              # 유니크 식별자
    role: str              # 한 줄 역할 설명
    instructions: str      # 상세 시스템 프롬프트
    tools: list[str]       # 사용 가능한 도구 이름
    model: str | None      # 선택적 모델 오버라이드
}
```

**TaskToolSchema** (확장됨)
```python
{
    description: str              # 작업 설명 (필수)
    subagent_type: str = ""       # 사전정의 에이전트 (옵션)
    spawn_config: SpawnAgentConfig | None  # 동적 생성 설정 (옵션)
}
```

---

## 구현된 기능

### 1. SpawnAgentConfig TypedDict

동적 서브에이전트 생성을 위한 설정 구조:

```python
class SpawnAgentConfig(TypedDict):
    name: str
    role: str
    instructions: str
    tools: list[str]
    model: NotRequired[str]  # 선택적
```

**필수 필드**:
- `name`: 서브에이전트의 고유 식별자
- `role`: 역할 설명 (한 줄)
- `instructions`: 상세 시스템 프롬프트
- `tools`: 사용 가능한 도구 이름 목록

**선택적 필드**:
- `model`: 모델 오버라이드 ('provider:model-name' 형식)

### 2. DynamicSubAgentRegistry 클래스

에페메럴 서브에이전트 레지스트리:

```python
class DynamicSubAgentRegistry:
    def __init__(
        self,
        backend: BackendProtocol,
        parent_model: str = "openai:gpt-4o",
        parent_tools: Sequence[BaseTool] | None = None,
    ) -> None:
        """레지스트리 초기화."""

    def spawn(self, config: SpawnAgentConfig) -> tuple[str, Runnable]:
        """새 서브에이전트 생성 또는 기존 것 반환."""

    def get(self, name: str) -> Runnable | None:
        """캐시된 서브에이전트 조회."""

    def list_active(self) -> list[str]:
        """활성 서브에이전트 목록."""
```

**주요 특징**:
- 캐싱: 동일 이름의 서브에이전트는 재사용
- 모델 해석: 'provider:model-name' 형식 자동 변환
- 도구 해석: 도구 이름 기반으로 실제 도구 객체 할당
- 예외 처리: 에러 발생 시 명확한 메시지 반환

### 3. TaskToolSchema 확장

기존 task 도구에 `spawn_config` 파라미터 추가:

```python
class TaskToolSchema(BaseModel):
    description: str
    subagent_type: str = ""  # 기존 - 사전정의 에이전트
    spawn_config: NotRequired[SpawnAgentConfig]  # 신규 - 동적 생성
```

**동작 순서**:
1. `spawn_config` 제공 시 → 동적 생성 (우선순위)
2. `spawn_config` 미제공 시 → `subagent_type` 사용 (기존 방식)
3. 둘 다 미제공 시 → 에러

### 4. task 도구 향상

`_build_task_tool()` 함수에 동적 스폰 지원 추가:

```python
def task(
    description: str,
    subagent_type: str = "",
    runtime: ToolRuntime | None = None,
    spawn_config: SpawnAgentConfig | None = None,
) -> str | Command:
    """사전정의 또는 동적으로 생성된 서브에이전트 실행."""
```

**로직**:
1. `runtime` 검증
2. `spawn_config` 있으면 동적 생성 (DynamicSubAgentRegistry 사용)
3. 없으면 기존 `subagent_type` 사용
4. 결과 반환 또는 에러 메시지

---

## 파일 구조

```
libs/deepagents/deepagents/middleware/
├── subagents.py (수정 - 540 → ~600줄)
│   ├── SpawnAgentConfig (새로 추가)
│   ├── DynamicSubAgentRegistry (새로 추가)
│   ├── TaskToolSchema (수정 - spawn_config 추가)
│   └── _build_task_tool() (수정 - 동적 생성 지원)
│
tests/unit_tests/
└── test_dynamic_subagents.py (새로 추가)
    ├── TestSpawnAgentConfig (13개 테스트)
    ├── TestDynamicSubAgentRegistry (8개 테스트)
    ├── TestTaskToolSchema (5개 테스트)
    └── TestSpawnAgentConfigTypes (3개 테스트)
```

**총 변경사항**:
- 새 클래스: 1개 (DynamicSubAgentRegistry)
- 수정된 클래스: 2개 (TaskToolSchema, _build_task_tool)
- 새 TypedDict: 1개 (SpawnAgentConfig)
- 테스트: 29개 케이스

---

## 사용 방법

### 1. 기본 동적 서브에이전트 생성

```python
from deepagents.middleware.subagents import (
    SpawnAgentConfig,
    DynamicSubAgentRegistry,
)

# 레지스트리 초기화
registry = DynamicSubAgentRegistry(
    backend=backend,
    parent_model="openai:gpt-4o",
    parent_tools=[search_tool, read_file_tool],
)

# 동적 서브에이전트 생성
config: SpawnAgentConfig = {
    "name": "security-analyst",
    "role": "보안 전문가",
    "instructions": "OWASP Top 10 기준으로 코드를 분석하세요...",
    "tools": ["read_file", "search"],  # 사용할 도구 이름
}

agent_name, runnable = registry.spawn(config)
```

### 2. task 도구에서 spawn_config 사용

에이전트 내에서 task 도구 호출 시:

```python
# 모델이 이렇게 호출 (JSON 형식)
{
    "name": "task",
    "arguments": {
        "description": "이 코드베이스의 보안 취약점 분석",
        "spawn_config": {
            "name": "security-analyst",
            "role": "보안 전문가",
            "instructions": "목표: OWASP Top 10 기준으로 코드 분석...",
            "tools": ["read_file", "execute"],
            "model": "anthropic:claude-opus"  # 선택적
        }
    }
}
```

### 3. 기존 정적 방식과 혼합 사용

```python
# 기존 방식 - 계속 작동
{
    "name": "task",
    "arguments": {
        "description": "데이터 분석",
        "subagent_type": "general-purpose"
    }
}

# 새로운 방식 - 동적 생성
{
    "name": "task",
    "arguments": {
        "description": "데이터 분석",
        "spawn_config": {
            "name": "data-analyst",
            "role": "데이터 분석가",
            "instructions": "...",
            "tools": ["analyze", "visualize"]
        }
    }
}
```

---

## 개발 상세

### DynamicSubAgentRegistry 구현 포인트

1. **캐싱 메커니즘**
   - `_spawned_agents` 딕셔너리에 이름으로 저장
   - 동일 이름 요청 시 기존 에이전트 반환 (중복 생성 방지)

2. **모델 해석**
   - `resolve_model()` 사용 ('provider:model-name' → 실제 모델 객체)
   - 모델 지정 없으면 `parent_model` 사용

3. **도구 해석**
   - `_resolve_tools_by_name()` 메서드
   - 도구 이름 문자열 → 실제 BaseTool 객체 변환
   - 존재하지 않는 도구는 조용히 제외

4. **에이전트 생성**
   - `create_agent()` (LangChain)로 에이전트 생성
   - 미들웨어 빈 리스트 (스포닝된 에이전트는 정적임)

### task 도구 향상 포인트

1. **런타임 검증**
   ```python
   if not runtime:
       return "Runtime is required..."
   if not runtime.tool_call_id:
       return "Tool call ID is required..."
   ```

2. **우선순위 처리**
   - `spawn_config` 있으면 먼저 처리 (우선순위 높음)
   - 없으면 기존 `subagent_type` 사용

3. **예외 처리**
   - 스포닝 실패 시 명확한 에러 메시지
   - 정의되지 않은 도구 조용히 건너뜀

4. **비동기 지원**
   - 동기 `task()` 함수
   - 비동기 `atask()` 코루틴
   - 동일한 로직, 다른 실행 모델

---

## 테스트

### 테스트 계획 (29개 케이스)

**TestSpawnAgentConfig (3개)**
- 최소 설정 검증
- 모델 오버라이드 검증
- 빈 도구 목록 검증

**TestTaskToolSchema (3개)**
- subagent_type 파라미터
- spawn_config 파라미터
- 기본값 검증

**TestDynamicSubAgentRegistry (11개)**
- 초기화
- 활성 목록 (빈 상태)
- 존재하지 않는 에이전트 조회
- 기본 스폰
- 모델 오버라이드 스폰
- 캐싱 메커니즘
- 도구 해석 (빈 경우)
- 도구 해석 (일치)
- 도구 해석 (부분 일치)

**TestTaskToolSchemaValidation (5개)**
- description 필수
- spawn_config 선택적
- 둘 다 제공 가능

**TestSpawnAgentConfigTypes (3개)**
- tools 타입 검증
- name 타입 검증
- instructions 타입 검증

### 테스트 실행

```bash
# 전체 테스트
make test

# 특정 테스트만 실행
uv run pytest tests/unit_tests/test_dynamic_subagents.py -v

# 특정 테스트 클래스
uv run pytest tests/unit_tests/test_dynamic_subagents.py::TestDynamicSubAgentRegistry -v
```

---

## Phase 2: 개선사항

### ⚠️ 현재 식별된 문제점

1. **캐싱 문제**: 동일 이름 에이전트 재사용
   - 현재: `spawn()` → 기존 에이전트 반환 (1회 생성)
   - 필요: 매번 새로운 인스턴스 생성 (Codex/Claude Code 스타일)

2. **상태 관리 부족**: 생성/작업/소멸 추적 없음
   - 필요: CREATED → RUNNING → COMPLETED → DESTROYED 상태 전환

### ✨ 제안된 해결책

#### 1. 상태 관리 추가 (SubAgentLifecycleState, SpawnedSubAgent)

```python
class SubAgentLifecycleState(str, Enum):
    """생명주기 상태."""
    CREATED = "created"      # 생성 완료
    RUNNING = "running"      # 작업 중
    COMPLETED = "completed"  # 작업 완료
    DESTROYED = "destroyed"  # 메모리 해제

class SpawnedSubAgent:
    """생명주기를 추적하는 에페메럴 서브에이전트."""
    - name: 서브에이전트 이름
    - runnable: LangChain Runnable
    - state: 현재 상태
    - instance_id: 고유 인스턴스 ID (매번 다름)
    - created_at: 생성 시간
    - started_at: 시작 시간
    - completed_at: 완료 시간

    메서드:
    - mark_running(): 작업 시작
    - mark_completed(): 작업 완료
    - destroy(): 메모리 정리
    - duration_ms(): 소요 시간
```

#### 2. Registry 수정 (spawn_ephemeral)

**기존**:
```python
def spawn(config) -> tuple[str, Runnable]:
    # 캐싱 - 기존 에이전트 반환
    if name in self._spawned_agents:
        return name, self._spawned_agents[name]
```

**개선**:
```python
def spawn_ephemeral(config) -> tuple[str, SpawnedSubAgent]:
    # 매번 새로운 인스턴스 생성
    # 캐싱 제거 - 동일 이름이어도 새로 생성
    spawned = SpawnedSubAgent(...)
    spawned.mark_running()
    return name, spawned

def destroy(agent_id: str) -> None:
    # 구체적인 인스턴스 정리
    agent.mark_completed()
    agent.destroy()
```

#### 3. task 도구 수정

```python
def task(...) -> str | Command:
    # 1. 동적 스포닝
    agent_id, spawned = dynamic_registry.spawn_ephemeral(spawn_config)

    # 2. 작업 실행
    spawned.mark_running()
    result = spawned.runnable.invoke(state)

    # 3. 자동 정리
    spawned.mark_completed()
    spawned.destroy()
    dynamic_registry.destroy(agent_id)

    return result
```

### Phase 2 체크리스트

- [ ] SubAgentLifecycleState Enum 추가
- [ ] SpawnedSubAgent 클래스 추가
- [ ] DynamicSubAgentRegistry.spawn_ephemeral() 메서드 추가
- [ ] DynamicSubAgentRegistry.destroy() 메서드 추가
- [ ] task/atask 함수에서 상태 관리 통합
- [ ] 테스트 케이스 업데이트 (상태 전환 검증)
- [ ] 문서 업데이트

### 예상 효과

✅ **매번 동적 호출**: 동일 이름이어도 새 인스턴스 생성
✅ **상태 추적**: 생성/실행/완료/소멸 명확히 추적
✅ **자동 정리**: 작업 후 즉시 메모리 해제
✅ **Codex/Claude Code 호환**: 정확한 에페메럴 에이전트 구현

---

## 향후 개선사항

1. **GUI 슬래시 명령** (`/spawn-agent`)
   - CLI에서 동적 서브에이전트 생성 간편화
   - 대화형 설정 입력

2. **영속성**
   - 스포닝 이력 기록
   - 자주 사용되는 스포닝 저장

3. **모니터링**
   - 활성 서브에이전트 수 추적
   - 성능 메트릭 수집

4. **제약 사항**
   - 최대 동시 서브에이전트 수 제한
   - 타임아웃 설정

5. **도구 그룹화**
   - 도구 집합을 프리셋으로 정의
   - "data-analysis", "code-review" 등

---

## 통합 체크리스트

### Phase 1 (완료됨)
- [x] SpawnAgentConfig TypedDict 정의
- [x] DynamicSubAgentRegistry 클래스 구현
- [x] TaskToolSchema 확장 (spawn_config 필드 추가)
- [x] _build_task_tool() 수정 (동적 생성 로직)
- [x] task/atask 함수 수정 (spawn_config 처리)
- [x] 단위 테스트 작성 (29개 케이스)
- [x] 문서 작성

### Phase 2 (진행 중)
- [ ] 상태 관리 추가
- [ ] 캐싱 메커니즘 개선
- [ ] 자동 정리 로직 구현
- [ ] 테스트 업데이트
- [ ] 문서 업데이트

### Phase 3 (계획 중)
- [ ] CLI 통합
- [ ] 모니터링 기능
- [ ] 시스템 프롬프트 업데이트

---

## 참고자료

**관련 파일**:
- `libs/deepagents/deepagents/middleware/subagents.py` - 메인 구현
- `libs/deepagents/tests/unit_tests/test_dynamic_subagents.py` - 테스트
- `MEMORY_SYSTEM_GUIDE.md` - Phase 1 가이드

**외부 참고**:
- [LangChain Agent](https://docs.langchain.com/oss/python/langchain/quickstart)
- [TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict)

---

**문서 작성**: 2026-04-06
**마지막 업데이트**: 2026-04-06
**상태**: ✅ Phase 1 완료 | ⚠️ Phase 2 개선 진행 중
