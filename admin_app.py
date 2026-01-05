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

# 3. 디자인 수정 (인쇄 최적화 및 표 스타일)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    .print-area { font-family: 'Noto Sans KR', sans-serif; }
    
    /* 헤더 스타일 */
    .header-box {
        background-color: #e8f0f2;
        font-weight: bold;
        text-align: center;
        border-top: 2px solid #333;
        border-bottom: 1px solid #aaa;
        padding: 10px 0;
        margin-bottom: 10px;
    }
    
    /* 셀 내부 마크다운 표 스타일 강제 적용 */
    table { border-collapse: collapse; width: 100% !important; margin: 5px 0; }
    th, td { border: 1px solid #ddd !important; padding: 8px !important; font-size: 13px; }
    th { background-color: #f9f9f9; }

    /* 정답 텍스트 강조 */
    .ans-text {
        margin-top: 15px;
        display: block;
    }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; }
        .stMarkdown { page-break-inside: avoid; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    # 헤더 출력 (너비 비율 4.5 : 4.5 : 1)
    h_col1, h_col2, h_col3 = st.columns([4.5, 4.5, 1])
    with h_col1: st.markdown('<div class="header-box">개념</div>', unsafe_allow_html=True)
    with h_col2: st.markdown('<div class="header-box">문제 및 정답</div>', unsafe_allow_html=True)
    with h_col3: st.markdown('<div class="header-box">출제</div>', unsafe_allow_html=True)

    # 데이터 행 출력
    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept = str(row.get('개념', '')).strip()
        problem = str(row.get('문제', '')).strip()
        answer = str(row.get('정답', '')).strip()
        info = str(row.get('출제', '')).strip()

        if not cat and not concept: continue

        # 행 시작 (1대1 비율 조정을 위해 4.5, 4.5, 1 할당)
        col1, col2, col3 = st.columns([4.5, 4.5, 1])

        with col1:
            st.markdown(f"**{cat}**")
            # unsafe_allow_html=True를 통해 마크다운 안의 <br> 작동
            st.markdown(concept, unsafe_allow_html=True)
            
        with col2:
            st.markdown(problem, unsafe_allow_html=True)
            # 파란 배경 제거 및 단순 텍스트 출력
            st.markdown(f"<span class='ans-text'>**정답:**<br>{answer}</span>", unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"<div style='text-align:center;'>{info}</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 10px 0; border: 0.5px solid #eee;'>", unsafe_allow_html=True) # 행 구분선
