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
        df.columns = [col.strip() for col in df.columns]
        return df.fillna("")
    except Exception:
        return None

df = load_data(csv_url)

st.title("건축기사 요약 노트 (계층 디자인 모드)")

if df is not None:
    if st.button("🖨️ PDF 인쇄/저장하기"):
        components.html("<script>window.parent.print();</script>", height=0)

    # pk 열 이름 찾기
    pk_col = next((c for c in df.columns if c.lower() == 'pk'), None)
    
    if pk_col is None:
        st.error(f"시트에서 'pk' 열을 찾을 수 없습니다.")
        st.stop()

    def extract_sub_cat_id(pk_val):
        parts = str(pk_val).split('-')
        if len(parts) >= 3:
            return "-".join(parts[:3])
        return "ETC"

    df['sub_cat_id'] = df[pk_col].apply(extract_sub_cat_id)
    
    md_extensions = ['tables', 'fenced_code', 'nl2br']
    sections_html = ""

    # 소카테고리 ID 그룹별로 반복
    for sub_id, group in df.groupby('sub_cat_id', sort=False):
        group_concept_html = ""
        group_problem_html = ""
        
        # 그룹의 첫 번째 행에서 카테고리 명칭 추출
        first_row = group.iloc[0]
        main_cat = str(first_row.get('대카테고리', '')).strip()
        sub_cat = str(first_row.get('소카테고리', '')).strip()
        category_title = f"{main_cat} / {sub_cat}" if main_cat else sub_cat

        for _, row in group.iterrows():
            cat = str(row.get('구분', '')).strip()
            concept_raw = str(row.get('개념', '')).strip()
            problem_raw = str(row.get('문제', '')).strip()
            answer_raw = str(row.get('정답', '')).strip()
            info = str(row.get('출제', '')).strip()
            
            raw_num = row.get('숫자', '')
            try:
                num_val = str(int(float(raw_num))) if str(raw_num).strip() and str(raw_num) != "nan" else str(raw_num).strip()
            except:
                num_val = str(raw_num).strip()
            num_display = f"{num_val}." if num_val else ""

            # 왼쪽: 개념 블록
            if cat or concept_raw:
                c_body = markdown.markdown(concept_raw, extensions=md_extensions)
                group_concept_html += f"""
                <div class="content-block">
                    <div class="category-title">{num_display} {cat}</div>
                    <div class="concept-body">{c_body}</div>
                </div>
                """

            # 오른쪽: 문제 블록
            if problem_raw:
                p_body = markdown.markdown(problem_raw, extensions=md_extensions)
                a_body = markdown.markdown(answer_raw, extensions=md_extensions)
                info_tag = f'<div class="info-tag">[{info} 출제]</div>' if info else ""
                group_problem_html += f"""
                <div class="content-block problem-block">
                    {info_tag}
                    <div class="problem-body">{p_body}</div>
                    <div class="ans-label">정답</div>
                    <div class="answer-body">{a_body}</div>
                </div>
                """

        # 전체 섹션 구성 (헤더 + 내용)
        sections_html += f"""
        <div class="section-container">
            <div class="section-header">{category_title}</div>
            <div class="sub-section">
                <div class="column concept-col">{group_concept_html}</div>
                <div class="column problem-col">{group_problem_html}</div>
            </div>
        </div>
        """

    full_html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 0; color: #333; line-height: 1.6; }}
            
            /* 상단 헤더 */
            .header-box {{
                display: flex; background-color: #f8f9fa;
                border-top: 3px solid #2D3748; border-bottom: 1px solid #dee2e6;
                font-weight: bold; text-align: center;
                position: sticky; top: 0; z-index: 100;
            }}
            .header-box div {{ padding: 12px; box-sizing: border-box; }}

            /* 섹션 전체 구조 */
            .section-container {{ margin-bottom: 40px; }}
            
            /* 소카테고리 헤더 (대카 / 소카) */
            .section-header {{
                width: 100%; background-color: #edf2f7;
                padding: 8px 20px; font-weight: bold; font-size: 0.95em;
                color: #2d3748; border-left: 5px solid #2d3748;
                box-sizing: border-box; margin-top: 20px;
            }}

            .sub-section {{ display: flex; width: 100%; page-break-inside: auto; }}
            
            /* 컬럼 설정 */
            .column {{ display: flex; flex-direction: column; padding: 20px; box-sizing: border-box; }}
            .concept-col {{ width: 60%; border-right: 1px solid #edf2f7; padding-left: 30px; }} /* 들여쓰기 효과 */
            .problem-col {{ width: 40%; background-color: #fcfcfc; padding-left: 25px; }}
            
            /* 개별 콘텐츠 블록 */
            .content-block {{ width: 100%; margin-bottom: 25px; page-break-inside: avoid; }}
            .category-title {{ font-weight: bold; font-size: 1.15em; color: #1a202c; margin-bottom: 8px; }}
            .concept-body {{ color: #4a5568; font-size: 0.98em; }}
            
            /* 문제 영역 스타일 */
            .problem-block {{ font-size: 0.92em; border-bottom: 1px dashed #e2e8f0; padding-bottom: 15px; }}
            .info-tag {{ color: #a0aec0; font-weight: bold; font-size: 0.85em; margin-bottom: 6px; }}
            .ans-label {{ 
                display: inline-block; background-color: #fff5f5; color: #c53030; 
                padding: 1px 6px; border-radius: 3px; font-weight: bold; 
                font-size: 0.8em; margin-top: 12px; margin-bottom: 4px;
                border: 1px solid #feb2b2;
            }}
            .answer-body {{ color: #2d3748; padding-left: 2px; }}

            /* 테이블 디자인 개선 */
            table {{ border-collapse: collapse; width: 100%; margin: 12px 0; border-top: 2px solid #cbd5e0; }}
            th, td {{ border-bottom: 1px solid #e2e8f0; padding: 10px 8px; font-size: 0.9em; text-align: center; }}
            th {{ background-color: #f7fafc; color: #4a5568; font-weight: bold; }}
            tr:last-child td {{ border-bottom: 2px solid #cbd5e0; }}

            @media print {{
                .header-box {{ position: static; }}
                .section-header {{ background-color: #edf2f7 !important; -webkit-print-color-adjust: exact; }}
                .problem-col {{ background-color: white !important; }}
                .ans-label {{ border: 1px solid #c53030 !important; }}
            }}
        </style>
    </head>
    <body>
        <div class="header-box">
            <div style="width: 60%; border-right: 1px solid #dee2e6;">개념 요약</div>
            <div style="width: 40%;">관련 문제 및 정답</div>
        </div>
        <div class="main-container">
            {sections_html}
        </div>
    </body>
    </html>
    """

    iframe_height = max(2000, len(df) * 200)
    components.html(full_html_page, height=iframe_height, scrolling=True)
else:
    st.error("데이터를 불러오지 못했습니다.")
