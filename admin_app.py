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
    except Exception:
        return None

df = load_data(csv_url)

# 3. 디자인 수정
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    .print-area { font-family: 'Noto Sans KR', sans-serif; width: 100%; }
    .main-table { width: 100%; border-collapse: collapse; table-layout: fixed; border: 1px solid #333; }
    .main-table th, .main-table td { border: 1px solid #aaa; padding: 12px; vertical-align: top; word-break: break-all; line-height: 1.6; }
    .main-table th { background-color: #e8f0f2 !important; font-weight: bold; text-align: center; border-bottom: 2px solid #333; }
    
    /* 너비 설정: 개념(6) : 문제(4) 비율 반영 (54%:36%:10%) */
    .col-concept { width: 54%; }
    .col-problem { width: 36%; font-size: 0.9em; } /* 개념 대비 90% 크기 */
    .col-info { width: 10%; text-align: center; }

    .category-title { font-weight: bold; display: block; margin-bottom: 8px; font-size: 1.1em; color: #000; }
    .ans-text { margin-top: 15px; display: block; font-weight: bold; }

    /* 셀 내부 마크다운 표 스타일 */
    .main-table td table { border-collapse: collapse; width: 100% !important; margin: 5px 0; }
    .main-table td table td, .main-table td table th { border: 1px solid #ddd !important; padding: 4px !important; }

    @media print {
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; }
        .main-table { page-break-inside: auto; }
        tr { page-break-inside: avoid; page-break-after: auto; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    # 4. HTML 표 생성 (들여쓰기 오류 방지를 위해 왼쪽 정렬 조립)
    table_html = '<div class="print-area"><table class="main-table">'
    table_html += '<thead><tr><th class="col-concept">개념</th><th class="col-problem">문제</th><th class="col-info">출제</th></tr></thead><tbody>'

    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept = str(row.get('개념', '')).strip().replace('\n', '<br>')
        prob = str(row.get('문제', '')).strip().replace('\n', '<br>')
        ans = str(row.get('정답', '')).strip().replace('\n', '<br>')
        info = str(row.get('출제', '')).strip().replace('\n', '<br>')

        if not cat and not concept: continue

        # f-string 내부의 들여쓰기를 모두 제거하여 텍스트 노출 오류 방지
        row_html = (
            "<tr>"
            f'<td class="col-concept"><span class="category-title">{cat}</span>{concept}</td>'
            f'<td class="col-problem">{prob}<span class="ans-text">정답:<br>{ans}</span></td>'
            f'<td class="col-info">{info}</td>'
            "</tr>"
        )
        table_html += row_html

    table_html += '</tbody></table></div>'

    # 렌더링
    st.markdown(table_html, unsafe_allow_html=True)
