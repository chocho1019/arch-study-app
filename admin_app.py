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

# 3. 디자인 및 인쇄 설정 (CSS 기반 단 나누기)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    body, [data-testid="stAppViewContainer"] { font-family: 'Noto Sans KR', sans-serif; }

    /* 전체 컨테이너를 2단으로 나눔 */
    .note-container {
        column-count: 2;
        column-gap: 30px;
        column-rule: 1px solid #aaa; /* 중앙 구분선 */
        width: 100%;
    }

    /* 각 아이템이 단 중간에서 잘리지 않도록 설정 */
    .content-block {
        break-inside: avoid;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #eee;
    }

    /* 개념 열과 문제 열 헤더 스타일 */
    .column-header {
        column-span: all; /* 헤더는 단을 가로지름 */
        display: flex;
        background-color: #e8f0f2;
        border: 1px solid #aaa;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .header-concept { width: 60%; border-right: 1px solid #aaa; padding: 8px; }
    .header-problem { width: 40%; padding: 8px; }

    /* 내부 스타일 */
    .category-title { font-weight: bold; font-size: 1.1em; color: #000; margin-bottom: 5px; display: block; }
    .info-tag { color: #888; font-weight: bold; font-size: 0.85em; }
    .ans-label { font-weight: bold; color: #333; margin-top: 8px; display: block; }
    
    /* 마크다운 표 스타일 */
    table { border-collapse: collapse; width: 100% !important; margin: 5px 0; border: 1px solid #ddd; }
    td, th { border: 1px solid #ddd !important; padding: 4px !important; font-size: 12px; text-align: center !important; }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        .note-container { column-fill: auto; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트 (단나누기 모드)")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    md_extensions = ['tables', 'fenced_code', 'nl2br']

    # 4. 데이터 분리 (개념 리스트와 문제 리스트를 별도로 생성)
    concepts_html = ""
    problems_html = ""

    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept = str(row.get('개념', '')).strip()
        problem = str(row.get('문제', '')).strip()
        answer = str(row.get('정답', '')).strip()
        info = str(row.get('출제', '')).strip()

        # 개념 블록 생성
        if cat or concept:
            c_html = markdown.markdown(concept, extensions=md_extensions)
            concepts_html += f"""
            <div class="content-block">
                <span class="category-title">{cat}</span>
                {c_html}
            </div>
            """

        # 문제 블록 생성
        if problem:
            p_html = markdown.markdown(problem, extensions=md_extensions)
            a_html = markdown.markdown(answer, extensions=md_extensions)
            info_tag = f'<span class="info-tag">[{info} 출제]</span><br>' if info else ""
            problems_html += f"""
            <div class="content-block" style="font-size: 0.9em;">
                {info_tag}
                {p_html}
                <span class="ans-label">정답:</span>
                {a_html}
            </div>
            """

    # 5. 최종 레이아웃 렌더링
    # 헤더 부분
    st.markdown(f"""
        <div class="column-header">
            <div class="header-concept">개념</div>
            <div class="header-problem">문제 및 정답</div>
        </div>
    """, unsafe_allow_html=True)

    # 본문 부분 (CSS column-count 이용)
    # 한글 단나누기처럼 왼쪽(개념)이 다 채워지면 오른쪽(문제)으로 넘어가는 구조입니다.
    # 만약 '왼쪽은 무조건 개념만, 오른쪽은 무조건 문제만' 나오게 하고 싶다면 
    # 아래의 note-container 방식을 유지하되 데이터를 조절해야 합니다.
    
    # [방안 A] 왼쪽 단에 개념만 몰아넣고, 오른쪽 단에 문제만 몰아넣는 구조
    st.markdown(f"""
        <div class="note-container">
            <div class="concepts-side">
                {concepts_html}
            </div>
            <div style="break-before: column;"></div> <div class="problems-side">
                {problems_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

else:
    st.error("데이터를 불러오지 못했습니다. Google Sheets URL을 확인해주세요.")
