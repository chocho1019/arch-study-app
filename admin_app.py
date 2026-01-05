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
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    body, [data-testid="stAppViewContainer"] { 
        font-family: 'Noto Sans KR', sans-serif; 
        color: #333;
    }

    /* 전체 테이블 구조 */
    .print-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        margin-bottom: 30px;
        border: 2px solid #343a40;
    }

    .print-table th {
        background-color: #f8f9fa !important;
        font-weight: 700;
        text-align: center;
        border: 1px solid #aaa;
        padding: 10px;
        text-transform: uppercase;
        font-size: 0.9em;
    }

    .print-table td {
        border: 1px solid #aaa;
        padding: 12px;
        vertical-align: top;
        line-height: 1.5;
    }

    /* [대카테고리] 진한 회색 / 전체 너비 */
    .row-main-cat {
        background-color: #343a40 !important;
        color: #ffffff !important;
        page-break-after: avoid; /* 대카테고리 직후 페이지 잘림 방지 */
    }
    .row-main-cat td {
        padding: 15px 20px !important;
        font-size: 1.4em !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* [소카테고리] 연한 회색 / 왼쪽 포인트 바 */
    .row-sub-cat {
        background-color: #f1f3f5 !important;
        page-break-after: avoid;
    }
    .row-sub-cat td {
        padding: 10px 20px !important;
        font-size: 1.15em !important;
        font-weight: 700 !important;
        border-left: 8px solid #495057 !important; /* 좌측 강조선 */
        color: #212529 !important;
    }

    .col-concept { width: 55%; }
    .col-problem { width: 45%; background-color: #fafafa; }

    /* 내부 텍스트 스타일 */
    .category-title { 
        font-weight: 800; 
        font-size: 1.1em; 
        color: #000; 
        margin-bottom: 10px; 
        display: block;
        border-bottom: 1px solid #eee;
        padding-bottom: 4px;
    }
    .info-tag { color: #495057; font-weight: bold; font-size: 0.85em; background: #e9ecef; padding: 2px 6px; border-radius: 4px; }
    .ans-label { font-weight: bold; color: #e8590c; margin-top: 15px; display: block; border-top: 1px dashed #ddd; padding-top: 8px; }

    /* 마크다운 리스트 스타일 조정 */
    .print-table ul { padding-left: 20px; margin: 5px 0; }
    .print-table li { margin-bottom: 4px; }

    @media print {
        @page { size: A4; margin: 15mm; }
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        
        /* 인쇄 시 배경색 강제 적용 */
        .row-main-cat { -webkit-print-color-adjust: exact; background-color: #343a40 !important; color: white !important; }
        .row-sub-cat { -webkit-print-color-adjust: exact; background-color: #f1f3f5 !important; }
        .col-problem { -webkit-print-color-adjust: exact; background-color: #fafafa !important; }
        
        tr { page-break-inside: avoid; } /* 행 중간 잘림 방지 */
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트")

if df is not None:
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("🖨️ PDF 인쇄/저장"):
            components.html("<script>window.parent.print();</script>", height=0)

    table_content = ""
    md_extensions = ['tables', 'fenced_code', 'nl2br']

    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept_raw = str(row.get('개념', '')).strip()
        problem_raw = str(row.get('문제', '')).strip()
        ans_raw = str(row.get('정답', '')).strip()
        info = str(row.get('출제', '')).strip()

        # 1. 대카테고리 (I. II. III.)
        if re.match(r'^[IVX]+\.', cat) and not concept_raw and not problem_raw:
            table_content += f'<tr class="row-main-cat"><td colspan="2">{cat}</td></tr>'
            continue
            
        # 2. 소카테고리 (1. 2. 3.)
        if re.match(r'^\d+\.', cat) and not concept_raw and not problem_raw:
            table_content += f'<tr class="row-sub-cat"><td colspan="2">{cat}</td></tr>'
            continue

        # 3. 일반 데이터
        if not cat and not concept_raw:
            continue

        concept_html = markdown.markdown(concept_raw, extensions=md_extensions)
        prob_html = markdown.markdown(problem_raw, extensions=md_extensions)
        ans_html = markdown.markdown(ans_raw, extensions=md_extensions)
        info_display = f'<span class="info-tag">{info} 출제</span>' if info else ""

        row_html = (
            f'<tr>'
            f'<td class="col-concept"><span class="category-title">{cat}</span>{concept_html}</td>'
            f'<td class="col-problem">{info_display}<div style="margin-top:8px;">{prob_html}</div>'
            f'<span class="ans-label">정답 확인</span>{ans_html}</td>'
            f'</tr>'
        )
        table_content += row_html

    if table_content:
        full_table_html = (
            f'<table class="print-table">'
            f'<thead><tr><th class="col-concept">개념 및 구조적 특징</th><th class="col-problem">기출 문제 및 정답</th></tr></thead>'
            f'<tbody>{table_content}</tbody></table>'
        )
        st.markdown(full_table_html, unsafe_allow_html=True)
    else:
        st.warning("데이터가 비어있습니다.")
else:
    st.error("데이터 로드 실패")
