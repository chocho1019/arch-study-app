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
    }

    thead { display: table-header-group; } 

    .print-table th, .print-table td {
        border: 1px solid #aaa;
        padding: 10px;
        vertical-align: top;
        overflow-wrap: break-word;
    }

    /* 헤더 높이 및 스타일 */
    .print-table th {
        background-color: #e8f0f2 !important;
        font-weight: bold;
        text-align: center;
        border-top: 2px solid #333;
        padding: 4px 10px;
        height: 30px;
    }

    /* --- 카테고리 스타일 추가 --- */
    /* 대카테고리: 진한 배경, 흰색 글씨 */
    .row-main-cat {
        background-color: #4A5568 !important;
        color: white !important;
        font-size: 1.2em;
        font-weight: bold;
        text-align: center;
    }
    .row-main-cat td { border: 1px solid #2D3748 !important; padding: 8px !important; }

    /* 소카테고리: 연한 배경, 들여쓰기 효과 */
    .row-sub-cat {
        background-color: #F7FAFC !important;
        color: #2D3748 !important;
        font-weight: bold;
        font-size: 1.05em;
    }
    .row-sub-cat td { border: 1px solid #CBD5E0 !important; padding: 6px 20px !important; }

    /* 일반 데이터 행 스타일 */
    .col-concept { width: 60%; }
    .col-problem { width: 40%; font-size: 0.9em; }

    .category-title { font-weight: bold; font-size: 1.1em; border-bottom: 1px solid #eee; margin-bottom: 8px; display: block; color: #000; }
    .info-tag { display: inline-block; color: #888; font-weight: bold; font-size: 0.85em; margin-bottom: 5px; }
    .ans-label { font-weight: bold; color: #333; margin-top: 10px; display: block; }

    /* 내부 마크다운 표 스타일 */
    .print-table td table { border-collapse: collapse; width: 100% !important; margin: 5px 0; border: 1px solid #ddd; }
    .print-table td table td, .print-table td table th { 
        border: 1px solid #ddd !important; 
        padding: 4px !important; 
        font-size: 12px; 
        background-color: #ffffff !important; 
        text-align: center !important; 
    }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        tr { page-break-inside: avoid; }
        .row-main-cat { -webkit-print-color-adjust: exact; } /* 인쇄 시 배경색 유지 */
        .row-sub-cat { -webkit-print-color-adjust: exact; }
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
        
        # --- 카테고리 판별 로직 ---
        # 1. 대카테고리 (예: I. 한국건축사)
        if re.match(r'^[IVX]+\.', cat) and not concept_raw:
            table_content += f'<tr class="row-main-cat"><td colspan="2">{cat}</td></tr>'
            continue
            
        # 2. 소카테고리 (예: 1. 공포양식)
        if re.match(r'^\d+\.', cat) and not concept_raw:
            table_content += f'<tr class="row-sub-cat"><td colspan="2">{cat}</td></tr>'
            continue

        # 3. 일반 데이터 행
        concept_html = markdown.markdown(concept_raw, extensions=md_extensions)
        prob_html = markdown.markdown(str(row.get('문제', '')).strip(), extensions=md_extensions)
        ans_html = markdown.markdown(str(row.get('정답', '')).strip(), extensions=md_extensions)
        info = str(row.get('출제', '')).strip()

        if not cat and not concept_html: continue

        info_display = f'<span class="info-tag">[{info} 출제]</span><br>' if info else ""

        row_html = (
            f'<tr>'
            f'<td class="col-concept"><span class="category-title">{cat}</span>{concept_html}</td>'
            f'<td class="col-problem">{info_display}{prob_html}<span class="ans-label">정답:</span>{ans_html}</td>'
            f'</tr>'
        )
        table_content += row_html

    full_table_html = (
        f'<table class="print-table">'
        f'<thead><tr><th class="col-concept">개념</th><th class="col-problem">문제 및 정답</th></tr></thead>'
        f'<tbody>{table_content}</tbody></table>'
    )

    st.markdown(full_table_html, unsafe_allow_html=True)
else:
    st.error("데이터를 불러오지 못했습니다.")
