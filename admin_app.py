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
    except Exception as e:
        return None

df = load_data(csv_url)

# 3. 인쇄 최적화 스타일 (메인 영역에 직접 주입)
# @media print 설정을 통해 인쇄 시 스트림릿 버튼이나 헤더를 숨깁니다.
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    .print-area { font-family: 'Noto Sans KR', sans-serif; }
    .report-table { width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }
    .report-table th, .report-table td { border: 1px solid #aaa; padding: 10px; vertical-align: top; line-height: 1.5; word-wrap: break-word; }
    .report-table th { background-color: #e8f0f2 !important; font-weight: bold; text-align: center; }
    .category-title { font-weight: bold; display: block; margin-bottom: 5px; font-size: 14px; color: #000; }
    
    .col-1 { width: 25%; }
    .col-2 { width: 35%; }
    .col-3 { width: 30%; }
    .col-4 { width: 10%; text-align: center; }

    @media print {
        /* 인쇄 시 스트림릿의 기본 UI 요소들을 모두 숨김 */
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] {
            display: none !important;
        }
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        .report-table {
            page-break-inside: auto;
        }
        tr {
            page-break-inside: avoid;
            page-break-after: auto;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 전자책 요약 노트 (관리자용)")

if df is not None:
    # 인쇄 버튼
    if st.button("🖨️ 전체 PDF로 저장하기"):
        # 부모 창 전체를 인쇄하도록 명령
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    # 4. HTML 표 조립 (들여쓰기 없이 조립)
    table_rows = ""
    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept = str(row.get('개념', '')).strip().replace('\n', '<br>')
        prob = str(row.get('문제', '')).strip().replace('\n', '<br>')
        ans = str(row.get('정답', '')).strip().replace('\n', '<br>')
        info = str(row.get('출제', '')).strip().replace('\n', '<br>')

        if not cat and not concept: continue

        # f-string의 공백 문제를 방지하기 위해 각 줄을 결합
        row_html = (
            "<tr>"
            f'<td class="col-1"><span class="category-title">{cat}</span>{concept}</td>'
            f'<td class="col-2">{prob}</td>'
            f'<td class="col-3">{ans}</td>'
            f'<td class="col-4">{info}</td>'
            "</tr>"
        )
        table_rows += row_html

    full_table_html = (
        '<div class="print-area">'
        '<table class="report-table">'
        '<thead><tr>'
        '<th class="col-1">개념</th><th class="col-2">문제</th>'
        '<th class="col-3">정답</th><th class="col-4">출제</th>'
        '</tr></thead>'
        f'<tbody>{table_rows}</tbody>'
        '</table>'
        '</div>'
    )

    # 5. st.markdown을 통해 메인 영역에 직접 렌더링
    st.markdown(full_table_html, unsafe_allow_html=True)
