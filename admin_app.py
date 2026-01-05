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

df = load_data(csv_url)

st.title("📑 건축기사 요약 노트 (소카테고리 분리 모드)")

if df is not None:
    if st.button("🖨️ PDF 인쇄/저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    # 3. HTML/CSS 통합 생성
    md_extensions = ['tables', 'fenced_code', 'nl2br']
    concept_list_html = ""
    problem_list_html = ""

    for _, row in df.iterrows():
        # 데이터 추출
        sub_cat = str(row.get('소카테고리', '')).strip()
        num_val_raw = str(row.get('숫자', '')).strip()
        cat = str(row.get('구분', '')).strip()
        concept_raw = str(row.get('개념', '')).strip()
        problem_raw = str(row.get('문제', '')).strip()
        answer_raw = str(row.get('정답', '')).strip()
        info = str(row.get('출제', '')).strip()

        # --- [오류 수정 지점] 들여쓰기 정렬 시작 ---
        raw_num = row.get('숫자', '')
        try:
            # 데이터가 숫자라면 정수로 변환하여 .0 제거
            num_val = str(int(float(raw_num))) if str(raw_num).strip() and str(raw_num) != "nan" else str(raw_num).strip()
        except:
            num_val = str(raw_num).strip()

        if num_val and num_val != "nan":
            # 숫자 뒤에 )를 붙여줍니다.
            num_display = f"{num_val})" if ')' not in num_val else num_val
        else:
            num_display = ""
        # --- [오류 수정 지점] 들여쓰기 정렬 끝 ---

        # 왼쪽: 개념 블록
        if cat or concept_raw:
            c_body = markdown.markdown(concept_raw, extensions=md_extensions)
            sub_cat_html = f'<div class="sub-cat-box">{sub_cat}</div>' if sub_cat else ""
            
            concept_list_html += f"""
            <div class="content-block">
                {sub_cat_html}
                <div class="concept-row">
                    <div class="category-title">{num_display} {cat}</div>
                    <div class="concept-body">{c_body}</div>
                </div>
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
    full_html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 0; color: #333; }}
            .header-box {{
                display: flex; background-color: #f1f3f5;
                border-top: 2px solid #333; border-bottom: 1px solid #aaa;
                font-weight: bold; text-align: center;
                position: sticky; top: 0; z-index: 10;
            }}
            .header-box div {{ padding: 10px; }}
            .main-wrapper {{ display: flex; width: 100%; align-items: flex-start; }}
            .column {{ display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; }}
            .concept-col {{ width: 60%; border-right: 1px solid #aaa; }}
            .problem-col {{ width: 40%; background-color: #fcfcfc; min-height: 100vh; }}
            .content-block {{ width: 100%; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px dashed #ddd; page-break-inside: avoid; }}
            .sub-cat-box {{
                display: inline-block; background-color: #2D3748; color: white;
                padding: 2px 8px; font-size: 0.85em; border-radius: 4px;
                margin-bottom: 8px; font-weight: bold;
            }}
            .category-title {{ font-weight: bold; font-size: 1.1em; color: #000; margin-bottom: 5px; }}
            .concept-body {{ padding-left: 5px; }}
            .info-tag {{ color: #718096; font-weight: bold; font-size: 0.85em; margin-bottom: 5px; }}
            .ans-label {{ font-weight: bold; color: #e53e3e; margin-top: 10px; font-size: 0.9em; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #cbd5e0; padding: 8px; font-size: 0.9em; text-align: center; }}
            th {{ background-color: #edf2f7; }}
            @media print {{
                .header-box {{ position: static; }}
                .sub-cat-box {{ background-color: #333 !important; color: white !important; -webkit-print-color-adjust: exact; }}
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

    iframe_height = max(2000, len(df) * 150)
    components.html(full_html_page, height=iframe_height, scrolling=True)
else:
    st.error("데이터를 불러오지 못했습니다.")
