import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 페이지 설정 (반드시 맨 처음에 위치)
st.set_page_config(layout="wide", page_title="건축기사 요약 노트 생성기")

# 1. 디자인 (인쇄 최적화 및 CSS - 사진 2의 스타일 반영)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');

    /* 화면 표시용 스타일 */
    .print-container {
        padding: 10px;
        background-color: white;
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .report-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        color: #333;
    }
    
    .report-table th, .report-table td {
        border: 1px solid #ccc; /* 회색 테두리 */
        padding: 10px;
        vertical-align: top;
        line-height: 1.6;
        word-break: break-word; /* 긴 단어 줄바꿈 */
    }

    /* 헤더 스타일 (사진 2와 유사한 푸른색) */
    .report-table th {
        background-color: #e8f0f2 !important; 
        font-weight: bold;
        text-align: center;
        color: #333;
        border-bottom: 2px solid #aaa;
    }

    /* 컬럼별 너비 조정 (반응형 대응) */
    .col-concept { width: 30%; }
    .col-problem { width: 30%; }
    .col-answer  { width: 30%; }
    .col-info    { width: 10%; text-align: center; }

    /* 개념(카테고리) 강조 스타일 */
    .category-title {
        font-weight: 700;
        display: block;
        margin-bottom: 8px;
        color: #000;
    }

    /* 인쇄 시 불필요한 요소 제거 */
    @media print {
        @page {
            margin: 1cm;
            size: A4 landscape; /* 가로 방향 인쇄 추천 */
        }
        header, footer, .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], .stButton {
            display: none !important;
        }
        .main .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        .print-container {
            padding: 0;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📑 건축기사 전자책 요약 노트 (관리자용)")

# 2. 데이터 로드
# 주의: 구글 시트는 '웹에 게시' 상태이거나 링크가 공개되어 있어야 합니다.
SPREADSHEET_ID = "1eg3TnoILIHXCzf4fPCU6uqzZssLnFS2xHO5zD7N2c0g"
GID = "397904038"
csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=600) # 10분마다 캐시 갱신
def load_data(url):
    try:
        df = pd.read_csv(url)
        # 결측치(NaN)를 빈 문자열로 변환하여 에러 방지
        return df.fillna("")
    except Exception as e:
        return None

df = load_data(csv_url)

if df is None:
    st.error("데이터를 불러오는 데 실패했습니다. 구글 시트 권한이나 URL을 확인해주세요.")
else:
    # 3. 인쇄 버튼 (화면 상단 배치)
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🖨️ PDF로 저장 (인쇄창 열기)"):
            js = "<script>window.print();</script>"
            components.html(js, height=0, width=0)
    
    st.markdown("---")

    # 4. HTML 표 조립
    # 구글 시트의 실제 컬럼명: '구분(카테고리)', '개념 내용', '관련 문제', '정답 및 해설', '출제 정보'
    
    table_rows = ""
    
    for i, row in df.iterrows():
        # 데이터 추출 (컬럼명 공백 주의)
        category = str(row['구분(카테고리)']).strip()
        concept_content = str(row['개념 내용']).strip()
        problem = str(row['관련 문제']).strip()
        answer = str(row['정답 및 해설']).strip()
        info = str(row['출제 정보']).strip()

        # 데이터가 아예 없는 빈 행은 스킵
        if not category and not concept_content:
            continue

        # 줄바꿈 처리 (\n -> <br>)
        concept_html = concept_content.replace('\n', '<br>')
        problem_html = problem.replace('\n', '<br>')
        answer_html = answer.replace('\n', '<br>')
        info_html = info.replace('\n', '<br>')

        # 목표 이미지(사진 2)처럼 '개념' 칸에 [카테고리]와 [내용]을 합침
        full_concept_cell = f"""
            <span class="category-title">{category}</span>
            <span>{concept_html}</span>
        """

        table_rows += f"""
            <tr>
                <td class="col-concept">{full_concept_cell}</td>
                <td class="col-problem">{problem_html}</td>
                <td class="col-answer">{answer_html}</td>
                <td class="col-info">{info_html}</td>
            </tr>
        """

    # 전체 HTML 구조
    full_html = f"""
    <div class="print-container">
        <table class="report-table">
            <thead>
                <tr>
                    <th class="col-concept">개념</th>
                    <th class="col-problem">문제</th>
                    <th class="col-answer">정답</th>
                    <th class="col-info">출제</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    """
    
    # 5. 화면 렌더링
    st.markdown(full_html, unsafe_allow_html=True)
