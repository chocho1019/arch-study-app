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
        # 시트 컬럼명: 구분, 개념, 문제, 정답, 출제
        df = pd.read_csv(url)
        return df.fillna("")
    except Exception:
        return None

df = load_data(csv_url)

# 3. 디자인 (3열 구성 및 인쇄 최적화)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    .print-area { font-family: 'Noto Sans KR', sans-serif; }
    .report-table { width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }
    .report-table th, .report-table td { border: 1px solid #aaa; padding: 12px; vertical-align: top; line-height: 1.6; word-wrap: break-word; }
    
    /* 헤더 디자인 */
    .report-table th { background-color: #e8f0f2 !important; font-weight: bold; text-align: center; color: #333; }
    
    /* 열 너비 설정 (개념 30%, 문제+정답 60%, 출제 10%) */
    .col-concept { width: 30%; }
    .col-combined { width: 60%; }
    .col-info    { width: 10%; text-align: center; }

    .category-title { font-weight: bold; display: block; margin-bottom: 6px; font-size: 14px; color: #000; }
    .answer-text { font-weight: bold; color: #000; display: block; margin-top: 8px; }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] {
            display: none !important;
        }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        .report-table { page-break-inside: auto; }
        tr { page-break-inside: avoid; page-break-after: auto; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트 (문제/정답 통합 버전)")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    # 4. HTML 표 조립 (개념 - 문제+정답 - 출제)
    table_rows = ""
    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept = str(row.get('개념', '')).strip().replace('\n', '<br>')
        
        # 문제와 정답을 하나의 변수로 합치기
        raw_problem = str(row.get('문제', '')).strip().replace('\n', '<br>')
        raw_answer = str(row.get('정답', '')).strip().replace('\n', '<br>')
        
        info = str(row.get('출제', '')).strip().replace('\n', '<br>')

        if not cat and not concept: continue

        # 정답 부분은 굵게 표시 (answer-text 클래스 적용)
        combined_problem_html = f"{raw_problem}<br><span class='answer-text'>{raw_answer}</span>"

        row_html = (
            "<tr>"
            f'<td class="col-concept"><span class="category-title">{cat}</span>{concept}</td>'
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
