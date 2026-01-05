import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(layout="wide", page_title="전자책 요약 노트 생성기")

# 1. 디자인 (인쇄 및 화면용 CSS)
st.markdown("""
    <style>
    .report-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Malgun Gothic', sans-serif;
        margin-top: 20px;
    }
    .report-table th, .report-table td {
        border: 1px solid #d3d3d3;
        padding: 12px;
        vertical-align: top;
        line-height: 1.6;
    }
    .report-table th {
        background-color: #f2f2f2;
        font-weight: bold;
        text-align: center;
    }
    @media print {
        .no-print { display: none !important; }
        header, footer, [data-testid="stSidebar"], [data-testid="stHeader"] { display: none !important; }
        .report-table { border: 2px solid #000 !important; }
        th { background-color: #e0e0e0 !important; -webkit-print-color-adjust: exact; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 전자책 요약 노트 생성기 (관리자용)")

# --------------------------------------------------
# 2. 데이터 로드 (ASCII 오류 해결을 위한 Pandas 방식)
# --------------------------------------------------
# 주소창의 gid 번호를 확인하여 입력하세요.
SPREADSHEET_ID = "1eg3TnoILIHXCzf4fPCU6uqzZssLnFS2xHO5zD7N2c0g"
GID = "397904038"  # '테스트용' 또는 '계획 최종' 탭의 GID
csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data
def load_data(url):
    # 인코딩을 utf-8로 지정하여 한글 깨짐 방지
    return pd.read_csv(url, encoding='utf-8')

try:
    df = load_data(csv_url)

    # 3. 인쇄 버튼 (들여쓰기 수정 완료)
    if st.button("🖨️ PDF로 추출하기 (인쇄 창 열기)"):
        components.html("<script>window.parent.focus(); window.parent.print();</script>", height=0)

    st.markdown("---")

    # 4. HTML 표 생성
    html_code = """
    <table class="report-table">
        <thead>
            <tr>
                <th style="width: 15%;">개념</th>
                <th style="width: 85%;">내용 요약</th>
            </tr>
        </thead>
        <tbody>
    """

    for i, row in df.iterrows():
        # 컬럼명은 실제 시트의 헤더와 일치해야 합니다 (개념, 내용)
        concept = str(row.get('개념 내용', '')).strip() if pd.notna(row.get('개념 내용')) else ""
        content = str(row.get('관련 문제', '')).strip() if pd.notna(row.get('관련 문제')) else ""
        
        # 줄바꿈 및 특수문자 처리
        content_html = content.replace('\n', '<br>').replace('|', '').replace('---', '')

        if concept or content:
            html_code += f"""
                <tr>
                    <td style="font-weight:bold; text-align:center; background-color:#f9f9f9;">{concept}</td>
                    <td>{content_html}</td>
                </tr>
            """

    html_code += "</tbody></table>"
    st.markdown(html_code, unsafe_allow_html=True)

except Exception as e:
    st.error(f"데이터 로드 중 오류 발생: {e}")
    st.info("시트의 GID 번호가 정확한지 확인해 주세요.")
