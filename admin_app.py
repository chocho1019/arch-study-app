import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import markdown

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="건축기사 요약 노트")

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

df_raw = load_data(csv_url)

st.title("📑 건축기사 요약 노트 (필터 및 독립 열 모드)")

if df_raw is not None:
    # --- 사이드바 필터 설정 ---
    st.sidebar.header("🔍 데이터 필터")
    
    # 과목 필터 (예: 건축계획, 건축구조 등)
    # 실제 구글 시트의 컬럼명에 맞춰 '과목' 부분을 수정하세요.
    subject_list = ["전체"] + sorted(df_raw['과목'].unique().tolist()) if '과목' in df_raw.columns else ["전체"]
    selected_subject = st.sidebar.selectbox("과목 선택", subject_list)

    # 대카테고리 필터 (예: 제1장, 한국건축사 등)
    # 실제 구글 시트의 컬럼명에 맞춰 '대카테고리' 부분을 수정하세요.
    category_list = ["전체"] + sorted(df_raw['대카테고리'].unique().tolist()) if '대카테고리' in df_raw.columns else ["전체"]
    selected_category = st.sidebar.selectbox("대카테고리 선택", category_list)

    # 데이터 필터링 적용
    df = df_raw.copy()
    if selected_subject != "전체":
        df = df[df['과목'] == selected_subject]
    if selected_category != "전체":
        df = df[df['대카테고리'] == selected_category]

    # 상단 버튼 영역
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🖨️ PDF 인쇄/저장"):
            components.html("<script>window.parent.print();</script>", height=0)
    with col2:
        st.write(f"현재 출력 항목: **{len(df)}** 개")

    # 3. HTML/CSS 통합 생성
    md_extensions = ['tables', 'fenced_code', 'nl2br']
    concept_list_html = ""
    problem_list_html = ""

    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept_raw = str(row.get('개념', '')).strip()
        problem_raw = str(row.get('문제', '')).strip()
        answer_raw = str(row.get('정답', '')).strip()
        info = str(row.get('출제', '')).strip()

        # 왼쪽: 개념 블록
        if cat or concept_raw:
            c_body = markdown.markdown(concept_raw, extensions=md_extensions)
            concept_list_html += f"""
            <div class="content-block">
                <div class="category-title">{cat}</div>
                <div class="concept-body">{c_body}</div>
            </div>
            """

        # 오른쪽: 문제 블록
        if problem_raw:
            p_body = markdown.markdown(problem_raw, extensions=md_extensions)
            a_body = markdown.markdown(answer_raw, extensions=md_extensions)
            info_tag = f'<div class="info-tag">[{info} 출제]</div>' if info else ""
            problem_list_html += f"""
            <div class="content-block" style="font-size: 0.9em;">
                {info_tag}
                <div class="problem-body">{p_body}</div>
                <div class="ans-label">정답:</div>
                <div class="answer-body">{a_body}</div>
            </div>
            """

    # 4. 전체 HTML 구조 정의
    # (내용 길이에 따라 높이가 가변적이므로 컨테이너 높이 설정을 위해 min-height 사용)
    full_html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 0; color: #333; }}
            .header-box {{
                display: flex;
                background-color: #f1f3f5;
                border-top: 2px solid #333;
                border-bottom: 1px solid #aaa;
                font-weight: bold;
                text-align: center;
                position: sticky; top: 0; z-index: 10;
            }}
            .header-box div {{ padding: 10px; }}
            .main-wrapper {{ display: flex; width: 100%; align-items: flex-start; }}
            .column {{ display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; }}
            .concept-col {{ width: 60%; border-right: 1px solid #aaa; }}
            .problem-col {{ width: 40%; background-color: #fcfcfc; min-height: 100vh; }}
            .content-block {{
                width: 100%;
                margin-bottom: 25px;
                padding-bottom: 15px;
                border-bottom: 1px dashed #ddd;
                page-break-inside: avoid;
            }}
            .category-title {{ font-weight: bold; font-size: 1.15em; color: #1a202c; margin-bottom: 10px; }}
            .info-tag {{ color: #718096; font-weight: bold; font-size: 0.85em; margin-bottom: 5px; }}
            .ans-label {{ font-weight: bold; color: #e53e3e; margin-top: 10px; font-size: 0.9em; }}
            
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #cbd5e0; padding: 8px; font-size: 0.9em; text-align: center; }}
            th {{ background-color: #edf2f7; }}

            @media print {{
                .header-box {{ position: static; }}
                .problem-col {{ background-color: white !important; -webkit-print-color-adjust: exact; }}
            }}
        </style>
    </head>
    <body>
        <div class="header-box">
            <div style="width: 60%; border-right: 1px solid #aaa;">개념 요약</div>
            <div style="width: 40%;">관련 문제 및 정답</div>
        </div>
        <div class="main-wrapper">
            <div class="column concept-col">{concept_list_html}</div>
            <div class="column problem-col">{problem_list_html}</div>
        </div>
    </body>
    </html>
    """

    # 내용의 양에 따라 height를 동적으로 조절하거나 충분히 큰 값을 줍니다.
    iframe_height = max(1000, len(df) * 150) 
    components.html(full_html_page, height=iframe_height, scrolling=True)

else:
    st.error("데이터를 불러오지 못했습니다.")
    
