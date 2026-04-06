# ⚠️ Phase 2 피드백 반영: 동적 호출 및 상태 관리 개선

**수정 사항**: 사용자 피드백에 따라 다음을 개선해야 합니다:

## 현재 문제점

1. **캐싱 문제**: 동일 이름 에이전트 재사용
   - 현재: `spawn()` → 기존 에이전트 반환 (1회 생성)
   - 필요: 매번 새로운 인스턴스 생성 (Codex/Claude Code 스타일)

2. **상태 관리 부족**: 생성/작업/소멸 추적 없음
   - 필요: CREATED → RUNNING → COMPLETED → DESTROYED 상태 전환

## 해결 방안

### 1. 상태 관리 추가 (SubAgentLifecycleState, SpawnedSubAgent)

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

### 2. Registry 수정 (spawn_ephemeral)

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

### 3. task 도구 수정

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

## 구현 체크리스트

- [ ] SubAgentLifecycleState Enum 추가
- [ ] SpawnedSubAgent 클래스 추가
- [ ] DynamicSubAgentRegistry.spawn_ephemeral() 메서드 추가
- [ ] DynamicSubAgentRegistry.destroy() 메서드 추가
- [ ] task/atask 함수에서 상태 관리 통합
- [ ] 테스트 케이스 업데이트 (상태 전환 검증)
- [ ] SUBAGENT_DYNAMIC_GUIDE.md 업데이트

## 예상 효과

✅ **매번 동적 호출**: 동일 이름이어도 새 인스턴스 생성
✅ **상태 추적**: 생성/실행/완료/소멸 명확히 추적
✅ **자동 정리**: 작업 후 즉시 메모리 해제
✅ **Codex/Claude Code 호환**: 정확한 에페메럴 에이전트 구현

---

**작업 상태**: 📝 구현 대기 중
**예상 완료**: 다음 커밋에서 구현
