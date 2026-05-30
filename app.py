import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import random
import json
from itertools import combinations

# ───────────────────────────────────────────────
# 페이지 설정
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="학생 데이터 기반 수업설계 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ───────────────────────────────────────────────
# 스타일
# ───────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #F8F6F2; }
  [data-testid="stSidebar"] { background: #1565C0; }
  [data-testid="stSidebar"] * { color: #fff !important; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stRadio label { color: #fff !important; }
  [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2); }
  .metric-card {
    background: white; border-radius: 12px; padding: 1.2rem 1.4rem;
    border: 1px solid #E0E8F4; margin-bottom: 0.5rem;
  }
  .profile-header {
    background: linear-gradient(135deg, #1565C0 0%, #1976D2 100%);
    border-radius: 14px; padding: 1.6rem 2rem; color: white; margin-bottom: 1rem;
  }
  .section-title {
    font-size: 1rem; font-weight: 600; color: #1565C0;
    border-left: 4px solid #1565C0; padding-left: 0.7rem;
    margin: 1.2rem 0 0.8rem;
  }
  .tag {
    display: inline-block; padding: 3px 12px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600; margin: 2px;
  }
  .tag-blue  { background: #E3F0FF; color: #1565C0; }
  .tag-green { background: #E8F5E9; color: #2E7D32; }
  .tag-red   { background: #FFF3F3; color: #C62828; }
  .tag-orange{ background: #FFF8E1; color: #E65100; }
  .tag-gray  { background: #F5F5F5; color: #555; }
  .warn-box {
    background: #FFF8F8; border-left: 4px solid #E57373;
    border-radius: 8px; padding: 0.8rem 1rem; margin: 0.5rem 0;
    font-size: 0.88rem; color: #555;
  }
  .success-box {
    background: #F1F8E9; border-left: 4px solid #66BB6A;
    border-radius: 8px; padding: 0.8rem 1rem; margin: 0.5rem 0;
    font-size: 0.88rem; color: #333;
  }
  .prompt-box {
    background: #EDE8DF; border-radius: 10px; padding: 1rem 1.2rem;
    font-size: 0.85rem; color: #333; font-family: monospace;
    white-space: pre-wrap; border: 1px solid #D4CFC7;
  }
  .rubric-table th { background: #1565C0; color: white; padding: 8px 12px; font-size: 0.85rem; }
  .rubric-table td { padding: 8px 12px; border: 1px solid #E0E8F4; font-size: 0.83rem; }
  .rubric-table tr:nth-child(even) td { background: #F0F6FF; }
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────
# 상수 정의
# ───────────────────────────────────────────────
VARK_TYPES = ["시각형", "청각형", "읽기쓰기형", "운동감각형"]
VARK_DESC = {
    "시각형":    "그림·도표·색채로 이해 — 공간 시각화 강점",
    "청각형":    "말하기·토론·음악으로 이해 — 언어·리듬 강점",
    "읽기쓰기형":"텍스트 읽기·기록으로 이해 — 문자 표현 강점",
    "운동감각형":"직접 만들기·체험으로 이해 — 신체·제작 강점",
}
VARK_ROLE = {
    "시각형":    "AI 이미지 시각화 분석 리더",
    "청각형":    "낭독·발표·녹음 담당",
    "읽기쓰기형":"자료 수집·정리·인용 담당",
    "운동감각형":"에코봇 설계·제작·전시 담당",
}

HOLLAND_TYPES = ["탐구형(I)", "예술형(A)", "사회형(S)", "진취형(E)"]
HOLLAND_Q = {
    "탐구형(I)": "완도 생태 위기의 과학적 원인은 무엇인가?",
    "예술형(A)": "자연의 아름다움을 어떻게 시조로 표현할까?",
    "사회형(S)": "우리가 지역 공동체로 할 수 있는 실천은?",
    "진취형(E)": "탄소중립 캠페인을 어떻게 기획할 것인가?",
}
HOLLAND_DEEP = {
    "탐구형(I)": "AI 에코봇 알고리즘 설계 리더",
    "예술형(A)": "Canva 탄소중립 가이드북 디자인",
    "사회형(S)": "지역 어촌계 인터뷰 & 캠페인 기획",
    "진취형(E)": "프로젝트 발표 리더 & AI 에코봇 시연",
}

SEL_DOMAINS = ["자기인식", "자기조절", "사회적 인식", "관계 기술", "책임 있는 의사결정"]
SEL_LEVEL = ["높음", "보통", "지원 필요"]
SEL_SUPPORT = {
    "자기조절": {
        "지원 필요": "H단계 소그룹 체크인 + AI 감성 데이터로 정서 패턴 인식 지원",
        "보통": "매 영역 자기목표 설정 루틴 제공",
    },
    "관계 기술": {
        "높음": "L단계 전시·발표 진행자 역할 배정",
    },
    "사회적 인식": {
        "높음": "2영역 토론 합의 촉진자 역할",
        "지원 필요": "토론 후 '상대방 논리 요약하기' 루틴",
    },
}

SUBJECT_AREAS = {
    "수학": ["수와 연산", "도형", "측정", "규칙성", "자료와 가능성"],
    "국어": ["듣기·말하기", "읽기", "쓰기", "문법", "문학"],
    "과학": ["운동과 에너지", "물질", "생명", "지구와 우주"],
}

# 교사 관찰지 항목
T_FOCUS_OPTIONS   = ["5분 이내", "10분 내외", "20분 이상", "활동 유형에 따라 크게 다름"]
T_HELP_OPTIONS    = ["자발적으로 먼저 질문함", "교사가 물어볼 때만 대답함",
                     "친구에게 먼저 물어봄", "모르는 것을 잘 드러내지 않음"]
T_ENGAGE_OPTIONS  = ["읽고 분석하기", "만들고 제작하기", "토론하고 발표하기",
                     "조용히 글쓰기", "시각 자료 보기·그리기"]
T_FEEDBACK_OPTIONS= ["즉시 수정 시도", "천천히 반영함", "방어적 반응", "무반응·무관심"]
T_GROUP_OPTIONS   = ["주도적으로 이끔", "적극적으로 협력함", "수동적으로 참여함", "고립·참여 회피"]
T_FRUSTRATE_OPTIONS=["스스로 다시 시도함", "도움을 요청함", "포기하거나 회피함", "감정 표출(울거나 짜증)"]
T_MATCH_OPTIONS   = ["잘 일치함", "부분적으로 일치함", "거의 일치하지 않음", "아직 판단하기 이름"]

# 학생 자기관찰지 항목
S_FOCUS_OPTIONS   = ["선생님 설명을 들을 때", "친구들과 이야기하거나 토론할 때",
                     "뭔가를 직접 만들거나 해볼 때", "혼자 조용히 읽거나 쓸 때"]
S_ROLE_OPTIONS    = ["아이디어 내기", "정리하고 기록하기", "발표하기", "만들고 꾸미기", "자료 찾기·조사하기"]
S_HELP_OPTIONS    = ["선생님께 바로 물어본다", "친구한테 물어본다",
                     "혼자 찾아보다가 물어본다", "그냥 넘어가는 편이다"]
S_STUCK_OPTIONS   = ["다시 해보려고 노력한다", "누군가에게 도움을 요청한다",
                     "잠깐 멈추고 다른 걸 하다가 돌아온다", "그냥 포기한다"]
S_MOOD_OPTIONS    = ["편안하고 좋다", "아직 낯설고 어색하다", "긴장되거나 불안하다", "재미없거나 지루하다"]

# ───────────────────────────────────────────────
# 세션 상태 초기화
# ───────────────────────────────────────────────
if "students" not in st.session_state:
    st.session_state.students = {}
if "page" not in st.session_state:
    st.session_state.page = "입력"

# ───────────────────────────────────────────────
# 샘플 데이터 생성
# ───────────────────────────────────────────────
def generate_sample(n=25):
    students = {}
    mood_labels = ["편안하고 좋다", "아직 낯설고 어색하다", "긴장되거나 불안하다"]
    for i in range(1, n + 1):
        vark = random.choice(VARK_TYPES)
        holland = random.choice(HOLLAND_TYPES)
        sel = {d: random.choice(SEL_LEVEL) for d in SEL_DOMAINS}
        diag = {}
        for subj, areas in SUBJECT_AREAS.items():
            diag[subj] = {area: round(random.uniform(45, 98), 1) for area in areas}

        # 교사 관찰지 샘플
        teacher_obs = {
            "t_focus":    random.choice(T_FOCUS_OPTIONS),
            "t_help":     random.choice(T_HELP_OPTIONS),
            "t_engage":   random.sample(T_ENGAGE_OPTIONS, k=random.randint(1, 3)),
            "t_feedback": random.choice(T_FEEDBACK_OPTIONS),
            "t_group":    random.choice(T_GROUP_OPTIONS),
            "t_frustrate":random.choice(T_FRUSTRATE_OPTIONS),
            "t_relation": random.choice(["해당 없음", "특정 학생과 갈등 관찰 중", "교우 관계 고립 우려"]),
            "t_vark_match":random.choice(T_MATCH_OPTIONS),
            "t_sel_match": random.choice(T_MATCH_OPTIONS),
            "t_memo":     random.choice(["시각 자료 중심 활동에서 두드러짐",
                                         "발표 시 긴장 많이 함. 소규모 발표부터 경험 필요",
                                         "모둠 활동 적극적, 리더 역할 적합",
                                         "혼자 탐구 시 집중력 높음", ""]),
        }
        # 학생 자기관찰지 샘플
        student_obs = {
            "s_focus":    random.choice(S_FOCUS_OPTIONS),
            "s_role":     random.sample(S_ROLE_OPTIONS, k=random.randint(1, 3)),
            "s_help":     random.choice(S_HELP_OPTIONS),
            "s_curious":  random.choice(["바다 쓰레기가 왜 계속 늘어나는지 궁금해요",
                                         "AI가 어떻게 그림을 그리는지 궁금해요",
                                         "기후 변화를 막을 수 있는 방법이 있을까요?",
                                         "우리 지역에서 할 수 있는 환경 운동은?", ""]),
            "s_nature":   random.choice(["나에게 자연이란 쉬는 곳이다. 바다에 가면 머리가 맑아지기 때문이다.",
                                         "나에게 자연이란 탐구 대상이다. 관찰하면 할수록 신기한 게 많다.",
                                         "나에게 자연이란 지켜야 할 곳이다. 오염되면 되돌릴 수 없기 때문이다.",
                                         "나에게 자연이란 친구이다. 가끔 답답할 때 산이나 바다에 가면 위로가 된다.", ""]),
            "s_stuck":    random.choice(S_STUCK_OPTIONS),
            "s_mood":     random.choice(mood_labels),
            "s_teacher_know": random.choice(["저는 사람 많은 곳에서 발표하는 게 많이 힘들어요",
                                              "수학 분수 부분이 아직 헷갈려요",
                                              "모둠 활동을 좋아해요!", "", ""]),
            "s_goal":     random.choice(["발표를 떨지 않고 하고 싶어요",
                                         "수학 분수를 완전히 이해하고 싶어요",
                                         "친구들과 협력해서 멋진 프로젝트를 만들고 싶어요", ""]),
            "s_wish":     random.choice(["영상을 더 많이 보여줬으면 해요",
                                         "직접 해보는 활동이 더 많으면 좋겠어요",
                                         "토론 시간이 더 많았으면 해요", ""]),
        }

        students[i] = {
            "번호": i, "vark": vark, "holland": holland,
            "sel": sel, "diag": diag,
            "teacher_obs": teacher_obs,
            "student_obs": student_obs,
        }
    return students

# ───────────────────────────────────────────────
# 사이드바
# ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 학생 데이터 분석")
    st.markdown("HEAL 프로젝트 수업설계 지원")
    st.markdown("---")
    page = st.radio(
        "메뉴",
        ["📥 데이터 입력", "📝 관찰지 입력", "👤 학생 프로파일",
         "👥 학급 전체 분석", "🧩 모둠 구성 추천",
         "📐 수업 설계 제안", "📋 AI 프롬프트 생성"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown(f"**등록 학생 수:** {len(st.session_state.students)}명")
    if st.button("🎲 샘플 데이터 생성 (25명)", use_container_width=True):
        st.session_state.students = generate_sample(25)
        st.success("샘플 데이터 생성 완료!")
        st.rerun()
    if st.button("🗑 데이터 초기화", use_container_width=True):
        st.session_state.students = {}
        st.rerun()
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; opacity:0.8; line-height:1.7'>
    📌 출처<br>
    · VARK (Fleming, 1992)<br>
    · Holland RIASEC (1997)<br>
    · CASEL SEL Framework (2020)<br>
    · OECD Digital Education 2026<br>
    · UNESCO AI in Education (2023)
    </div>
    """, unsafe_allow_html=True)

# ───────────────────────────────────────────────
# 헬퍼 함수
# ───────────────────────────────────────────────
def get_weak_areas(diag, threshold=70):
    weak = []
    for subj, areas in diag.items():
        for area, score in areas.items():
            if score < threshold:
                weak.append(f"{subj} - {area} ({score}%)")
    return weak

def get_sel_support(sel):
    tips = []
    for domain, level in sel.items():
        if domain in SEL_SUPPORT and level in SEL_SUPPORT[domain]:
            tips.append(SEL_SUPPORT[domain][level])
    return tips

def score_color(score):
    if score >= 80: return "#2E7D32"
    if score >= 60: return "#E65100"
    return "#C62828"

def radar_chart(sel_data, student_num):
    levels_map = {"높음": 3, "보통": 2, "지원 필요": 1}
    vals = [levels_map.get(sel_data[d], 2) for d in SEL_DOMAINS]
    vals += [vals[0]]
    cats = SEL_DOMAINS + [SEL_DOMAINS[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats, fill='toself',
        fillcolor='rgba(21,101,192,0.15)',
        line=dict(color='#1565C0', width=2),
        marker=dict(size=6, color='#1565C0')
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 3],
                tickvals=[1,2,3], ticktext=["지원필요","보통","높음"],
                tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=11))
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=30, b=30),
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

def bar_chart_diag(diag_data, student_num):
    all_areas, all_scores, all_colors, all_subjs = [], [], [], []
    for subj, areas in diag_data.items():
        for area, score in areas.items():
            all_areas.append(area)
            all_scores.append(score)
            all_colors.append(score_color(score))
            all_subjs.append(subj)
    df = pd.DataFrame({"영역": all_areas, "정답률": all_scores,
                       "색상": all_colors, "교과": all_subjs})
    fig = px.bar(df, x="정답률", y="영역", color="교과",
                 orientation='h', text="정답률",
                 color_discrete_map={"수학":"#1565C0","국어":"#2E7D32","과학":"#E65100"},
                 height=max(280, len(all_areas)*28))
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.add_vline(x=70, line_dash="dash", line_color="#E57373",
                  annotation_text="70% 기준선", annotation_font_size=10)
    fig.update_layout(
        margin=dict(l=10, r=60, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0, 115], gridcolor='#EEE'),
        yaxis=dict(gridcolor='#EEE'),
        legend=dict(orientation="h", y=-0.15),
    )
    return fig

# ───────────────────────────────────────────────
# 페이지 1: 데이터 입력
# ───────────────────────────────────────────────
if page == "📥 데이터 입력":
    st.title("📥 학생 데이터 입력")

    # ── API 키 확인 ──────────────────────────────────
    api_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    if not api_key:
        api_key = st.sidebar.text_input(
            "Gemini API Key", type="password",
            placeholder="AIza...",
            help="이미지 자동 파싱에 필요합니다. Streamlit secrets에 GEMINI_API_KEY로 등록하면 자동 로드됩니다."
        )

    # ── 이미지 → OCR 파싱 함수 (Gemini Vision) ──────
    def parse_image_with_gemini(image_bytes: bytes, exam_type: str, api_key: str) -> dict:
        """Gemini Vision API로 검사 결과지 이미지를 파싱."""
        import base64, urllib.request, urllib.error
        b64 = base64.standard_b64encode(image_bytes).decode()

        PROMPTS = {
            "vark": """이 이미지는 학습유형검사(VARK) 결과지입니다.
아래 JSON 형식으로만 응답하세요. 다른 말은 절대 하지 마세요.
{
  "vark": "시각형 또는 청각형 또는 읽기쓰기형 또는 운동감각형",
  "scores": {"시각형": 숫자, "청각형": 숫자, "읽기쓰기형": 숫자, "운동감각형": 숫자}
}
점수가 보이지 않으면 scores는 빈 객체 {}로 두세요.""",

            "holland": """이 이미지는 진로탐색검사(Holland RIASEC) 결과지입니다.
아래 JSON 형식으로만 응답하세요. 다른 말은 절대 하지 마세요.
{
  "holland": "탐구형(I) 또는 예술형(A) 또는 사회형(S) 또는 진취형(E) 또는 현실형(R) 또는 관습형(C)",
  "scores": {"R": 숫자, "I": 숫자, "A": 숫자, "S": 숫자, "E": 숫자, "C": 숫자}
}
점수가 보이지 않으면 scores는 빈 객체 {}로 두세요.""",

            "sel": """이 이미지는 사회정서역량검사(SEL/CASEL) 결과지입니다.
아래 JSON 형식으로만 응답하세요. 다른 말은 절대 하지 마세요.
각 영역의 수준을 "높음", "보통", "지원 필요" 중 하나로 판단하세요.
점수가 있으면: 80점 이상=높음, 60~79점=보통, 60점 미만=지원 필요로 변환하세요.
{
  "자기인식": "높음 또는 보통 또는 지원 필요",
  "자기조절": "높음 또는 보통 또는 지원 필요",
  "사회적 인식": "높음 또는 보통 또는 지원 필요",
  "관계 기술": "높음 또는 보통 또는 지원 필요",
  "책임 있는 의사결정": "높음 또는 보통 또는 지원 필요"
}""",

            "diag": """이 이미지는 기초학력진단검사 결과지입니다.
아래 JSON 형식으로만 응답하세요. 다른 말은 절대 하지 마세요.
교과별·내용영역별 정답률(%)을 추출하세요.
없는 교과나 영역은 포함하지 마세요.
{
  "수학": {"수와 연산": 숫자, "도형": 숫자, "측정": 숫자, "규칙성": 숫자, "자료와 가능성": 숫자},
  "국어": {"듣기·말하기": 숫자, "읽기": 숫자, "쓰기": 숫자, "문법": 숫자, "문학": 숫자},
  "과학": {"운동과 에너지": 숫자, "물질": 숫자, "생명": 숫자, "지구와 우주": 숫자}
}
없는 항목은 제외하고 있는 항목만 포함하세요.""",
        }

        # Gemini 1.5 Flash — 빠르고 비용 효율적
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={api_key}"
        )
        payload = json.dumps({
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": b64
                        }
                    },
                    {"text": PROMPTS[exam_type]}
                ]
            }],
            "generationConfig": {
                "temperature": 0,
                "maxOutputTokens": 800,
            }
        }).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read())
                raw = body["candidates"][0]["content"]["parts"][0]["text"].strip()
                # JSON 블록만 추출
                if "```" in raw:
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                return json.loads(raw.strip())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            st.error(f"Gemini API 오류 ({e.code}): {err_body[:300]}")
            return {}
        except Exception as e:
            st.error(f"파싱 오류: {e}")
            return {}

    # ── 세션에 임시 파싱 결과 저장용 ───────────────
    if "parsed" not in st.session_state:
        st.session_state.parsed = {}

    # ── 학생 번호 ────────────────────────────────────
    st.markdown('<div class="section-title">학생 정보</div>', unsafe_allow_html=True)
    stu_num = st.number_input("학생 번호", min_value=1, max_value=40, value=1, key="stu_num_input")

    # ── 이미지 업로드 섹션 ──────────────────────────
    st.markdown('<div class="section-title">🖼 검사 결과지 이미지 업로드 (자동 파싱)</div>',
                unsafe_allow_html=True)

    has_api = bool(api_key)
    if not has_api:
        st.info("💡 사이드바에 Gemini API Key를 입력하면 이미지를 올리는 즉시 데이터를 자동으로 읽어옵니다. "
                "아래에서 직접 입력도 가능합니다.")

    upload_cols = st.columns(4)
    exam_labels = {
        "vark":    ("① 학습유형검사",   "upload_vark"),
        "holland": ("② 진로탐색검사",   "upload_holland"),
        "sel":     ("③ 사회정서역량검사","upload_sel"),
        "diag":    ("④ 기초학력진단검사","upload_diag"),
    }

    uploaded = {}
    for col, (etype, (label, key)) in zip(upload_cols, exam_labels.items()):
        with col:
            f = st.file_uploader(label, type=["png","jpg","jpeg","webp"], key=key)
            uploaded[etype] = f
            if f:
                st.image(f, use_column_width=True)

    # ── 파싱 실행 버튼 ──────────────────────────────
    any_uploaded = any(v is not None for v in uploaded.values())
    if any_uploaded:
        if st.button("🔍 업로드된 이미지 자동 파싱", type="primary",
                     disabled=not has_api,
                     help="API Key가 필요합니다" if not has_api else ""):
            parsed = st.session_state.parsed.copy()
            for etype, f in uploaded.items():
                if f is None:
                    continue
                f.seek(0)
                img_bytes = f.read()
                with st.spinner(f"{exam_labels[etype][0]} 파싱 중..."):
                    result = parse_image_with_gemini(img_bytes, etype, api_key)
                    if result:
                        parsed[etype] = result
                        st.success(f"✅ {exam_labels[etype][0]} 파싱 완료")
                    else:
                        st.warning(f"⚠ {exam_labels[etype][0]} 파싱 실패 — 아래에서 직접 입력하세요")
            st.session_state.parsed = parsed
            st.rerun()

        if not has_api:
            st.caption("API Key 없이도 아래에서 직접 입력할 수 있습니다.")

    # 파싱 결과 미리보기
    p = st.session_state.parsed
    if p:
        with st.expander("📋 파싱된 데이터 미리보기", expanded=True):
            pc = st.columns(len(p))
            for col, (etype, data) in zip(pc, p.items()):
                with col:
                    st.markdown(f"**{exam_labels[etype][0]}**")
                    st.json(data)

    st.markdown("---")

    # ── 수동 입력 (파싱 결과 자동 반영) ─────────────
    st.markdown('<div class="section-title">검사 결과 확인 · 수정</div>', unsafe_allow_html=True)
    st.caption("파싱된 값이 자동으로 채워집니다. 수정이 필요하면 직접 바꾸세요.")

    col1, col2 = st.columns([1, 2])

    with col1:
        # VARK
        st.markdown('<div class="section-title">① 학습유형검사 (VARK)</div>', unsafe_allow_html=True)
        parsed_vark = p.get("vark", {}).get("vark", "시각형")
        vark_default = parsed_vark if parsed_vark in VARK_TYPES else "시각형"
        vark = st.selectbox("주요 학습유형", VARK_TYPES,
                            index=VARK_TYPES.index(vark_default))
        if p.get("vark", {}).get("scores"):
            scores = p["vark"]["scores"]
            for t, sc in scores.items():
                bar_pct = min(int(sc), 100)
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:6px;margin:2px 0">'
                    f'<span style="font-size:11px;min-width:72px;color:var(--color-text-secondary)">{t}</span>'
                    f'<div style="flex:1;background:#EEE;border-radius:4px;height:6px">'
                    f'<div style="width:{bar_pct}%;background:#1565C0;height:6px;border-radius:4px"></div></div>'
                    f'<span style="font-size:11px;min-width:24px">{sc}</span></div>',
                    unsafe_allow_html=True)
        st.caption(VARK_DESC[vark])

        # Holland
        st.markdown('<div class="section-title">② 진로탐색검사 (Holland)</div>', unsafe_allow_html=True)
        parsed_h = p.get("holland", {}).get("holland", "탐구형(I)")
        holland_default = parsed_h if parsed_h in HOLLAND_TYPES else "탐구형(I)"
        holland = st.selectbox("Holland 유형", HOLLAND_TYPES,
                               index=HOLLAND_TYPES.index(holland_default))
        if p.get("holland", {}).get("scores"):
            sc_map = {"R":"현실형","I":"탐구형","A":"예술형","S":"사회형","E":"진취형","C":"관습형"}
            scores = p["holland"]["scores"]
            max_sc = max(scores.values()) if scores else 1
            for code, val in scores.items():
                bar_pct = int(val / max_sc * 100) if max_sc else 0
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:6px;margin:2px 0">'
                    f'<span style="font-size:11px;min-width:72px;color:var(--color-text-secondary)">{sc_map.get(code,code)}</span>'
                    f'<div style="flex:1;background:#EEE;border-radius:4px;height:6px">'
                    f'<div style="width:{bar_pct}%;background:#2E7D32;height:6px;border-radius:4px"></div></div>'
                    f'<span style="font-size:11px;min-width:24px">{val}</span></div>',
                    unsafe_allow_html=True)
        st.caption(f"핵심 질문: {HOLLAND_Q[holland]}")

        # SEL
        st.markdown('<div class="section-title">③ 사회정서역량검사 (CASEL SEL)</div>', unsafe_allow_html=True)
        parsed_sel = p.get("sel", {})
        sel = {}
        for domain in SEL_DOMAINS:
            default_lv = parsed_sel.get(domain, "보통")
            if default_lv not in ["높음","보통","지원 필요"]:
                default_lv = "보통"
            tag_color = {"높음":"#2E7D32","보통":"#E65100","지원 필요":"#C62828"}.get(default_lv,"#888")
            badge = f'<span style="font-size:10px;background:{tag_color}20;color:{tag_color};padding:1px 7px;border-radius:10px;margin-left:4px">{default_lv}</span>' if parsed_sel else ""
            sel[domain] = st.select_slider(
                domain + ("  ✨" if domain in parsed_sel else ""),
                options=["지원 필요","보통","높음"],
                value=default_lv,
                key=f"sel_{domain}"
            )

    with col2:
        # 기초학력
        st.markdown('<div class="section-title">④ 기초학력진단검사 결과</div>', unsafe_allow_html=True)
        st.caption("70% 미만은 취약 영역으로 자동 분류됩니다.")
        parsed_diag = p.get("diag", {})

        diag = {}
        tabs_diag = st.tabs(list(SUBJECT_AREAS.keys()))
        for tab_d, (subj, areas) in zip(tabs_diag, SUBJECT_AREAS.items()):
            with tab_d:
                diag[subj] = {}
                cols_d = st.columns(2)
                for idx, area in enumerate(areas):
                    default_score = float(
                        parsed_diag.get(subj, {}).get(area, 75.0)
                    )
                    is_parsed = subj in parsed_diag and area in parsed_diag[subj]
                    label = area + (" ✨" if is_parsed else "")
                    color_hint = " 🔴" if default_score < 70 else ""
                    with cols_d[idx % 2]:
                        diag[subj][area] = st.number_input(
                            label + color_hint,
                            min_value=0.0, max_value=100.0,
                            value=default_score, step=0.1,
                            key=f"diag_{subj}_{area}_{stu_num}"
                        )
                        if default_score < 70:
                            st.markdown(
                                '<span style="font-size:10px;color:#C62828">⚠ 취약영역</span>',
                                unsafe_allow_html=True)

    # ── 저장 ────────────────────────────────────────
    st.markdown("---")
    c1, c2 = st.columns([3,1])
    with c1:
        parsed_count = len(p)
        if parsed_count:
            st.success(f"✅ {parsed_count}개 검사 자동 파싱 완료 — 값 확인 후 저장하세요. "
                       f"(✨ 표시 항목이 자동 입력된 값입니다)")
    with c2:
        if st.button("✅ 학생 데이터 저장", type="primary", use_container_width=True):
            existing = st.session_state.students.get(stu_num, {})
            st.session_state.students[stu_num] = {
                "번호": stu_num,
                "vark": vark,
                "holland": holland,
                "sel": sel,
                "diag": diag,
                "teacher_obs": existing.get("teacher_obs", {}),
                "student_obs": existing.get("student_obs", {}),
            }
            st.session_state.parsed = {}   # 파싱 버퍼 초기화
            st.success(
                f"✅ {stu_num}번 학생 데이터 저장 완료! "
                f"(현재 총 {len(st.session_state.students)}명)"
            )

    # ── 저장된 학생 목록 ────────────────────────────
    if st.session_state.students:
        st.markdown('<div class="section-title">저장된 학생 목록</div>', unsafe_allow_html=True)
        summary = []
        for num, s in sorted(st.session_state.students.items()):
            weak = get_weak_areas(s["diag"])
            summary.append({
                "번호": num,
                "학습유형": s["vark"],
                "진로유형": s["holland"],
                "자기조절": s["sel"]["자기조절"],
                "취약영역 수": len(weak),
                "교사관찰지": "✅" if s.get("teacher_obs") else "⬜",
                "학생관찰지": "✅" if s.get("student_obs") else "⬜",
            })
        st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

# ───────────────────────────────────────────────
# 페이지 2: 관찰지 입력
# ───────────────────────────────────────────────
elif page == "📝 관찰지 입력":
    st.title("📝 첫 2주 관찰지 입력")
    st.caption("교사 관찰지와 학생 자기관찰지를 입력합니다. 검사 결과와 함께 통합 분석됩니다.")

    if not st.session_state.students:
        st.warning("먼저 '📥 데이터 입력' 메뉴에서 학생 기본 데이터를 등록해주세요.")
        st.stop()

    stu_num = st.selectbox("학생 번호 선택",
                           sorted(st.session_state.students.keys()),
                           format_func=lambda x: f"{x}번 학생")
    s = st.session_state.students[stu_num]
    existing_t = s.get("teacher_obs", {})
    existing_s = s.get("student_obs", {})

    tab_t, tab_s = st.tabs(["👩‍🏫 교사 관찰지", "🧒 학생 자기관찰지"])

    # ── 교사 관찰지 ──────────────────────────────
    with tab_t:
        st.markdown('<div class="section-title">① 학습 행동 관찰</div>',
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            t_focus = st.selectbox(
                "Q1. 수업 중 집중 지속 시간",
                T_FOCUS_OPTIONS,
                index=T_FOCUS_OPTIONS.index(existing_t.get("t_focus", T_FOCUS_OPTIONS[1]))
                      if existing_t.get("t_focus") in T_FOCUS_OPTIONS else 1
            )
            t_help = st.selectbox(
                "Q2. 도움·질문 요청 방식",
                T_HELP_OPTIONS,
                index=T_HELP_OPTIONS.index(existing_t.get("t_help", T_HELP_OPTIONS[0]))
                      if existing_t.get("t_help") in T_HELP_OPTIONS else 0
            )
        with col2:
            t_feedback = st.selectbox(
                "Q4. 피드백 받았을 때 반응",
                T_FEEDBACK_OPTIONS,
                index=T_FEEDBACK_OPTIONS.index(existing_t.get("t_feedback", T_FEEDBACK_OPTIONS[0]))
                      if existing_t.get("t_feedback") in T_FEEDBACK_OPTIONS else 0
            )
            t_frustrate = st.selectbox(
                "Q6. 어려움·좌절 상황에서 보이는 행동",
                T_FRUSTRATE_OPTIONS,
                index=T_FRUSTRATE_OPTIONS.index(existing_t.get("t_frustrate", T_FRUSTRATE_OPTIONS[0]))
                      if existing_t.get("t_frustrate") in T_FRUSTRATE_OPTIONS else 0
            )

        t_engage = st.multiselect(
            "Q3. 두드러지게 몰입하는 활동 유형 (복수 선택)",
            T_ENGAGE_OPTIONS,
            default=existing_t.get("t_engage", [])
        )

        st.markdown('<div class="section-title">② 관계·정서 관찰</div>',
                    unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            t_group = st.selectbox(
                "Q5. 모둠 활동 역할",
                T_GROUP_OPTIONS,
                index=T_GROUP_OPTIONS.index(existing_t.get("t_group", T_GROUP_OPTIONS[0]))
                      if existing_t.get("t_group") in T_GROUP_OPTIONS else 0
            )
        with col4:
            t_relation = st.text_input(
                "Q7. 특이 관계 상황 (없으면 비워두세요)",
                value=existing_t.get("t_relation", ""),
                placeholder="예: 3번 학생과 갈등 이력 있음"
            )

        st.markdown('<div class="section-title">③ 검사 결과 교차 확인</div>',
                    unsafe_allow_html=True)
        col5, col6 = st.columns(2)
        with col5:
            t_vark_match = st.selectbox(
                "Q8. 학습유형검사 결과와 실제 행동 일치도",
                T_MATCH_OPTIONS,
                index=T_MATCH_OPTIONS.index(existing_t.get("t_vark_match", T_MATCH_OPTIONS[0]))
                      if existing_t.get("t_vark_match") in T_MATCH_OPTIONS else 0
            )
        with col6:
            t_sel_match = st.selectbox(
                "Q9. SEL검사 결과와 실제 정서·관계 행동 일치도",
                T_MATCH_OPTIONS,
                index=T_MATCH_OPTIONS.index(existing_t.get("t_sel_match", T_MATCH_OPTIONS[0]))
                      if existing_t.get("t_sel_match") in T_MATCH_OPTIONS else 0
            )

        st.markdown('<div class="section-title">④ 수업 설계 메모</div>',
                    unsafe_allow_html=True)
        t_memo = st.text_area(
            "Q10. 수업 설계 시 반드시 고려할 사항",
            value=existing_t.get("t_memo", ""),
            height=100,
            placeholder="모둠 배치, 역할 배정, 피드백 전략, 특이사항 등 자유롭게 메모"
        )

        if st.button("💾 교사 관찰지 저장", type="primary", use_container_width=True):
            st.session_state.students[stu_num]["teacher_obs"] = {
                "t_focus": t_focus, "t_help": t_help, "t_engage": t_engage,
                "t_feedback": t_feedback, "t_group": t_group,
                "t_frustrate": t_frustrate, "t_relation": t_relation,
                "t_vark_match": t_vark_match, "t_sel_match": t_sel_match,
                "t_memo": t_memo,
            }
            st.success(f"✅ {stu_num}번 교사 관찰지 저장 완료!")

    # ── 학생 자기관찰지 ──────────────────────────
    with tab_s:
        st.markdown('<div class="section-title">① 나는 어떻게 배우나요?</div>',
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            s_focus = st.selectbox(
                "Q1. 수업 중 집중이 잘 되는 순간",
                S_FOCUS_OPTIONS,
                index=S_FOCUS_OPTIONS.index(existing_s.get("s_focus", S_FOCUS_OPTIONS[0]))
                      if existing_s.get("s_focus") in S_FOCUS_OPTIONS else 0
            )
        with col2:
            s_help = st.selectbox(
                "Q3. 모를 때 나는 보통",
                S_HELP_OPTIONS,
                index=S_HELP_OPTIONS.index(existing_s.get("s_help", S_HELP_OPTIONS[0]))
                      if existing_s.get("s_help") in S_HELP_OPTIONS else 0
            )

        s_role = st.multiselect(
            "Q2. 모둠 활동에서 좋아하는 역할 (복수 선택)",
            S_ROLE_OPTIONS,
            default=existing_s.get("s_role", [])
        )

        st.markdown('<div class="section-title">② 나의 관심사와 경험</div>',
                    unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            s_curious = st.text_area(
                "Q4. 요즘 내가 가장 궁금한 것",
                value=existing_s.get("s_curious", ""),
                height=90,
                placeholder="학교 공부가 아니어도 됩니다"
            )
        with col4:
            s_nature = st.text_area(
                "Q5. 나에게 자연이란 ___ 이다 (이유 포함)",
                value=existing_s.get("s_nature", ""),
                height=90,
                placeholder="예: 쉬는 곳이다. 바다에 가면 머리가 맑아지기 때문이다."
            )

        st.markdown('<div class="section-title">③ 나의 감정과 관계</div>',
                    unsafe_allow_html=True)
        col5, col6 = st.columns(2)
        with col5:
            s_stuck = st.selectbox(
                "Q6. 수업이 잘 안 풀릴 때 나는?",
                S_STUCK_OPTIONS,
                index=S_STUCK_OPTIONS.index(existing_s.get("s_stuck", S_STUCK_OPTIONS[0]))
                      if existing_s.get("s_stuck") in S_STUCK_OPTIONS else 0
            )
        with col6:
            s_mood = st.selectbox(
                "Q7. 지금 이 반에서 내 기분",
                S_MOOD_OPTIONS,
                index=S_MOOD_OPTIONS.index(existing_s.get("s_mood", S_MOOD_OPTIONS[0]))
                      if existing_s.get("s_mood") in S_MOOD_OPTIONS else 0
            )

        s_teacher_know = st.text_area(
            "Q8. 선생님이 나를 도와주기 위해 꼭 알아야 할 것",
            value=existing_s.get("s_teacher_know", ""),
            height=70,
            placeholder="공부, 친구 관계, 건강 등 무엇이든. 쓰기 싫으면 비워도 됩니다."
        )

        st.markdown('<div class="section-title">④ 학습 목표</div>',
                    unsafe_allow_html=True)
        col7, col8 = st.columns(2)
        with col7:
            s_goal = st.text_area(
                "Q9. 올해 학교에서 잘하고 싶은 것",
                value=existing_s.get("s_goal", ""),
                height=80,
                placeholder="예: 발표를 떨지 않고 하고 싶어요"
            )
        with col8:
            s_wish = st.text_area(
                "Q10. 수업에 바라는 점",
                value=existing_s.get("s_wish", ""),
                height=80,
                placeholder="예: 직접 해보는 활동이 더 많으면 좋겠어요"
            )

        if st.button("💾 학생 자기관찰지 저장", type="primary", use_container_width=True):
            st.session_state.students[stu_num]["student_obs"] = {
                "s_focus": s_focus, "s_role": s_role, "s_help": s_help,
                "s_curious": s_curious, "s_nature": s_nature,
                "s_stuck": s_stuck, "s_mood": s_mood,
                "s_teacher_know": s_teacher_know,
                "s_goal": s_goal, "s_wish": s_wish,
            }
            st.success(f"✅ {stu_num}번 학생 자기관찰지 저장 완료!")

    # 입력 현황 요약
    st.markdown("---")
    st.markdown('<div class="section-title">📊 관찰지 입력 현황</div>',
                unsafe_allow_html=True)
    obs_summary = []
    for num, stu in sorted(st.session_state.students.items()):
        has_t = bool(stu.get("teacher_obs"))
        has_s = bool(stu.get("student_obs"))
        obs_summary.append({
            "번호": num,
            "교사 관찰지": "✅ 완료" if has_t else "⬜ 미입력",
            "학생 자기관찰지": "✅ 완료" if has_s else "⬜ 미입력",
            "둘 다 완료": "🟢" if (has_t and has_s) else ("🟡" if (has_t or has_s) else "⚪"),
        })
    st.dataframe(pd.DataFrame(obs_summary), use_container_width=True, hide_index=True)


    # ── 관찰지 입력 현황 요약 끝 → 학생 프로파일 페이지는 elif로 분리됨

# ───────────────────────────────────────────────
# 페이지 3: 학생 프로파일 (관찰지 통합)
# ───────────────────────────────────────────────
elif page == "👤 학생 프로파일":
    st.title("👤 개별 학생 프로파일")
    st.caption("검사 4종 + 첫 2주 관찰지를 통합한 종합 분석입니다.")

    if not st.session_state.students:
        st.warning("먼저 데이터를 입력하거나 샘플 데이터를 생성해주세요.")
        st.stop()

    stu_num = st.selectbox("학생 번호 선택",
                           sorted(st.session_state.students.keys()),
                           format_func=lambda x: f"{x}번 학생")
    s       = st.session_state.students[stu_num]
    weak    = get_weak_areas(s["diag"])
    sel_tips= get_sel_support(s["sel"])
    t_obs   = s.get("teacher_obs", {})
    s_obs   = s.get("student_obs", {})
    has_t   = bool(t_obs)
    has_s   = bool(s_obs)

    # 헤더
    obs_badge = ""
    if has_t and has_s:
        obs_badge = '&nbsp;<span style="background:rgba(255,255,255,0.25);padding:2px 10px;border-radius:20px;font-size:0.78rem">관찰지 완비 ✅</span>'
    elif has_t or has_s:
        obs_badge = '&nbsp;<span style="background:rgba(255,255,255,0.2);padding:2px 10px;border-radius:20px;font-size:0.78rem">관찰지 일부 입력</span>'
    else:
        obs_badge = '&nbsp;<span style="background:rgba(255,255,255,0.15);padding:2px 10px;border-radius:20px;font-size:0.78rem">관찰지 미입력</span>'

    st.markdown(f"""
    <div class="profile-header">
      <div style="font-size:1.3rem;font-weight:700;margin-bottom:0.5rem">
        {stu_num}번 학생 · 종합 프로파일{obs_badge}
      </div>
      <div style="opacity:0.9;font-size:0.9rem">
        학습유형: <b>{s['vark']}</b> &nbsp;|&nbsp;
        진로유형: <b>{s['holland']}</b> &nbsp;|&nbsp;
        취약영역: <b>{len(weak)}개</b> &nbsp;|&nbsp;
        데이터 소스: <b>검사 4종{"＋교사관찰" if has_t else ""}{"＋학생자기보고" if has_s else ""}</b>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # 학습유형 카드 (관찰지 교차 포함)
        st.markdown('<div class="section-title">학습유형 & HEAL 역할 배치</div>',
                    unsafe_allow_html=True)
        vark_extra = ""
        if t_obs.get("t_vark_match"):
            color = "#2E7D32" if "잘 일치" in t_obs["t_vark_match"] else (
                    "#E65100" if "부분" in t_obs["t_vark_match"] else "#C62828")
            vark_extra += f'<div style="font-size:0.79rem;color:{color};margin-top:3px">📋 교사 관찰 일치도: {t_obs["t_vark_match"]}</div>'
        if t_obs.get("t_engage"):
            vark_extra += f'<div style="font-size:0.79rem;color:#555;margin-top:2px">🎯 실제 몰입 유형: {", ".join(t_obs["t_engage"])}</div>'
        if s_obs.get("s_focus"):
            vark_extra += f'<div style="font-size:0.79rem;color:#555;margin-top:2px">🧒 학생 자기보고: {s_obs["s_focus"]}</div>'
        st.markdown(f"""
        <div class="metric-card">
          <div style="font-size:1.1rem;font-weight:600;color:#1565C0">{s['vark']}</div>
          <div style="font-size:0.85rem;color:#555;margin:3px 0">{VARK_DESC[s['vark']]}</div>
          {vark_extra}
          <div style="font-size:0.82rem;color:#333;margin-top:8px;padding-top:6px;border-top:1px solid #EEF">
            <b>추천 HEAL 역할:</b> {VARK_ROLE[s['vark']]}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # 진로유형 카드 (학생 관심사 연결)
        st.markdown('<div class="section-title">진로유형 & 핵심 질문 개인화</div>',
                    unsafe_allow_html=True)
        holland_extra = ""
        if s_obs.get("s_curious"):
            holland_extra += f'<div style="font-size:0.79rem;color:#555;margin-top:3px">💬 학생 관심사: <i>"{s_obs["s_curious"]}"</i></div>'
        if s_obs.get("s_nature"):
            holland_extra += f'<div style="font-size:0.79rem;color:#2E7D32;margin-top:2px">🌿 자연관: <i>"{s_obs["s_nature"]}"</i></div>'
        st.markdown(f"""
        <div class="metric-card">
          <div style="font-size:1.1rem;font-weight:600;color:#1565C0">{s['holland']}</div>
          <div style="font-size:0.85rem;color:#555;margin:3px 0">
            핵심 질문: <i>"{HOLLAND_Q[s['holland']]}"</i>
          </div>
          {holland_extra}
          <div style="font-size:0.82rem;color:#333;margin-top:8px;padding-top:6px;border-top:1px solid #EEF">
            <b>심화 활동:</b> {HOLLAND_DEEP[s['holland']]}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # 교사 지원 전략 (SEL + 관찰지 통합)
        st.markdown('<div class="section-title">교사 지원 전략</div>',
                    unsafe_allow_html=True)
        if sel_tips:
            for tip in sel_tips:
                st.markdown(f'<div class="success-box">✅ {tip}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">✅ 표준 HEAL 활동 참여 가능</div>',
                        unsafe_allow_html=True)
        if t_obs.get("t_group") == "고립·참여 회피":
            st.markdown('<div class="warn-box">⚠ 모둠 참여 어려움 — H단계 2인 소그룹부터 점진 확장</div>',
                        unsafe_allow_html=True)
        if t_obs.get("t_frustrate") in ("포기하거나 회피함", "감정 표출(울거나 짜증)"):
            st.markdown('<div class="warn-box">⚠ 좌절 대응 지원 — 소규모 성공 경험 먼저 제공</div>',
                        unsafe_allow_html=True)
        if t_obs.get("t_memo"):
            st.markdown(f'<div class="success-box">📝 교사 메모: {t_obs["t_memo"]}</div>',
                        unsafe_allow_html=True)
        if s_obs.get("s_teacher_know"):
            st.markdown(f'<div class="success-box">🧒 학생 전달: {s_obs["s_teacher_know"]}</div>',
                        unsafe_allow_html=True)
        if s_obs.get("s_mood") in ("긴장되거나 불안하다", "재미없거나 지루하다"):
            st.markdown(f'<div class="warn-box">⚠ 정서 상태: "{s_obs["s_mood"]}" — 안전한 참여 환경 우선</div>',
                        unsafe_allow_html=True)
        if s_obs.get("s_wish"):
            st.markdown(f'<div class="success-box">🎯 수업 선호: {s_obs["s_wish"]}</div>',
                        unsafe_allow_html=True)

        # 취약영역 + 관계 특이사항
        if weak:
            st.markdown('<div class="section-title">취약 내용영역</div>', unsafe_allow_html=True)
            for w in weak:
                st.markdown(f'<div class="warn-box">⚠ {w}</div>', unsafe_allow_html=True)
        if t_obs.get("t_relation") and t_obs["t_relation"] not in ("", "해당 없음"):
            st.markdown(f'<div class="warn-box">⚠ 관계 특이사항: {t_obs["t_relation"]}<br>'
                        f'→ 모둠 구성 AI 초안에서 반드시 수동 수정 필요</div>',
                        unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">사회정서역량 (SEL) 레이더</div>',
                    unsafe_allow_html=True)
        if t_obs.get("t_sel_match") == "거의 일치하지 않음":
            st.warning("⚠ SEL 검사 결과와 실제 행동 불일치 — 관찰 데이터 우선 참고")
        st.plotly_chart(radar_chart(s["sel"], stu_num),
                        use_container_width=True, key=f"radar_{stu_num}")

        st.markdown('<div class="section-title">기초학력진단 내용영역별 정답률</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(bar_chart_diag(s["diag"], stu_num),
                        use_container_width=True, key=f"bar_{stu_num}")

    # 관찰지 원본 (접이식)
    if has_t or has_s:
        with st.expander("🔍 첫 2주 관찰지 원본 보기", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**👩‍🏫 교사 관찰지**")
                if has_t:
                    for label, key in [("집중 지속 시간","t_focus"),("도움 요청 방식","t_help"),
                                       ("피드백 반응","t_feedback"),("모둠 역할","t_group"),
                                       ("좌절 반응","t_frustrate"),("학습유형 일치도","t_vark_match"),
                                       ("SEL 일치도","t_sel_match"),("관계 특이사항","t_relation"),
                                       ("수업 설계 메모","t_memo")]:
                        val = t_obs.get(key, "")
                        if val: st.markdown(f"- **{label}:** {val}")
                    engage = t_obs.get("t_engage", [])
                    if engage: st.markdown(f"- **몰입 활동 유형:** {', '.join(engage)}")
                else:
                    st.caption("미입력 → 📝 관찰지 입력 메뉴에서 추가하세요")
            with c2:
                st.markdown("**🧒 학생 자기관찰지**")
                if has_s:
                    for label, key in [("집중이 잘 되는 순간","s_focus"),("모를 때 행동","s_help"),
                                       ("요즘 궁금한 것","s_curious"),("자연관","s_nature"),
                                       ("잘 안 풀릴 때","s_stuck"),("반 분위기 느낌","s_mood"),
                                       ("교사에게 전할 말","s_teacher_know"),
                                       ("올해 목표","s_goal"),("수업 바라는 점","s_wish")]:
                        val = s_obs.get(key, "")
                        if val: st.markdown(f"- **{label}:** {val}")
                    roles = s_obs.get("s_role", [])
                    if roles: st.markdown(f"- **좋아하는 모둠 역할:** {', '.join(roles)}")
                else:
                    st.caption("미입력 → 📝 관찰지 입력 메뉴에서 추가하세요")

    # 통합 해석 메모
    st.markdown('<div class="section-title">📝 통합 해석 메모 (최대 6가지 데이터 교차 분석)</div>',
                unsafe_allow_html=True)
    low_adjust = s["sel"]["자기조절"] == "지원 필요"
    high_rel   = s["sel"]["관계 기술"] == "높음"
    memo_parts = [
        f"**학습유형({s['vark']})** 기반으로 모둠 내 **{VARK_ROLE[s['vark']]}** 역할을 배치하세요.",
        f"**진로유형({s['holland']})** 에 맞는 핵심 질문으로 탐구 경로를 개인화하세요.",
    ]
    if has_t and t_obs.get("t_vark_match") == "거의 일치하지 않음":
        memo_parts.append(f"⚠ **학습유형 불일치**: 검사 결과({s['vark']})와 실제 행동 다름 — 관찰 우선, 역할 배치 재검토")
    if has_s and s_obs.get("s_curious"):
        memo_parts.append(f"🌱 **핵심 질문 힌트**: 학생 관심사 '{s_obs['s_curious']}'를 HEAL 탐구 경로와 연결하세요.")
    if has_t and t_obs.get("t_relation") and t_obs["t_relation"] not in ("", "해당 없음"):
        memo_parts.append(f"⚠ **관계 주의**: {t_obs['t_relation']} — AI 모둠 초안 반드시 수동 수정")
    if low_adjust:
        memo_parts.append("**자기조절 지원 필요** — H단계 소그룹 체크인, 매 차시 목표 자기 설정 루틴")
    if high_rel:
        memo_parts.append("**관계 기술 높음** — L단계 전시·발표 진행자 역할 배정")
    if weak:
        memo_parts.append(f"**취약 영역 {len(weak)}개** — 수업 중 연결 질문으로 보완")
    for m in memo_parts:
        st.markdown(f"- {m}")
    src_count = 4 + (1 if has_t else 0) + (1 if has_s else 0)
    st.caption(f"⚠ 위 해석은 {src_count}가지 데이터 기반 가설입니다. 수업 중 관찰로 반드시 교차 검증하세요.")

# ───────────────────────────────────────────────
# 페이지 3: 학급 전체 분석
# ───────────────────────────────────────────────
elif page == "👥 학급 전체 분석":
    st.title("👥 학급 전체 분석")

    if not st.session_state.students:
        st.warning("먼저 데이터를 입력하거나 샘플 데이터를 생성해주세요.")
        st.stop()

    students = st.session_state.students
    n = len(students)

    # ─ 요약 지표
    vark_cnt    = pd.Series([s["vark"] for s in students.values()]).value_counts()
    holland_cnt = pd.Series([s["holland"] for s in students.values()]).value_counts()
    weak_counts = [len(get_weak_areas(s["diag"])) for s in students.values()]
    avg_weak    = np.mean(weak_counts)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 학생 수", f"{n}명")
    m2.metric("가장 많은 학습유형", vark_cnt.idxmax())
    m3.metric("가장 많은 진로유형", holland_cnt.idxmax())
    m4.metric("학생당 평균 취약영역", f"{avg_weak:.1f}개")

    st.markdown("---")
    col1, col2 = st.columns(2)

    # VARK 분포
    with col1:
        st.markdown('<div class="section-title">학습유형 (VARK) 분포</div>',
                    unsafe_allow_html=True)
        fig_v = px.pie(
            values=vark_cnt.values, names=vark_cnt.index,
            color_discrete_sequence=["#1565C0","#1976D2","#42A5F5","#90CAF9"],
            hole=0.42
        )
        fig_v.update_traces(textinfo='label+value', textfont_size=13)
        fig_v.update_layout(
            showlegend=False, height=280,
            margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_v, use_container_width=True)

    # Holland 분포
    with col2:
        st.markdown('<div class="section-title">진로유형 (Holland) 분포</div>',
                    unsafe_allow_html=True)
        fig_h = px.pie(
            values=holland_cnt.values, names=holland_cnt.index,
            color_discrete_sequence=["#2E7D32","#43A047","#81C784","#C8E6C9"],
            hole=0.42
        )
        fig_h.update_traces(textinfo='label+value', textfont_size=13)
        fig_h.update_layout(
            showlegend=False, height=280,
            margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_h, use_container_width=True)

    # SEL 분포
    st.markdown('<div class="section-title">사회정서역량 (SEL) 영역별 분포</div>',
                unsafe_allow_html=True)
    sel_data = {d: {"높음": 0, "보통": 0, "지원 필요": 0} for d in SEL_DOMAINS}
    for s in students.values():
        for d, lv in s["sel"].items():
            sel_data[d][lv] += 1

    sel_df = pd.DataFrame(sel_data).T.reset_index()
    sel_df.columns = ["영역", "높음", "보통", "지원 필요"]
    fig_sel = go.Figure()
    for col, color in [("높음","#43A047"),("보통","#FFA726"),("지원 필요","#EF5350")]:
        fig_sel.add_trace(go.Bar(
            name=col, x=sel_df["영역"], y=sel_df[col],
            marker_color=color, text=sel_df[col], textposition='inside'
        ))
    fig_sel.update_layout(
        barmode='stack', height=280,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", y=-0.2),
        yaxis=dict(gridcolor='#EEE')
    )
    st.plotly_chart(fig_sel, use_container_width=True)

    # 기초학력 취약영역 히트맵
    st.markdown('<div class="section-title">기초학력 내용영역별 평균 정답률</div>',
                unsafe_allow_html=True)
    area_scores = {}
    for s in students.values():
        for subj, areas in s["diag"].items():
            for area, score in areas.items():
                key = f"{subj}\n{area}"
                area_scores.setdefault(key, []).append(score)
    area_avg = {k: np.mean(v) for k, v in area_scores.items()}
    labels = list(area_avg.keys())
    vals   = list(area_avg.values())
    colors = [score_color(v) for v in vals]

    fig_diag = go.Figure(go.Bar(
        x=vals, y=labels, orientation='h',
        marker_color=colors, text=[f"{v:.1f}%" for v in vals],
        textposition='outside'
    ))
    fig_diag.add_vline(x=70, line_dash="dash", line_color="#E57373",
                       annotation_text="70% 기준선")
    fig_diag.update_layout(
        height=max(300, len(labels)*30),
        margin=dict(l=0, r=60, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0, 115], gridcolor='#EEE'),
        yaxis=dict(gridcolor='#EEE'),
    )
    st.plotly_chart(fig_diag, use_container_width=True)

    # SEL 지원 필요 학생 목록
    st.markdown('<div class="section-title">⚠ 자기조절 지원 필요 학생</div>',
                unsafe_allow_html=True)
    need_support = [num for num, s in students.items()
                    if s["sel"]["자기조절"] == "지원 필요"]
    if need_support:
        st.markdown(
            " ".join([f'<span class="tag tag-red">{n}번</span>'
                      for n in sorted(need_support)]),
            unsafe_allow_html=True
        )
        st.caption(f"총 {len(need_support)}명 → H단계 소그룹 체크인 대상")
    else:
        st.success("자기조절 지원 필요 학생 없음")

# ───────────────────────────────────────────────
# 페이지 4: 모둠 구성 추천
# ───────────────────────────────────────────────
elif page == "🧩 모둠 구성 추천":
    st.title("🧩 모둠 구성 추천")
    st.caption("VARK·Holland 유형이 모둠 내에서 상보적으로 구성되도록 자동 배치합니다.")

    if not st.session_state.students:
        st.warning("먼저 데이터를 입력하거나 샘플 데이터를 생성해주세요.")
        st.stop()

    students = st.session_state.students
    n = len(students)

    col1, col2 = st.columns([1, 3])
    with col1:
        group_size = st.selectbox("모둠 인원", [3, 4, 5], index=1)
        n_groups   = n // group_size
        remainder  = n % group_size
        st.metric("예상 모둠 수", f"{n_groups}개")
        if remainder:
            st.caption(f"※ {remainder}명은 기존 모둠에 분산 배치")

    if st.button("🔀 모둠 구성 생성", type="primary"):
        nums = sorted(students.keys())
        random.shuffle(nums)

        # VARK·Holland 다양성 우선 배치
        vark_buckets = {v: [] for v in VARK_TYPES}
        for num in nums:
            vark_buckets[students[num]["vark"]].append(num)

        groups = [[] for _ in range(n_groups)]
        assigned = set()

        # 1라운드: VARK 다양성 보장
        for v_type in VARK_TYPES:
            bucket = vark_buckets[v_type][:]
            for i, g in enumerate(groups):
                if bucket and i < n_groups:
                    g.append(bucket.pop(0))
                    assigned.add(g[-1])

        # 2라운드: 나머지 배치
        remaining = [n for n in nums if n not in assigned]
        for num in remaining:
            min_group = min(range(n_groups), key=lambda i: len(groups[i]))
            groups[min_group].append(num)

        st.session_state["groups"] = groups

    if "groups" in st.session_state:
        groups = st.session_state["groups"]
        st.markdown('<div class="section-title">추천 모둠 구성</div>',
                    unsafe_allow_html=True)

        for gi, group in enumerate(groups):
            with st.expander(f"모둠 {gi+1}  ({len(group)}명)", expanded=gi < 3):
                cols = st.columns(len(group))
                for ci, num in enumerate(group):
                    s = students[num]
                    weak = get_weak_areas(s["diag"])
                    with cols[ci]:
                        st.markdown(f"""
                        <div class="metric-card" style="text-align:center">
                          <div style="font-size:1.3rem;font-weight:700;color:#1565C0">{num}번</div>
                          <span class="tag tag-blue">{s['vark']}</span><br>
                          <span class="tag tag-green">{s['holland']}</span><br>
                          <span class="tag {'tag-red' if s['sel']['자기조절']=='지원 필요' else 'tag-gray'}">
                            자기조절 {s['sel']['자기조절']}
                          </span>
                          <div style="font-size:0.78rem;color:#888;margin-top:6px">
                            취약영역 {len(weak)}개
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                # VARK 다양성 점수
                vark_set = set(students[n]["vark"] for n in group)
                diversity = len(vark_set)
                bar = "🟦" * diversity + "⬜" * (4 - diversity)
                st.caption(f"VARK 다양성: {bar}  ({diversity}/4 유형)")

        st.markdown('<div class="warn-box">⚠ 이 구성은 검사 데이터 기반 초안입니다. '
                    '교우 관계·특수 요구·가정 상황을 반드시 교사가 직접 검토·수정하세요.</div>',
                    unsafe_allow_html=True)

# ───────────────────────────────────────────────
# 페이지 5: 수업 설계 제안
# ───────────────────────────────────────────────
elif page == "📐 수업 설계 제안":
    st.title("📐 수업 설계 제안")
    st.caption("학생 데이터를 기반으로 HEAL 4단계 수업 설계의 주요 결정을 지원합니다.")

    if not st.session_state.students:
        st.warning("먼저 데이터를 입력하거나 샘플 데이터를 생성해주세요.")
        st.stop()

    students = st.session_state.students
    n = len(students)

    tab1, tab2, tab3 = st.tabs(["핵심 질문 개인화", "수행 과제 다양화", "루브릭 설계 원칙"])

    # ─ Tab1: 핵심 질문
    with tab1:
        st.markdown('<div class="section-title">Holland 유형별 핵심 질문 배분</div>',
                    unsafe_allow_html=True)
        for htype in HOLLAND_TYPES:
            members = [num for num, s in students.items() if s["holland"] == htype]
            if not members:
                continue
            st.markdown(f"""
            <div class="metric-card">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                  <span style="font-weight:600;color:#1565C0">{htype}</span>
                  <span style="color:#888;font-size:0.85rem;margin-left:8px">{len(members)}명</span>
                </div>
                <div>{" ".join([f'<span class="tag tag-blue">{m}번</span>' for m in sorted(members)])}</div>
              </div>
              <div style="font-size:0.9rem;color:#333;margin:8px 0 4px">
                🔑 <b>핵심 질문:</b> {HOLLAND_Q[htype]}
              </div>
              <div style="font-size:0.83rem;color:#555">
                🔬 <b>심화 활동:</b> {HOLLAND_DEEP[htype]}
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ─ Tab2: 수행 과제
    with tab2:
        st.markdown('<div class="section-title">VARK 유형별 산출물 다양화 제안</div>',
                    unsafe_allow_html=True)
        task_options = {
            "시각형":    "카드뉴스 · AI 이미지 시각화 · 인포그래픽",
            "청각형":    "QR 음성 해설 · 팟캐스트 · 낭독 영상",
            "읽기쓰기형":"감상문 · 탐구 보고서 · 건의문",
            "운동감각형":"3D 전시 구성 · 에코봇 실물 제작 · 전시 설치",
        }
        for vtype in VARK_TYPES:
            members = [num for num, s in students.items() if s["vark"] == vtype]
            if not members:
                continue
            st.markdown(f"""
            <div class="metric-card">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:600;color:#1565C0">{vtype}</span>
                <div>{" ".join([f'<span class="tag tag-blue">{m}번</span>' for m in sorted(members)])}</div>
              </div>
              <div style="font-size:0.88rem;color:#333;margin-top:8px">
                📦 <b>추천 산출물:</b> {task_options[vtype]}
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="warn-box">
        ⚠ <b>평가 형평성 원칙:</b> 산출물 형태가 달라도 루브릭의 평가 항목과 기준은 동일해야 합니다.
        '핵심 아이디어 이해도'를 중심으로 평가하세요.
        </div>
        """, unsafe_allow_html=True)

    # ─ Tab3: 루브릭
    with tab3:
        st.markdown('<div class="section-title">HEAL 루브릭 4원칙</div>',
                    unsafe_allow_html=True)
        principles = [
            ("① 수치", "3개 이상(상) / 2개(중) / 1개 이하(하)",
             "학습유형별 산출물이 달라도 동일한 수치 기준 적용"),
            ("② 자율성", "스스로(상) / 모둠 공유를 통해(중) / 교사의 도움을 받아(하)",
             "SEL 자기조절 수준을 반영한 단계 설정"),
            ("③ 행동동사", "설명하고 연결하여 생성한다(상) / 설명하고 연결할 수 있다(중) / 파악하고 만들 수 있다(하)",
             "Bloom 분류학 기반 구체적 행동 기술"),
            ("④ 발달적합성", "6학년 학생이 자기평가 도구로 직접 활용 가능한 언어 수준",
             "학생이 읽고 스스로 다음 단계를 설정할 수 있어야 함"),
        ]
        st.markdown("""
        <table class="rubric-table" style="width:100%;border-collapse:collapse">
          <tr>
            <th>원칙</th><th>기준 예시</th><th>설계 의도</th>
          </tr>
        """ + "".join([f"<tr><td><b>{p}</b></td><td>{ex}</td><td style='color:#555'>{desc}</td></tr>"
                       for p, ex, desc in principles]) + "</table>",
        unsafe_allow_html=True)

        st.markdown('<div class="section-title">학습유형별 관찰 포인트</div>',
                    unsafe_allow_html=True)
        obs = {
            "탐구형(I)": "분석적 근거의 정확성과 논리적 연결",
            "예술형(A)": "표현의 완성도와 감성적 깊이",
            "사회형(S)": "협력적 기여와 공동체 관점 반영",
            "진취형(E)": "발표의 명확성과 설득력",
        }
        for htype, point in obs.items():
            members = [num for num, s in students.items() if s["holland"] == htype]
            st.markdown(
                f'<span class="tag tag-green">{htype}</span> {point} '
                f'<span style="color:#888;font-size:0.8rem">({len(members)}명)</span><br>',
                unsafe_allow_html=True
            )

# ───────────────────────────────────────────────
# 페이지 6: AI 프롬프트 생성
# ───────────────────────────────────────────────
elif page == "📋 AI 프롬프트 생성":
    st.title("📋 AI 프롬프트 생성")
    st.caption("학생 데이터를 Claude에 바로 붙여넣을 수 있는 구조화된 프롬프트로 변환합니다.")

    if not st.session_state.students:
        st.warning("먼저 데이터를 입력하거나 샘플 데이터를 생성해주세요.")
        st.stop()

    students = st.session_state.students

    prompt_type = st.selectbox("프롬프트 유형 선택", [
        "① 학급 전체 모둠 구성 요청",
        "② 특정 학생 핵심 질문 개인화",
        "③ HEAL 루브릭 초안 생성",
        "④ 개인화 피드백 프롬프트",
    ])

    if prompt_type == "① 학급 전체 모둠 구성 요청":
        group_size = st.selectbox("모둠 인원", [3, 4, 5], index=1)
        data_lines = []
        for num, s in sorted(students.items()):
            data_lines.append(
                f"  {num}번: VARK={s['vark']}, Holland={s['holland']}, "
                f"자기조절={s['sel']['자기조절']}, 관계기술={s['sel']['관계 기술']}"
            )
        prompt = f"""당신은 초등학교 담임교사를 돕는 수업 설계 전문가입니다.

아래는 우리 반 {len(students)}명의 학습자 데이터입니다 (개인정보 없음, 번호만 사용).

[학생 데이터]
{chr(10).join(data_lines)}

[요청]
위 데이터를 기반으로 {group_size}인 1모둠으로 모둠을 구성해주세요.

구성 원칙:
1. 각 모둠 내에 VARK 유형이 최대한 다양하게 포함될 것
2. 자기조절 '지원 필요' 학생은 모둠당 1명 이하로 분산할 것
3. Holland 유형도 가능한 다양하게 구성할 것

출력 형식:
- 모둠별 번호 목록
- 각 모둠의 VARK 구성 요약
- 모둠 내 예상 역할 배치 (HEAL H·E·A·L 단계 연결)

⚠ 이 결과는 초안이며, 교사가 교우 관계·특수 요구를 반드시 검토 후 확정합니다."""

    elif prompt_type == "② 특정 학생 핵심 질문 개인화":
        stu_num = st.selectbox("학생 선택", sorted(students.keys()),
                               format_func=lambda x: f"{x}번")
        s = students[stu_num]
        weak  = get_weak_areas(s["diag"])
        t_obs = s.get("teacher_obs", {})
        s_obs = s.get("student_obs", {})

        obs_section = ""
        if t_obs:
            obs_section += f"""
[교사 관찰지 — 첫 2주]
- 집중 지속 시간: {t_obs.get('t_focus','')}
- 몰입 활동 유형: {', '.join(t_obs.get('t_engage',[]))}
- 모둠 역할: {t_obs.get('t_group','')}
- 학습유형 검사 일치도: {t_obs.get('t_vark_match','')}
- 수업 설계 메모: {t_obs.get('t_memo','')}"""
        if s_obs:
            obs_section += f"""
[학생 자기관찰지 — 첫 2주]
- 집중이 잘 되는 순간: {s_obs.get('s_focus','')}
- 요즘 가장 궁금한 것: {s_obs.get('s_curious','')}
- 나에게 자연이란: {s_obs.get('s_nature','')}
- 수업에 바라는 점: {s_obs.get('s_wish','')}"""

        prompt = f"""당신은 초등 6학년 HEAL 프로젝트(어부사시사 × 생태시민성) 수업 설계 전문가입니다.

[학생 프로파일] (번호: {stu_num}번, 개인정보 없음)
- 학습유형(VARK): {s['vark']} — {VARK_DESC[s['vark']]}
- 진로유형(Holland): {s['holland']}
- 자기조절: {s['sel']['자기조절']} / 관계 기술: {s['sel']['관계 기술']}
- 취약 내용영역: {', '.join(weak) if weak else '없음'}
{obs_section}

[요청]
위 학생의 특성에 맞는 HEAL 핵심 질문 3가지를 생성해주세요.

조건:
1. Holland 유형({s['holland']})의 관심과 강점을 반영할 것
2. VARK 유형({s['vark']})에 맞는 탐구 방식으로 접근 가능할 것
{'3. 학생 관심사("' + s_obs.get("s_curious","") + '")와 자연관("' + s_obs.get("s_nature","") + '")을 핵심 질문에 연결할 것' if s_obs.get("s_curious") or s_obs.get("s_nature") else "3. '생태시민성'이라는 공통 핵심 아이디어에 도달할 수 있는 질문일 것"}
4. 초등 6학년 수준의 언어로 작성할 것
5. 힌트 형식으로 (정답을 직접 제시하지 말 것)

출력 형식:
- 핵심 질문 3가지 (각각 한 문장)
- 각 질문과 연결되는 HEAL 단계 (H/E/A/L)
- 교사 활용 팁 1줄"""

    elif prompt_type == "③ HEAL 루브릭 초안 생성":
        subj = st.selectbox("교과", list(SUBJECT_AREAS.keys()))
        unit = st.text_input("단원명", placeholder="예: 분수의 나눗셈")
        prompt = f"""당신은 초등 6학년 과정중심평가 루브릭 설계 전문가입니다.

[요청]
{subj} - {unit if unit else '(단원명 입력)'} 단원의 HEAL 프로젝트 연계 루브릭을 작성해주세요.

[우리 반 학생 구성]
- VARK 유형: {dict(pd.Series([s['vark'] for s in students.values()]).value_counts())}
- Holland 유형: {dict(pd.Series([s['holland'] for s in students.values()]).value_counts())}

[HEAL 루브릭 4원칙 적용]
① 수치: 상/중/하 기준에 구체적 숫자 포함 (예: 3개 이상 / 2개 / 1개 이하)
② 자율성: 상=스스로 / 중=모둠 공유를 통해 / 하=교사의 도움을 받아
③ 행동동사: Bloom 분류학 기반 구체적 동사 사용
④ 발달적합성: 6학년 학생이 자기평가 도구로 직접 활용 가능한 언어

[출력 형식]
평가 항목 3가지 × 상/중/하 3단계 루브릭 표
+ 학습유형별 관찰 포인트 (VARK 4유형)
+ 교사 체크리스트 3가지"""

    else:  # 피드백 프롬프트
        stu_num = st.selectbox("학생 선택", sorted(students.keys()),
                               format_func=lambda x: f"{x}번")
        s = students[stu_num]
        t_obs = s.get("teacher_obs", {})
        s_obs = s.get("student_obs", {})
        work_type = st.text_input("피드백 대상 산출물",
                                  placeholder="예: 시조 초고, 탄소중립 건의문")

        obs_context = ""
        if t_obs.get("t_feedback"):
            obs_context += f"\n- 평소 피드백 반응: {t_obs['t_feedback']}"
        if t_obs.get("t_frustrate"):
            obs_context += f"\n- 좌절 상황 행동 패턴: {t_obs['t_frustrate']}"
        if s_obs.get("s_stuck"):
            obs_context += f"\n- 잘 안 풀릴 때 학생 행동: {s_obs['s_stuck']}"
        if s_obs.get("s_goal"):
            obs_context += f"\n- 학생 올해 목표: {s_obs['s_goal']}"

        prompt = f"""당신은 초등 6학년 HEAL 프로젝트 수업의 피드백 전문가입니다.

[학생 프로파일] (번호: {stu_num}번)
- 학습유형: {s['vark']} ({VARK_DESC[s['vark']]})
- 진로유형: {s['holland']}
- 자기조절: {s['sel']['자기조절']}
- 반 분위기 느낌(학생 자기보고): {s_obs.get('s_mood','미입력')}{obs_context}

[피드백 대상] {work_type if work_type else '(산출물 입력)'}

[피드백 원칙]
1. 힌트 형식으로 제공할 것 (정답을 직접 알려주지 말 것)
2. {s['vark']} 학습유형에 맞는 피드백 채널 사용
   - 시각형: 도표·이미지 중심 / 청각형: 음성 코멘트 중심
   - 읽기쓰기형: 서술 피드백 / 운동감각형: 수정 체험 기회 제공
3. {s['holland']} 진로유형의 강점을 살리는 방향으로 격려
4. {'자기조절 지원이 필요한 학생이므로 한 가지 수정 포인트만 제시할 것' if s['sel']['자기조절']=='지원 필요' else '학생이 스스로 다음 단계를 설정할 수 있도록 자기조절을 촉진할 것'}
5. 따뜻하고 구체적인 언어 사용

[요청]
위 학생의 {work_type if work_type else '산출물'}에 대한 교사 피드백 코멘트를 3~5문장으로 작성해주세요.
마지막 문장은 다음 단계로 나아갈 수 있는 질문으로 끝내주세요."""

    st.markdown('<div class="section-title">생성된 프롬프트</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="prompt-box">{prompt}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 프롬프트 다운로드",
            data=prompt,
            file_name=f"heal_prompt_{prompt_type[:2]}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        st.info("💡 위 텍스트를 복사해서 Claude에 붙여넣으세요.")

    st.markdown("""
    <div class="warn-box">
    ⚠ <b>개인정보 원칙:</b> 이 프롬프트에는 학생 이름·학교명이 포함되지 않습니다.
    Claude 사용 시 개인 식별 정보를 절대 추가하지 마세요. (UNESCO·GDPR 원칙)
    </div>
    """, unsafe_allow_html=True)
