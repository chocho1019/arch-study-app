import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import markdown

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="건축기사 요약 노트 생성기")

# 2. 데이터 로드
SPREADSHEET_ID = "1eg3TnoILIHXCzf4fPCU6uqzZssLnFS2xHO5zD7N2c0g"
GID = "397904038"
csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        return df.fillna("")
    except Exception:
        return None

df = load_data(csv_url)

# 3. 디자인 설정 (Flexbox 기반 독립 열 구조)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    body, [data-testid="stAppViewContainer"] { font-family: 'Noto Sans KR', sans-serif; background-color: white; }

    /* 메인 컨테이너: 좌우를 나눔 */
    .main-wrapper {
        display: flex;
        width: 100%;
        min-height: 1000px;
        border-top: 2px solid #333;
    }

    /* 각 열의 공통 스타일 */
    .column {
        display: flex;
        flex-direction: column; /* 세로로 쌓임 */
        padding: 15px;
    }

    /* 개념 열 (60%) */
    .concept-col {
        width: 60%;
        border-right: 1px solid #aaa;
    }

    /* 문제 열 (40%) */
    .problem-col {
        width: 40%;
        background-color: #fcfcfc;
    }

    /* 개별 콘텐츠 블록 (빨간 선 없이 위로 밀착되는 핵심) */
    .content-block {
        width: 100%;
        margin-bottom: 20px; /* 항목 간 최소 간격 */
        padding-bottom: 15px;
        border-bottom: 1px dashed #ddd; /* 구분선 */
    }

    /* 타이틀 및 폰트 스타일 */
    .header-box {
        display: flex;
        width: 100%;
        background-color: #e8f0f2;
        border: 1px solid #aaa;
        font-weight: bold;
        text-align: center;
    }
    .header-box div { padding: 10px; }

    .category-title { font-weight: bold; font-size: 1.1em; color: #2D3748; margin-bottom: 8px; display: block; }
    .info-tag { color: #888; font-weight: bold; font-size: 0.85em; margin-bottom: 5px; display: block; }
    .ans-label { font-weight: bold; color: #d9480f; margin-top: 10px; display: block; }

    /* 마크다운 표 스타일 최적화 */
    table { border-collapse: collapse; width: 100% !important; margin: 10px 0; }
    th, td { border: 1px solid #ccc !important; padding: 6px !important; font-size: 0.85em; text-align: center !important; }
    th { background-color: #f8f9fa !important; }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        .content-block { page-break-inside: avoid; }
        .main-wrapper { border-bottom: none; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트 (좌우 독립 모드)")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    md_extensions = ['tables', 'fenced_code', 'nl2br']

    # 데이터를 좌측(개념)과 우측(문제)으로 분리하여 저장
    concept_list_html = ""
    problem_list_html = ""

    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept_raw = str(row.get('개념', '')).strip()
        problem_raw = str(row.get('문제', '')).strip()
        answer_raw = str(row.get('정답', '')).strip()
        info = str(row.get('출제', '')).strip()

        # 1. 왼쪽: 개념 블록 (구분이나 개념이 있을 때만 생성)
        if cat or concept_raw:
            c_body = markdown.markdown(concept_raw, extensions=md_extensions)
            concept_list_html += f"""
            <div class="content-block">
                <span class="category-title">{cat}</span>
                <div class="concept-body">{c_body}</div>
            </div>
            """

        # 2. 오른쪽: 문제 블록 (문제가 있을 때만 생성)
        if problem_raw:
            p_body = markdown.markdown(problem_raw, extensions=md_extensions)
            a_body = markdown.markdown(answer_raw, extensions=md_extensions)
            info_tag = f'<span class="info-tag">[{info} 출제]</span>' if info else ""
            problem_list_html += f"""
            <div class="content-block" style="font-size: 0.9em;">
                {info_tag}
                <div class="problem-body">{p_body}</div>
                <span class="ans-label">정답:</span>
                <div class="answer-body">{a_body}</div>
            </div>
            """

    # 최종 레이아웃 합치기
    full_html = f"""
    <div class="header-box">
        <div style="width: 60%; border-right: 1px solid #aaa;">개념 요약</div>
        <div style="width: 40%;">관련 문제 및 정답</div>
    </div>
    <div class="main-wrapper">
        <div class="column concept-col">
            {concept_list_html}
        </div>
        <div class="column problem-col">
            {problem_list_html}
        </div>
    </div>
    """

    st.markdown(full_html, unsafe_allow_html=True)

else:
    st.error("데이터를 불러오지 못했습니다.")
