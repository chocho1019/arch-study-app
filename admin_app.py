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
        # 사진에 확인된 컬럼명: 구분, 개념, 문제, 정답, 출제
        df = pd.read_csv(url)
        return df.fillna("")
    except Exception:
        return None

df = load_data(csv_url)

# 3. 디자인 수정 (내장 마크다운 표가 잘 보이도록 조정)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    .print-area { font-family: 'Noto Sans KR', sans-serif; }
    
    /* 전체 표 레이아웃 */
    .custom-row {
        display: flex;
        border-bottom: 1px solid #aaa;
        min-height: 100px;
    }
    .custom-cell {
        padding: 12px;
        border-left: 1px solid #aaa;
        word-break: break-all;
    }
    .header-row {
        background-color: #e8f0f2;
        font-weight: bold;
        text-align: center;
        border-top: 2px solid #333;
    }
    
    /* 너비 설정 */
    .col-1 { width: 30%; border-left: 1px solid #aaa; }
    .col-2 { width: 60%; border-left: 1px solid #aaa; }
    .col-3 { width: 10%; border-left: 1px solid #aaa; border-right: 1px solid #aaa; }

    .category-title { font-weight: bold; display: block; margin-bottom: 8px; font-size: 15px; color: #000; }
    .ans-box { 
        margin-top: 10px; 
        padding: 10px; 
        background-color: #f8f9fa; 
        border-left: 4px solid #007bff;
        font-weight: bold;
    }

    /* 셀 내부 마크다운 표 스타일 강제 적용 */
    table { border-collapse: collapse; width: 100% !important; margin: 5px 0; }
    th, td { border: 1px solid #ddd !important; padding: 4px !important; }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    # 헤더 출력
    st.markdown("""
        <div class="custom-row header-row">
            <div class="custom-cell col-1">개념</div>
            <div class="custom-cell col-2">문제 및 정답</div>
            <div class="custom-cell col-3">출제</div>
        </div>
    """, unsafe_allow_html=True)

    # 데이터 행 출력
    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept = str(row.get('개념', '')).strip()
        problem = str(row.get('문제', '')).strip()
        answer = str(row.get('정답', '')).strip()
        info = str(row.get('출제', '')).strip()

        if not cat and not concept: continue

        # 3열 구성을 컬럼 객체로 구현하여 마크다운 표가 작동하게 함
        col1, col2, col3 = st.columns([3, 6, 1])

        with col1:
            st.markdown(f"**{cat}**")
            st.markdown(concept)
        with col2:
            st.markdown(problem)
            st.info(f"**정답:** \n{answer}")
        with col3:
            st.markdown(f"<div style='text-align:center;'>{info}</div>", unsafe_allow_html=True)
        
        st.markdown("---") # 행 구분선
