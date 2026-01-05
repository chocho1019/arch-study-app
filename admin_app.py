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

df = load_data(url=csv_url)

# 3. 디자인 및 인쇄 설정 (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    /* 기본 폰트 설정 */
    body, [data-testid="stAppViewContainer"] { font-family: 'Noto Sans KR', sans-serif; }

    /* 테이블 구조 */
    .print-table {
        width: 100%;
        border-collapse: collapse;
        display: table;
    }

    /* 헤더 반복 설정 (인쇄 시 핵심) */
    thead { display: table-header-group; }
    tfoot { display: table-footer-group; }

    /* 셀 스타일 */
    .print-table th, .print-table td {
        border: 1px solid #aaa;
        padding: 12px;
        vertical-align: top;
        overflow-wrap: break-word;
    }

    /* 헤더 배경 및 텍스트 */
    .print-table th {
        background-color: #e8f0f2 !important;
        font-weight: bold;
        text-align: center;
        border-top: 2px solid #333;
    }

    /* 너비 비율 설정 */
    .col-concept { width: 54%; }
    .col-problem { width: 36%; font-size: 0.95em; }
    .col-info { 
        width: 10%; 
        text-align: center; 
        font-size: 0.8em; /* 개념 대비 0.8배 */
        color: #888;      /* 연한 회색 */
    }

    /* 내부 요소 스타일 */
    .category-title { font-weight: bold; font-size: 1.1em; border-bottom: 1px solid #eee; margin-bottom: 8px; display: block; color: #000; }
    .ans-label { font-weight: bold; color: #333; margin-top: 10px; display: block; }

    /* 마크다운 표 내부 스타일 */
    .print-table td table { border-collapse: collapse; width: 100% !important; margin: 5px 0; }
    .print-table td table td { border: 1px solid #ccc !important; padding: 4px !important; }

    @media print {
        /* 불필요한 Streamlit UI 숨기기 */
        header, footer, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        
        /* 테이블 인쇄 최적화 */
        .print-table { border: 1px solid #aaa; }
        tr { page-break-inside: avoid; } /* 행 중간에 페이지 잘림 방지 */
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 요약 노트")

if df is not None:
    if st.button("🖨️ 전체 PDF로 저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    # 4. HTML 테이블 생성 (마크다운 지원을 위해 내용을 미리 변환하지 않고 구조만 생성)
    # Streamlit은 st.markdown 내부에 HTML table 태그를 넣으면 마크다운 렌더링을 지원합니다.
    
    table_content = ""
    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept = str(row.get('개념', '')).strip().replace('\n', '<br>')
        prob = str(row.get('문제', '')).strip().replace('\n', '<br>')
        ans = str(row.get('정답', '')).strip().replace('\n', '<br>')
        info = str(row.get('출제', '')).strip()

        if not cat and not concept: continue

        table_content += f"""
        <tr>
            <td class="col-concept">
                <span class="category-title">{cat}</span>
                <div>{concept}</div>
            </td>
            <td class="col-problem">
                <div>{prob}</div>
                <span class="ans-label">정답:</span>
                <div>{ans}</div>
            </td>
            <td class="col-info">
                <div style="margin-top:10px;">{info}</div>
            </td>
        </tr>
        """

    # 전체 테이블 조립 (<thead> 태그가 인쇄 시 반복을 결정합니다)
    full_table_html = f"""
    <table class="print-table">
        <thead>
            <tr>
                <th class="col-concept">개념</th>
                <th class="col-problem">문제</th>
                <th class="col-info">출제</th>
            </tr>
        </thead>
        <tbody>
            {table_content}
        </tbody>
    </table>
    """

    st.markdown(full_table_html, unsafe_allow_html=True)
