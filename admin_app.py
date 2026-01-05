import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import markdown  # 마크다운 변환 라이브러리 추가

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

# 3. 디자인 (표 내부의 표 스타일 추가)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    .print-area { font-family: 'Noto Sans KR', sans-serif; }
    .report-table { width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }
    .report-table th, .report-table td { border: 1px solid #aaa; padding: 12px; vertical-align: top; line-height: 1.6; word-break: break-word; }
    
    .report-table th { background-color: #e8f0f2 !important; font-weight: bold; text-align: center; color: #333; }
    
    /* 셀 내부 마크다운 표(Nested Table) 스타일 */
    .report-table td table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        background-color: #fcfcfc;
    }
    .report-table td table th, .report-table td table td {
        border: 1px solid #ddd !important;
        padding: 6px !important;
        font-size: 12px;
    }

    .col-concept { width: 35%; }
    .col-combined { width: 55%; }
    .col-info    { width: 10%; text-align: center; }

    .category-title { font-weight: bold; display: block; margin-bottom: 8px; font-size: 15px; color: #000; border-bottom: 2px solid #e8f0f2; padding-bottom: 4px; }
    .answer-text { font-weight: bold; color: #000; display: block; margin-top: 10px; padding: 5px; background-color: #f0f7f9; border-left: 3px solid #007bff; }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        .report-table { page-break-inside: auto; }
        tr { page-break-inside: avoid; page-break-after: auto; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    table_rows = ""
    # 마크다운 변환 옵션 설정 (표 문법 활성화)
    md_configs = ['extra', 'nl2br']

    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        
        # [수정] 단순 replace 대신 markdown 라이브러리로 변환
        concept_raw = str(row.get('개념', '')).strip()
        concept_html = markdown.markdown(concept_raw, extensions=md_configs)
        
        prob_raw = str(row.get('문제', '')).strip()
        prob_html = markdown.markdown(prob_raw, extensions=md_configs)
        
        ans_raw = str(row.get('정답', '')).strip()
        ans_html = markdown.markdown(ans_raw, extensions=md_configs)
        
        info = str(row.get('출제', '')).strip()

        if not cat and not concept_raw: continue

        # 문제와 정답 합치기 (정답은 강조 스타일 적용)
        combined_problem_html = f"{prob_html}<div class='answer-text'>{ans_html}</div>"

        row_html = (
            "<tr>"
            f'<td class="col-concept"><span class="category-title">{cat}</span>{concept_html}</td>'
            f'<td class="col-combined">{combined_problem_html}</td>'
            f'<td class="col-info">{info}</td>'
            "</tr>"
        )
        table_rows += row_html

    full_table_html = (
        '<div class="print-area">'
        '<table class="report-table">'
        '<thead><tr>'
        '<th class="col-concept">개념</th>'
        '<th class="col-combined">문제 및 정답</th>'
        '<th class="col-info">출제</th>'
        '</tr></thead>'
        f'<tbody>{table_rows}</tbody>'
        '</table>'
        '</div>'
    )

    st.markdown(full_table_html, unsafe_allow_html=True)
