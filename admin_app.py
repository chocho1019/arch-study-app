import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import markdown  # 내부 마크다운 변환을 위해 필요합니다.

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
        table-layout: fixed; /* 너비 고정을 위해 추가 */
    }

    thead { display: table-header-group; } /* 인쇄 시 헤더 반복 */

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

    /* 비율 설정 및 글씨 크기 조정 */
    .col-concept { width: 54%; }
    .col-problem { width: 36%; font-size: 0.9em; } /* 개념 대비 90% */
    .col-info { 
        width: 10%; 
        text-align: center; 
        font-size: 0.8em; /* 개념 대비 0.8배 */
        color: #888;      /* 연한 회색 */
    }

    .category-title { font-weight: bold; font-size: 1.1em; border-bottom: 1px solid #eee; margin-bottom: 8px; display: block; color: #000; }
    .ans-label { font-weight: bold; color: #333; margin-top: 10px; display: block; }

    /* 마크다운 표 내부 스타일 강제 적용 */
    .print-table td table { border-collapse: collapse; width: 100% !important; margin: 5px 0; border: 1px solid #ddd; }
    .print-table td table td, .print-table td table th { border: 1px solid #ddd !important; padding: 4px !important; font-size: 12px; }

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

    # 4. HTML 테이블 생성
    # 들여쓰기로 인한 코드블록 오작동을 막기 위해 문자열을 왼쪽으로 붙여서 생성합니다.
    table_content = ""
    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        # 셀 내부 마크다운 문법을 HTML로 미리 변환합니다.
        concept_html = markdown.markdown(str(row.get('개념', '')).strip())
        prob_html = markdown.markdown(str(row.get('문제', '')).strip())
        ans_html = markdown.markdown(str(row.get('정답', '')).strip())
        info = str(row.get('출제', '')).strip()

        if not cat and not concept_html: continue

        # 들여쓰기를 제거한 한 줄 형태로 조립
        row_html = f'<tr><td class="col-concept"><span class="category-title">{cat}</span>{concept_html}</td>'
        row_html += f'<td class="col-problem">{prob_html}<span class="ans-label">정답:</span>{ans_html}</td>'
        row_html += f'<td class="col-info"><div style="margin-top:10px;">{info}</div></td></tr>'
        table_content += row_html

    full_table_html = (
        f'<table class="print-table">'
        f'<thead><tr><th class="col-concept">개념</th><th class="col-problem">문제</th><th class="col-info">출제</th></tr></thead>'
        f'<tbody>{table_content}</tbody></table>'
    )

    # 최종 렌더링
    st.write(full_table_html, unsafe_allow_html=True)
