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
        # 최신 사진의 컬럼명 적용: 구분, 개념, 문제, 정답, 출제
        df = pd.read_csv(url)
        return df.fillna("")
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None

df = load_data(csv_url)

# 3. 화면 UI
st.title("📑 건축기사 전자책 요약 노트 (관리자용)")

if df is not None:
    # 인쇄 버튼
    if st.button("🖨️ PDF로 저장 (인쇄창 열기)"):
        components.html("<script>window.parent.print();</script>", height=0)

    st.markdown("---")

    # 4. HTML/CSS 조립 (st.markdown의 들여쓰기 오류를 피하기 위해 변수로 관리)
    style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        body { font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 20px; }
        .report-table { width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }
        .report-table th, .report-table td { border: 1px solid #aaa; padding: 10px; vertical-align: top; line-height: 1.5; word-wrap: break-word; }
        .report-table th { background-color: #e8f0f2; font-weight: bold; text-align: center; }
        .category-title { font-weight: bold; display: block; margin-bottom: 5px; font-size: 14px; color: #000; }
        .col-1 { width: 25%; }
        .col-2 { width: 35%; }
        .col-3 { width: 30%; }
        .col-4 { width: 10%; text-align: center; }
        @media print {
            .no-print { display: none; }
            body { padding: 0; }
        }
    </style>
    """

    table_rows = ""
    for _, row in df.iterrows():
        # 사진에 맞춰 정확한 컬럼명 매칭
        cat = str(row.get('구분', '')).strip()
        concept = str(row.get('개념', '')).strip().replace('\n', '<br>')
        prob = str(row.get('문제', '')).strip().replace('\n', '<br>')
        ans = str(row.get('정답', '')).strip().replace('\n', '<br>')
        info = str(row.get('출제', '')).strip().replace('\n', '<br>')

        if not cat and not concept: continue

        table_rows += f"""
        <tr>
            <td class="col-1"><span class="category-title">{cat}</span>{concept}</td>
            <td class="col-2">{prob}</td>
            <td class="col-3">{ans}</td>
            <td class="col-4">{info}</td>
        </tr>
        """

    # 전체 HTML 완성
    full_html = f"""
    <html>
    <head>{style}</head>
    <body>
        <table class="report-table">
            <thead>
                <tr>
                    <th class="col-1">개념</th>
                    <th class="col-2">문제</th>
                    <th class="col-3">정답</th>
                    <th class="col-4">출제</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </body>
    </html>
    """

    # 5. iframe으로 렌더링 (가장 안전한 방법)
    # 데이터 양에 따라 height를 조절하거나 스크롤이 생기게 합니다.
    components.html(full_html, height=1200, scrolling=True)
