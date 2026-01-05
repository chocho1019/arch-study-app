import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

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

# 3. 디자인 수정 (세로선 강제 적용 및 마크다운 최적화)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    /* 전체 배경 및 폰트 */
    [data-testid="stAppViewContainer"] { font-family: 'Noto Sans KR', sans-serif; }

    /* 헤더 스타일 */
    .table-header {
        display: flex;
        background-color: #e8f0f2;
        border-top: 2px solid #333;
        border-bottom: 1px solid #aaa;
        font-weight: bold;
        text-align: center;
    }

    /* 행 레이아웃 (세로선 포함) */
    .custom-row {
        display: flex;
        border-bottom: 1px solid #aaa;
        border-left: 1px solid #aaa;
        border-right: 1px solid #aaa;
    }

    /* 셀 공통 스타일 */
    .cell {
        padding: 15px;
        border-right: 1px solid #aaa;
        overflow-wrap: break-word;
    }
    .cell:last-child { border-right: none; }

    /* 너비 및 글자 크기 비율 반영 (6:4 비율 근사) */
    .col-concept { width: 54%; }
    .col-problem { width: 36%; font-size: 0.95em; } /* 문제 영역 90~95% 크기 */
    .col-info { width: 10%; text-align: center; }

    /* 내부 요소 스타일 */
    .category-title { font-weight: bold; font-size: 1.2em; border-bottom: 1px solid #eee; margin-bottom: 10px; display: block; }
    .ans-label { font-weight: bold; color: #333; margin-top: 15px; display: block; }

    /* 마크다운 표/리스트 간격 조절 */
    .cell p { margin-bottom: 5px; }
    table { border-collapse: collapse; width: 100% !important; margin: 10px 0; }
    th, td { border: 1px solid #ccc !important; padding: 6px !important; }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; }
        .custom-row { page-break-inside: avoid; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    # 헤더 출력
    st.markdown(f"""
        <div class="table-header">
            <div class="cell col-concept">개념</div>
            <div class="cell col-problem">문제</div>
            <div class="cell col-info">출제</div>
        </div>
    """, unsafe_allow_html=True)

    # 데이터 행 출력
    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept = str(row.get('개념', '')).strip()
        prob = str(row.get('문제', '')).strip()
        ans = str(row.get('정답', '')).strip()
        info = str(row.get('출제', '')).strip()

        if not cat and not concept: continue

        # 행 시작
        row_container = st.container()
        
        # st.columns를 사용하여 내부 마크다운 렌더링 기능을 살림
        # 동시에 커스텀 CSS(.custom-row 등)가 적용된 HTML 구조 안에 배치
        st.markdown('<div class="custom-row">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([5.4, 3.6, 1.0])
        
        with col1:
            # 왼쪽 세로선이 columns 구조상 사라질 수 있어 여백과 선을 조정
            st.markdown(f'<span class="category-title">{cat}</span>', unsafe_allow_html=True)
            st.markdown(concept, unsafe_allow_html=True) # 여기서 마크다운 반영됨
            
        with col2:
            st.markdown(prob, unsafe_allow_html=True)
            st.markdown('<span class="ans-label">정답:</span>', unsafe_allow_html=True)
            st.markdown(ans, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"<div style='text-align:center; padding-top:20px;'>{info}</div>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
