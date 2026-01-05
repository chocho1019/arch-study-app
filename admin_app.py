import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(layout="wide", page_title="전자책 요약 노트 생성기")

# 1. 디자인 (인쇄 최적화 및 CSS)
st.markdown("""
    <style>
    /* 화면 표시용 스타일 */
    .print-container {
        padding: 20px;
        background-color: white;
    }
    .report-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Malgun Gothic', sans-serif;
    }
    .report-table th, .report-table td {
        border: 1px solid #000;
        padding: 12px;
        vertical-align: top;
        line-height: 1.6;
        word-break: break-all;
    }
    .report-table th {
        background-color: #f2f2f2 !important;
        font-weight: bold;
        text-align: center;
    }
    .concept-cell {
        background-color: #f9f9f9 !important;
        font-weight: bold;
        text-align: center;
        width: 20%;
    }
    
    /* 인쇄 시 불필요한 요소 제거 */
    @media print {
        header, footer, .no-print, [data-testid="stSidebar"], [data-testid="stHeader"] {
            display: none !important;
        }
        .main .block-container {
            padding: 0 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 전자책 요약 노트 생성기 (관리자용)")

# 2. 데이터 로드
SPREADSHEET_ID = "1eg3TnoILIHXCzf4fPCU6uqzZssLnFS2xHO5zD7N2c0g"
GID = "397904038" # '테스트용' 탭의 GID
csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data
def load_data(url):
    return pd.read_csv(url, encoding='utf-8')

try:
    df = load_data(csv_url)

    # 3. 인쇄 버튼
    if st.button("🖨️ PDF로 추출하기 (인쇄 창 열기)"):
        components.html("<script>window.parent.focus(); window.parent.print();</script>", height=0)

    st.markdown("---")

    # 4. HTML 표 생성 (안정적인 렌더링을 위해 f-string 조립)
    table_rows = ""
    for i, row in df.iterrows():
        # 시트의 실제 헤더 이름을 확인하여 매칭하세요. 
        # 현재는 '개념'과 '내용' 컬럼을 기준으로 작성되었습니다.
        concept = str(row.get('개념', '')).strip() if pd.notna(row.get('개념')) else ""
        content = str(row.get('내용', '')).strip() if pd.notna(row.get('내용')) else ""
        
        if not concept and not content:
            continue

        # 줄바꿈 처리
        content_html = content.replace('\n', '<br>')

        table_rows += f"""
            <tr>
                <td class="concept-cell">{concept}</td>
                <td>{content_html}</td>
            </tr>
        """

    # 전체 테이블 조립
    full_html = f"""
    <div class="print-container">
        <table class="report-table">
            <thead>
                <tr>
                    <th>개념</th>
                    <th>내용 요약</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    """
    
    # unsafe_allow_html을 통해 테이블 렌더링
    st.write(full_html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"데이터 로드 중 오류 발생: {e}")
