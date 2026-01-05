import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components

# 페이지 설정 (넓게 보기)
st.set_page_config(layout="wide")

# 1. CSS 설정 (이미지 1번처럼 표 디자인 + 인쇄 최적화)
st.markdown("""
    <style>
    /* 화면에 보이는 표 스타일 */
    .report-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Malgun Gothic', sans-serif;
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
    
    /* 인쇄 시 설정 */
    @media print {
        .no-print { display: none !important; } /* 버튼 등 숨기기 */
        header, footer { visibility: hidden; }
        .report-table { border: 2px solid #000 !important; }
        th { background-color: #e0e0e0 !important; -webkit-print-color-adjust: exact; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 전자책 요약 노트 생성기 (관리자용)")

# 2. 구글 시트 연결
# 'url' 부분에 복사한 시트 주소를 넣으세요.
url = "https://docs.google.com/spreadsheets/d/1eg3TnoILIHXCzf4fPCU6uqzZssLnFS2xHO5zD7N2c0g/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

# 3. 인쇄 버튼 (화면 상단 고정)
if st.button("🖨️ PDF로 추출하기 (인쇄 창 열기)", help="브라우저 인쇄 창이 뜨면 'PDF로 저장'을 선택하세요."):
    components.html("<script>window.parent.focus(); window.parent.print();</script>", height=0)

st.markdown("---")

# 4. 이미지 1번 스타일의 HTML 표 생성
html_code = """
<table class="report-table">
    <thead>
        <tr>
            <th style="width: 15%;">개념</th>
            <th style="width: 35%;">내용 요약</th>
            <th style="width: 25%;">문제</th>
            <th style="width: 20%;">정답</th>
            <th style="width: 5%;">출제</th>
        </tr>
    </thead>
    <tbody>
"""

for i, row in df.iterrows():
    # 데이터의 줄바꿈(\n)을 HTML의 줄바꿈(<br>)으로 변경
    concept_content = str(row['개념 내용']).replace('\n', '<br>')
    answer_content = str(row['정답 및 해설']).replace('\n', '<br>')
    
    html_code += f"""
        <tr>
            <td style="font-weight:bold; text-align:center;">{row['구분(카테고리)']}</td>
            <td>{concept_content}</td>
            <td>{row['관련 문제']}</td>
            <td>{answer_content}</td>
            <td style="text-align:center; color:gray; font-size:12px;">{row['출제 정보']}</td>
        </tr>
    """

html_code += "</tbody></table>"

# 화면에 HTML 표 렌더링
st.markdown(html_code, unsafe_allow_html=True)
