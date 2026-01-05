import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import markdown
import re

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

# 3. 디자인 및 인쇄 설정 (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    body, [data-testid="stAppViewContainer"] { font-family: 'Noto Sans KR', sans-serif; }

    .print-table {
        width: 100%;
        border-collapse: collapse;
        display: table;
        table-layout: fixed;
        margin-bottom: 20px;
    }

    /* 헤더 스타일 */
    .print-table th {
        background-color: #f1f3f5 !important;
        font-weight: bold;
        text-align: center;
        border: 1px solid #aaa;
        padding: 6px 10px;
        height: 35px;
    }

    .print-table td {
        border: 1px solid #aaa;
        padding: 10px;
        vertical-align: top;
        overflow-wrap: break-word;
    }

    /* --- 대카테고리: 진한 회색 배경, 흰색 글씨 --- */
    .row-main-cat {
        background-color: #343a40 !important; /* 더 진한 회색 */
        color: #ffffff !important;
        text-align: left;
    }
    .row-main-cat td {
        padding: 12px 15px !important;
        font-size: 1.25em !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        border: 1px solid #212529 !important;
    }

    /* --- 소카테고리: 연한 회색 배경, 파란색 포인트 --- */
    .row-sub-cat {
        background-color: #e9ecef !important;
        color: #212529 !important;
        text-align: left;
    }
    .row-sub-cat td {
        padding: 10px 20px !important;
        font-size: 1.1em !important;
        font-weight: 600 !important;
        border: 1px solid #dee2e6 !important;
        border-left: 5px solid #495057 !important; /* 좌측 포인트 선 */
    }

    /* 일반 데이터 스타일 */
    .col-concept { width: 60%; }
    .col-problem { width: 40%; font-size: 0.95em; line-height: 1.6; }

    .category-title { font-weight: bold; font-size: 1.1em; color: #000; margin-bottom: 8px; display: block; }
    .info-tag { color: #868e96; font-weight: bold; font-size: 0.85em; margin-bottom: 8px; display: block; }
    .ans-label { font-weight: bold; color: #d9480f; margin-top: 12px; display: block; }

    /* 내부 표(Markdown Table) 스타일 */
    .print-table td table { border-collapse: collapse; width: 100% !important; margin: 8px 0; }
    .print-table td table td, .print-table td table th { 
        border: 1px solid #dee2e6 !important; 
        padding: 5px !important; 
        font-size: 0.9em; 
        text-align: center !important; 
    }
    .print-table td table th { background-color: #f8f9fa !important; }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        tr { page-break-inside: avoid; }
        .row-main-cat { -webkit-print-color-adjust: exact; background-color: #343a40 !important; color: white !important; }
        .row-sub-cat { -webkit-print-color-adjust: exact; background-color: #e9ecef !important; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    table_content = ""
    md_extensions = ['tables', 'fenced_code', 'nl2br']

    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept_raw = str(row.get('개념', '')).strip()
        problem_raw = str(row.get('문제', '')).strip()
        
        # --- 카테고리 판별 로직 강화 ---
        # 1. 대카테고리 (I. , II. 등 로마자로 시작)
        if re.match(r'^[IVX]+\.', cat):
            table_content += f'<tr class="row-main-cat"><td colspan="2">{cat}</td></tr>'
            # 대카테고리이면서 내용이 있는 경우를 위해 아래쪽을 skip하지 않고 처리하려면 조건을 조정해야 함.
            # 여기서는 카테고리 전
