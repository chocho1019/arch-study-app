import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import markdown
import re

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

st.title("📑 건축기사 요약 노트 (계층 구조 최적화)")

if df_raw is not None:
    # --- 사이드바 필터 설정 ---
    st.sidebar.header("🔍 데이터 필터")
    
    subject_list = ["전체"] + sorted(df_raw['과목'].unique().tolist()) if '과목' in df_raw.columns else ["전체"]
    selected_subject = st.sidebar.selectbox("과목 선택", subject_list)

    category_list = ["전체"] + sorted(df_raw['대카테고리'].unique().tolist()) if '대카테고리' in df_raw.columns else ["전체"]
    selected_category = st.sidebar.selectbox("대카테고리 선택", category_list)

    # 데이터 필터링
    df = df_raw.copy()
    if selected_subject != "전체":
        df = df[df['과목'] == selected_subject]
    if selected_category != "전체":
        df = df[df['대카테고리'] == selected_category]

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🖨️ PDF 인쇄/저장"):
            components.html("<script>window.parent.print();</script>", height=0)
    with col2:
        st.write(f"현재 출력 항목: **{len(df)}** 개")

    # 3. HTML/CSS 생성
    md_extensions = ['tables', 'fenced_code', 'nl2br']
    concept_list_html = ""
    problem_list_html = ""
    
    current_sub_category = ""

    for _, row in df.iterrows():
        cat = str(row.get('구분', '')).strip()
        concept_raw = str(row.get('개념', '')).strip()
        problem_raw = str(row.get('문제', '')).strip()
        answer_raw = str(row.get('정답', '')).strip()
        info = str(row.get('출제', '')).strip()

        # [지능형 구분 로직] 
        # 1. "1. 제목" 형태를 찾아서 소카테고리로 저장
        if re.match(r'^\d+\.', cat):
            current_sub_category = cat
            # 만약 이 행에 개념/내용이 아예 없다면 제목 전용 행으로 간주하고 넘어감
            if not concept_raw and not problem_raw:
                continue
        
        # 2. "1)" 형태가 나오면 저장된 소카테고리를 머리에 붙임
        display_title_html = ""
        if re.match(r'^\d+\)', cat) or (not cat and concept_raw):
            if current_sub_category:
                display_title_html = f'<div class="sub-category-title">{current_sub_category}</div>'
                current_sub_category = "" # 한 번 표시 후 초기화

        # 왼쪽: 개념 블록
        if cat or concept_raw:
            c_body = markdown.markdown(concept_raw, extensions=md_extensions)
            concept_list_html += f"""
            <div class="content-block">
                {display_title_html}
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

    # 4. 전체 HTML 구조 (스타일 보강)
    full_html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 0; color: #333; line-height: 1.6; }}
            .header-box {{
                display: flex; background-color: #f8f9fa;
                border-top: 2.5px solid #222; border-bottom: 1px solid #dee2e6;
                font-weight: bold; text-align: center;
                position: sticky; top: 0; z-index: 10;
            }}
            .header-box div {{ padding: 12px; }}
            .main-wrapper {{ display: flex; width: 100%; align-items: flex-start; }}
            .column {{ display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; }}
            .concept-col {{ width: 60%; border-right: 1.5px solid #eee; }}
            .problem-col {{ width: 40%; background-color: #fafafa; min-height: 100vh; }}
            
            .content-block {{
                width: 100%; margin-bottom: 30px; padding-bottom: 15px;
                border-bottom: 1px solid #f0f0f0; page-break-inside: avoid;
            }}
            
            .sub-category-title {{
                font-size: 1.2em; font-weight: 800; color: #1a365d;
                margin-bottom: 12px; padding: 6px 12px;
                background-color: #ebf8ff; border-left: 5px solid #3182ce;
            }}

            .category-title {{ font-weight: 700; font-size: 1.05em; color: #2d3748; margin-bottom: 8px; }}
            .info-tag {{ color: #a0aec0; font-weight: bold; font-size: 0.8em; margin-bottom: 8px; }}
            .ans-label {{ font-weight: bold; color: #e53e3e; margin-top: 12px; font-size: 0.9em; }}
            
            table {{ border-collapse: collapse; width: 100%; margin: 12px 0; border: 1px solid #e2e8f0; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 10px; font-size: 0.9em; text-align: left; }}
            th {{ background-color: #f7fafc; font-weight: bold; }}

            @media print {{
                .header-box {{ position: static; }}
                .problem-col {{ background-color: white !important; -webkit-print-color-adjust: exact; }}
                .sub-category-title {{ background-color: #f0f7ff !important; border-left: 5px solid #3182ce !important; }}
            }}
        </style>
    </head>
    <body>
        <div class="header-box">
            <div style="width: 60%; border-right: 1.5px solid #eee;">개념 요약</div>
            <div style="width: 40%;">관련 문제 및 정답</div>
        </div>
        <div class="main-wrapper">
            <div class="column concept-col">{concept_list_html}</div>
            <div class="column problem-col">{problem_list_html}</div>
        </div>
    </body>
    </html>
    """

    iframe_height = max(1500, len(df) * 180) 
    components.html(full_html_page, height=iframe_height, scrolling=True)
else:
    st.error("데이터를 불러오지 못했습니다.")
