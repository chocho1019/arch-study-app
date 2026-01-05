import streamlit as st
from streamlit_gsheets import GSheetsConnection
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
        header, footer, [data-testid="stSidebar"] { display: none !important; }
        .report-table { border: 2px solid #000 !important; }
        th { background-color: #e0e0e0 !important; -webkit-print-color-adjust: exact; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 전자책 요약 노트 생성기 (관리자용)")

# --------------------------------------------------
# Google Sheet 연결 (연결 안정화 버전)
# --------------------------------------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = "1eg3TnoILIHXCzf4fPCU6uqzZssLnFS2xHO5zD7N2c0g"

@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPE
    )
    return gspread.authorize(creds)

# 전역 변수로 설정
gc = get_gspread_client()

@st.cache_resource
def get_working_sheets():
    try:
        doc = gc.open_by_key(SPREADSHEET_ID)
        return doc.worksheet("users"), doc.worksheet("favorites")
    except Exception as e:
        return None, None

user_sheet, fav_sheet = get_working_sheets()



    # 3. 인쇄 버튼
    if st.button("🖨️ PDF로 추출하기 (인쇄 창 열기)"):
        components.html("<script>window.parent.focus(); window.parent.print();</script>", height=0)

    st.markdown("---")

    # 4. 시트 제목에 맞춘 HTML 표 생성
    html_code = """
    <table class="report-table">
        <thead>
            <tr>
                <th style="width: 15%;">개념</th>
                <th style="width: 35%;">내용 요약</th>
                <th style="width: 25%;">문제</th>
                <th style="width: 20%;">정답 및 해설</th>
                <th style="width: 5%;">출제</th>
            </tr>
        </thead>
        <tbody>
    """

    for i, row in df.iterrows():
        # 시트의 컬럼명을 정확히 매칭 (스크린샷 기준)
        # 데이터가 비어있을 경우를 대비해 str() 처리 및 공백 제거
        category = str(row.get('구분(카테고리)', ''))
        content  = str(row.get('개념 내용', '')).replace('\n', '<br>')
        question = str(row.get('관련 문제', ''))
        answer   = str(row.get('정답 및 해설', '')).replace('\n', '<br>')
        info     = str(row.get('출제 정보', ''))
        
        html_code += f"""
            <tr>
                <td style="font-weight:bold; text-align:center;">{category}</td>
                <td>{content}</td>
                <td>{question}</td>
                <td>{answer}</td>
                <td style="text-align:center; color:gray; font-size:12px;">{info}</td>
            </tr>
        """

    html_code += "</tbody></table>"
    st.markdown(html_code, unsafe_allow_html=True)

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.info("시트의 탭 이름이 '테스트용'이 맞는지 확인해 주세요.")
    
