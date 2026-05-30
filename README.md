# 📊 학생 데이터 기반 수업설계 분석 앱
### HEAL 프로젝트 교육과정·평가 설계 지원 도구

---

## 🚀 실행 방법

### 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud 배포
1. GitHub 저장소에 이 폴더 전체 업로드
2. [streamlit.io/cloud](https://streamlit.io/cloud) 접속 → New app
3. 저장소 선택 → `app.py` 선택 → Deploy
4. App settings → Secrets에 아래 추가:
```
GEMINI_API_KEY = "AIza..."
```

---

## 🖼 이미지 자동 파싱 기능

검사 결과지를 캡처한 이미지(PNG/JPG)를 업로드하면
Claude Vision API가 자동으로 데이터를 읽어 입력란을 채워줍니다.

| 검사 | 추출 항목 |
|------|-----------|
| 학습유형검사 (VARK) | 주요 유형 + 영역별 점수 |
| 진로탐색검사 (Holland) | 주요 유형 + RIASEC 점수 |
| 사회정서역량검사 (SEL) | 5개 영역 수준 (높음/보통/지원필요) |
| 기초학력진단검사 | 교과·내용영역별 정답률(%) |

**사용 흐름:**
1. 학생 번호 입력
2. 검사별 결과지 이미지 업로드 (1~4장)
3. "자동 파싱" 버튼 클릭
4. 파싱 결과 확인 후 필요 시 수정
5. "학생 데이터 저장" 클릭

---

## 📋 앱 구성 (7개 메뉴)

| 메뉴 | 기능 |
|------|------|
| 📥 데이터 입력 | 이미지 업로드 자동 파싱 + 수동 입력 |
| 📝 관찰지 입력 | 교사관찰지 + 학생자기관찰지 (각 10문항) |
| 👤 학생 프로파일 | 6가지 데이터 통합 종합 분석 카드 |
| 👥 학급 전체 분석 | 학급 분포·취약영역 시각화 |
| 🧩 모둠 구성 추천 | VARK·Holland 기반 상보적 모둠 배치 |
| 📐 수업 설계 제안 | 핵심질문 개인화·루브릭 원칙 |
| 📋 AI 프롬프트 생성 | 관찰지 포함 Claude 프롬프트 자동 생성 |

---

## 📚 이론 근거

- **VARK** (Fleming & Mills, 1992)
- **Holland RIASEC** (Holland, 1997)
- **CASEL SEL Framework** (2020)
- **OECD Digital Education Outlook 2026**
- **UNESCO AI in Education** (2023)
- **Tomlinson** (2014) — 차별화 수업(DI)
- **Wiggins & McTighe** (2005) — 백워드 설계

---

## ⚠ 개인정보 원칙

- 학생 이름 없이 **번호만** 사용
- AI 프롬프트에 개인 식별 정보 미포함
- 이미지에 이름이 포함된 경우 **마스킹 후 업로드** 권장
- UNESCO·GDPR 데이터 최소화 원칙 준수
