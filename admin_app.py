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
    }

    thead { display: table-header-group; } 

    .print-table th, .print-table td {
        border: 1px solid #aaa;
        padding: 10px;
        vertical-align: top;
        overflow-wrap: break-word;
    }

    .print-table th {
        background-color: #e8f0f2 !important;
        font-weight: bold;
        text-align: center;
        border-top: 2px solid #333;
    }

    /* 비율 및 글씨 크기 설정: 출제 칸 너비를 10%에서 30% 축소한 7%로 설정 */
    .col-concept { width: 57%; }
    .col-problem { width: 36%; font-size: 0.9em; }
    .col-info { 
        width: 7%; 
        text-align: center; 
        font-size: 0.8em; 
        color: #888;
    }

    .category-title { font-weight: bold; font-size: 1.1em; border-bottom: 1px solid #eee; margin-bottom: 8px; display: block; color: #000; }
    .ans-label { font-weight: bold; color: #333; margin-top: 10px; display: block; }

    /* 마크다운 표 내부 스타일: 배경색 흰색 및 가운데 정렬 */
    .print-table td table { border-collapse: collapse; width: 100% !important; margin: 5px 0; border: 1px solid #ddd; }
    .print-table td table td, .print-table td table th { 
        border: 1px solid #ddd !important; 
        padding: 4px !important; 
        font-size: 12px; 
        background-color: #ffffff !important; /* 내부 표 배경 흰색 */
        text-align: center !important;         /* 내부 표 내용 가운데 정렬 */
    }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        tr { page-break-inside: avoid; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0
