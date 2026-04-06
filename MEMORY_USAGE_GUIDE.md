# Deep Agents CLI - 메모리 기능 사용 가이드

**작성일**: 2026-04-06
**상태**: ✅ 실제 운영 가능

---

## 📌 메모리 기능이란?

Deep Agents CLI는 **개발자 개인 지식 베이스(Personal Knowledge Base)** 시스템을 제공합니다. 개발 중에 배운 내용, 패턴, 팁 등을 자동으로 저장하고 나중에 검색할 수 있습니다.

---

## 🚀 빠른 시작

### 1단계: CLI 실행
```bash
cd /home/ubuntu/deepagents/libs/cli
uv run deepagents
```

### 2단계: 프로필 확인
```
/memory profile
```
**출력 예**:
```
Developer Profile:
  Name: Developer
  Role: Software Developer
  Experience: mid
  Languages: python, javascript
  Frameworks: fastapi, react
  Updated: 2026-04-06
```

### 3단계: 학습 추가
```
/memory add "Python에서는 항상 type hints를 사용하기"
```
**출력 예**:
```
✓ Learning added (ID: 019d61c0-bf86-7ac1-80d5)
```

### 4단계: 학습 검색
```
/memory search "python"
```
**출력 예**:
```
Found 1 learning(s):

[1] Python 관련 학습
  Content: Python에서는 항상 type hints를 사용하기
  Category: best_practice
  Source: user_feedback
  Date: 2026-04-06 14:30
```

---

## 📚 전체 명령어 (5가지)

### 1️⃣ `/memory profile` - 프로필 조회

**설명**: 현재 개발자 프로필을 확인합니다.

**사용법**:
```
/memory profile
```

**출력**:
- 이름 (Name)
- 역할 (Role): Backend Engineer, Frontend Developer 등
- 경험 수준 (Experience): junior / mid / senior / lead
- 주 프로그래밍 언어 (Languages)
- 선호 프레임워크 (Frameworks)
- 마지막 업데이트 시간

**예시**:
```
/memory profile
```

---

### 2️⃣ `/memory add "내용"` - 학습 추가

**설명**: 새로운 학습, 팁, 패턴, 발견사항을 메모리에 저장합니다.

**사용법**:
```
/memory add "학습 내용"
```

**예시들**:
```bash
# 베스트 프랙티스
/memory add "Python List Comprehension은 loop보다 빠르다"

# 발견사항
/memory add "FastAPI는 비동기 지원으로 높은 성능 제공"

# 문제 해결
/memory add "N+1 쿼리 문제는 eager loading으로 해결"

# 패턴
/memory add "Repository 패턴으로 데이터 접근 추상화"

# 선호도
/memory add "VSCode의 Pylance는 Python 타입 체크에 최고"

# 고급 팁
/memory add "async/await는 I/O 바운드 작업에 유용"
```

**데이터 구조**:
- Content: 저장되는 내용
- Source: `user_feedback` (사용자가 직접 추가)
- Category: `best_practice` (기본값)
- Tags: 자동 생성 (쿼리 단어)
- Timestamp: 자동 기록

---

### 3️⃣ `/memory search "쿼리"` - 학습 검색

**설명**: 저장된 학습 중에서 키워드로 검색합니다.

**사용법**:
```
/memory search "검색어"
```

**예시들**:
```bash
# 언어별 검색
/memory search "python"
/memory search "javascript"
/memory search "go"

# 패턴 검색
/memory search "repository"
/memory search "async"
/memory search "performance"

# 프레임워크 검색
/memory search "fastapi"
/memory search "react"
/memory search "django"

# 개념 검색
/memory search "type hints"
/memory search "optimization"
/memory search "best practice"
```

**출력 형식**:
```
Found N learning(s):

[1] 제목 1
  Content: 학습 내용
  Category: best_practice
  Source: user_feedback
  Date: 2026-04-06

[2] 제목 2
  ...
```

**검색 팁**:
- 대소문자 구분 없음
- 부분 매칭 (예: "async"는 "asynchronous" 포함)
- 태그로도 검색 가능

---

### 4️⃣ `/memory stats` - 통계 조회

**설명**: 현재 메모리 상태의 통계를 확인합니다.

**사용법**:
```
/memory stats
```

**출력 예**:
```
Memory Statistics:
  Total Learnings: 15
  Total Entities: 8
  Total Relationships: 12
  Database Size: 0.25 MB
  Location: /home/user/.deepagents/memory

  By Category:
    best_practice: 8
    knowledge: 5
    anti_pattern: 2

  By Source:
    user_feedback: 12
    conversation: 3
```

---

### 5️⃣ `/memory export` - 메모리 내보내기

**설명**: 모든 메모리를 JSON 파일로 내보냅니다. 백업이나 공유 목적으로 사용합니다.

**사용법**:
```
/memory export
```

**출력**:
```
✓ Memory exported to: ~/.deepagents/memory_export_20260406_140530.json
```

**파일 구조**:
```json
{
  "profile": {
    "name": "Developer",
    "role": "Software Developer",
    "experience_level": "mid",
    "primary_languages": ["python"],
    "preferred_frameworks": ["fastapi"],
    "updated_at": "2026-04-06"
  },
  "learnings": [
    {
      "id": "019d61c0-bf86-7ac1-80d5",
      "content": "Python에서는 항상 type hints를 사용하기",
      "source": "user_feedback",
      "category": "best_practice",
      "tags": ["python", "typing"],
      "created_at": "2026-04-06",
      "confidence": 1.0
    }
  ],
  "entities": [...],
  "relationships": [...]
}
```

---

## 💾 저장 위치

모든 메모리 데이터는 다음 위치에 자동으로 저장됩니다:

```
~/.deepagents/memory/
├── memory.db                    # SQLite 데이터베이스 (영구 저장소)
├── developer_profile.json       # 개발자 프로필
└── memory_export_*.json         # 내보낸 백업 파일들
```

**파일 설명**:
- **memory.db**: SQLite 데이터베이스
  - learnings 테이블: 저장된 모든 학습
  - entities 테이블: 프로젝트, 라이브러리, 패턴 등
  - relationships 테이블: 그들 간의 관계

- **developer_profile.json**: JSON 형식의 프로필
  - 수동으로 편집 가능
  - 이름, 역할, 언어, 프레임워크 등

---

## 🎯 실제 사용 시나리오

### 시나리오 1: 새로운 개발자의 첫날

```bash
# 1. CLI 실행
deepagents

# 2. 프로필 확인 (기본값)
/memory profile

# 3. 첫 번째 학습 추가
/memory add "FastAPI 프로젝트 시작"
/memory add "async/await 기본 개념 학습"
/memory add "SQLAlchemy ORM 사용법"
/memory add "Pydantic으로 데이터 검증하기"

# 4. 학습 검색
/memory search "fastapi"
/memory search "async"

# 5. 통계 확인
/memory stats
```

**메모리 상태**:
- Learnings: 4개
- Categories: best_practice (3), knowledge (1)
- Ready for future reference

---

### 시나리오 2: 프로젝트 진행 중 얻은 교훈

**상황**: REST API 개발 중 성능 문제 발견

```bash
# 1. 문제 해결 방법 저장
/memory add "N+1 쿼리 문제: eager loading으로 해결 (SQLAlchemy)"
/memory add "쿼리 최적화: 불필요한 column select 제거"
/memory add "캐싱 전략: Redis로 자주 조회되는 데이터 캐싱"

# 2. 성능 개선 결과 저장
/memory add "응답 시간 1000ms -> 50ms로 개선됨 (캐싱)"

# 3. 나중에 참고
/memory search "performance"
/memory search "optimization"
/memory search "caching"
```

---

### 시나리오 3: 팀에 공유 또는 백업

```bash
# 1. 메모리 내보내기
/memory export

# 2. 생성된 파일 확인
ls ~/.deepagents/memory_export_*.json

# 3. 팀과 공유 또는 다른 컴퓨터에서 사용
# (향후 import 기능 추가 예정)
```

---

## 📋 학습 입력 베스트 프랙티스

### ✅ Good 예시

```bash
# 명확하고 구체적
/memory add "Python의 f-string은 .format()보다 빠르고 가독성 좋음"

# 문제와 해결책
/memory add "TypeScript type inference 문제: 제네릭에 명시적 타입 지정"

# 측정 가능한 결과
/memory add "캐싱 적용으로 API 응답 시간 500ms 단축"

# 실전 코드 패턴
/memory add "데이터 검증: Pydantic BaseModel 상속 + validator 데코레이터"
```

### ❌ Bad 예시

```bash
# 너무 일반적
/memory add "Python은 좋은 언어다"

# 너무 모호함
/memory add "뭔가 되네"

# 정보 부족
/memory add "fastapi"  # 단어만 있음
```

---

## 🔍 검색 팁

### 카테고리별 검색
```bash
# 베스트 프랙티스만 검색
/memory search "python" type:best_practice

# 안티 패턴 검색
/memory search "global" type:anti_pattern
```

### 최신 학습 조회
```bash
# 가장 최근에 저장된 5개
/memory search "" limit:5
```

### 관련 항목 한꺼번에 보기
```bash
/memory search "async python"  # 여러 키워드 조합
```

---

## 📈 메모리 성장 추적

시간이 지남에 따라 메모리가 어떻게 성장하는지 추적:

```bash
# Week 1
/memory stats
# → Learnings: 5개

# Week 2
/memory stats
# → Learnings: 15개 (새로운 프로젝트)

# Month 1
/memory stats
# → Learnings: 50개 (다양한 경험)
```

---

## 🛠️ 문제 해결

### Q1: 메모리 파일이 생성되지 않음
**A**: 디렉토리 권한 확인
```bash
mkdir -p ~/.deepagents/memory
chmod 755 ~/.deepagents/memory
```

### Q2: 검색 결과가 없음
**A**: 다른 검색어 시도
```bash
/memory search "python"    # 실패
/memory search "type"      # 시도
/memory search "hints"     # 구체적 검색
```

### Q3: 프로필 초기화하고 싶음
**A**: 프로필 파일 삭제
```bash
rm ~/.deepagents/memory/developer_profile.json
# 다음 /memory profile 실행 시 새로 생성됨
```

### Q4: 메모리 완전 초기화
**A**: 데이터베이스 삭제
```bash
rm -rf ~/.deepagents/memory/
# 다음 /memory 명령 실행 시 새로 생성됨
```

---

## 🚀 향후 기능 (계획 중)

- [ ] 자동 학습 기록: 에이전트가 사용자 피드백 감지 시 자동 저장
- [ ] 학습 동기화: 여러 장치 간 메모리 클라우드 동기화
- [ ] 우선순위 기반 추천: 자주 조회되는 학습 먼저 표시
- [ ] 지식 그래프 시각화: 개념들 간의 관계를 대시보드에 표시
- [ ] LLM 기반 메모리 요약: 유사한 학습들을 자동으로 통합
- [ ] CSV/PDF 내보내기: 다양한 형식 지원

---

## 📞 지원

문제 발생 시:
1. `~/.deepagents/memory/` 디렉토리 확인
2. `/memory stats` 로 메모리 상태 확인
3. `/memory export` 로 백업 생성
4. 로그 파일 확인 (향후 추가)

---

## 요약

| 명령어 | 목적 | 예시 |
|--------|------|------|
| `/memory profile` | 프로필 조회 | 현재 정보 확인 |
| `/memory add` | 학습 추가 | `/memory add "Python 팁"` |
| `/memory search` | 학습 검색 | `/memory search "python"` |
| `/memory stats` | 통계 조회 | 저장된 학습 수 확인 |
| `/memory export` | 백업 내보내기 | JSON 파일로 저장 |

---

**마지막 업데이트**: 2026-04-06
**상태**: ✅ 프로덕션 운영 가능
