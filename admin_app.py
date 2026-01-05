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

st.title("📑 건축기사 요약 노트 (소카테고리 동기화 모드)")

if df is not None:
    if st.button("🖨️ PDF 인쇄/저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    # 3. 데이터 가공 (pk를 기준으로 그룹화 아이디 생성)
    def extract_sub_cat_id(pk):
        parts = str(pk).split('-')
        if len(parts) >= 3:
            return "-".join(parts[:3]) # A-02-01 형태 추출
        return "ETC"

    df['sub_cat_id'] = df['pk'].apply(extract_sub_cat_id)
    
    # HTML 생성을 위한 변수
    md_extensions = ['tables', 'fenced_code', 'nl2br']
    sections_html = ""

    # 소카테고리 ID 그룹별로 반복
    for sub_id, group in df.groupby('sub_cat_id', sort=False):
        group_concept_html = ""
        group_problem_html = ""
        
        # 그룹 내에서 데이터 추출
        for _, row in group.iterrows():
            sub_cat_name = str(row.get('소카테고리', '')).strip()
            cat = str(row.get('구분', '')).strip()
            concept_raw = str(row.get('개념', '')).strip()
            problem_raw = str(row.get('문제', '')).strip()
            answer_raw = str(row.get('정답', '')).strip()
            info = str(row.get('출제', '')).strip()
            
            # 숫자 가공
            raw_num = row.get('숫자', '')
            try:
                num_val = str(int(float(raw_num))) if str(raw_num).strip() and str(raw_num) != "nan" else str(raw_num).strip()
            except:
                num_val = str(raw_num).strip()
            num_display = f"{num_val})" if num_val and ')' not in num_val else (f"{num_val}" if num_val else "")

            # 왼쪽: 개념 블록 생성
            if cat or concept_raw:
                c_body = markdown.markdown(concept_raw, extensions=md_extensions)
                # 숫자 1일 때만 소카테고리 헤더 표시
                sub_cat_header = f'<div class="sub-cat-box">{sub_cat_name}</div>' if num_val == "1" and sub_cat_name else ""
                
                group_concept_html += f"""
                <div class="content-block">
                    {sub_cat_header}
                    <div class="category-title">{num_display} {cat}</div>
                    <div class="concept-body">{c_body}</div>
                </div>
                """

            # 오른쪽: 문제 블록 생성
            if problem_raw:
                p_body = markdown.markdown(problem_raw, extensions=md_extensions)
                a_body = markdown.markdown(answer_raw, extensions=md_extensions)
                info_tag = f'<div class="info-tag">[{info} 출제]</div>' if info else ""
                group_problem_html += f"""
                <div class="content-block" style="font-size: 0.9em;">
                    {info_tag}
                    <div class="problem-body">{p_body}</div>
                    <div class="ans-label">정답:</div>
                    <div class="answer-body">{a_body}</div>
                </div>
                """

        # 한 소카테고리 그룹을 하나의 행(row)으로 묶어서 추가
        sections_html += f"""
        <div class="sub-section">
            <div class="column concept-col">{group_concept_html}</div>
            <div class="column problem-col">{group_problem_html}</div>
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
            .header-box div {{ padding: 10px; box-sizing: border-box; }}
            
            /* 소카테고리별 섹션 묶음 */
            .sub-section {{ 
                display: flex; 
                width: 100%; 
                border-bottom: 2px solid #444; /* 소카테고리 구분선 */
                page-break-inside: auto;
            }}
            
            .column {{ display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; }}
            .concept-col {{ width: 60%; border-right: 1px solid #aaa; }}
            .problem-col {{ width: 40%; background-color: #fcfcfc; }}
            
            .content-block {{ 
                width: 100%; margin-bottom: 20px; padding-bottom: 10px; 
                border-bottom: 1px dashed #ddd; page-break-inside: avoid; 
            }}
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
                .sub-section {{ page-break-after: auto; }}
                .problem-col {{ background-color: white !important; -webkit-print-color-adjust: exact; }}
            }}
        </style>
    </head>
    <body>
        <div class="header-box">
            <div style="width: 60%; border-right: 1px solid #aaa;">개념 요약</div>
            <div style="width: 40%;">관련 문제 및 정답</div>
        </div>
        <div class="main-container">
            {sections_html}
        </div>
    </body>
    </html>
    """

    iframe_height = max(2000, len(df) * 180)
    components.html(full_html_page, height=iframe_height, scrolling=True)
else:
    st.error("데이터를 불러오지 못했습니다.")
