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

    /* 1. 헤더 높이 축소 (패딩 조절) */
    .print-table th {
        background-color: #e8f0f2 !important;
        font-weight: bold;
        text-align: center;
        border-top: 2px solid #333;
        padding: 4px 10px; /* 기존 10px에서 대폭 축소 */
        height: 30px;      /* 최소 높이 지정 */
    }

    /* 2. 열 비율 재설정 (개념 60% : 문제 40%) */
    .col-concept { width: 60%; }
    .col-problem { width: 40%; font-size: 0.9em; }

    .category-title { font-weight: bold; font-size: 1.1em; border-bottom: 1px solid #eee; margin-bottom: 8px; display: block; color: #000; }
    
    /* 문제 셀 내부 출제 정보 스타일 */
    .info-tag { 
        display: inline-block;
        color: #888;
        font-weight: bold;
        font-size: 0.85em;
        margin-bottom: 5px;
    }
    
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
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    # 4. HTML 테이블 생성 로직
    table_content = ""
    md_extensions = ['tables', 'fenced_code', 'nl2br']

    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept_html = markdown.markdown(str(row.get('개념', '')).strip(), extensions=md_extensions)
        prob_html = markdown.markdown(str(row.get('문제', '')).strip(), extensions=md_extensions)
        ans_html = markdown.markdown(str(row.get('정답', '')).strip(), extensions=md_extensions)
        info = str(row.get('출제', '')).strip()

        if not cat and not concept_html: continue

        # 출제 정보가 있을 경우 [정보 출제] 형태로 생성
        info_display = f'<span class="info-tag">[{info} 출제]</span><br>' if info else ""

        row_html = (
            f'<tr>'
            f'<td class="col-concept"><span class="category-title">{cat}</span>{concept_html}</td>'
            f'<td class="col-problem">'
            f'{info_display}{prob_html}'
            f'<span class="ans-label">정답:</span>{ans_html}'
            f'</td>'
            f'</tr>'
        )
        table_content += row_html

    full_table_html = (
        f'<table class="print-table">'
        f'<thead><tr><th class="col-concept">개념</th><th class="col-problem">문제</th></tr></thead>'
        f'<tbody>{table_content}</tbody></table>'
    )

    st.markdown(full_table_html, unsafe_allow_html=True)
else:
    st.error("데이터를 불러오지 못했습니다. Google Sheets URL을 확인해주세요.")
