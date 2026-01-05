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
        if '빈출' in df.columns:
            df['빈출'] = pd.to_numeric(df['빈출'], errors='coerce').fillna(0).astype(int)
        return df.fillna("")
    except Exception:
        return None

df_raw = load_data(csv_url)

st.title("건축기사 요약 노트 (커스텀 디자인 모드)")

if df_raw is not None:
    # --- 필터 영역 ---
    st.sidebar.header("🔍 필터 설정")
    
    subject_list = ["전체"] + sorted(list(df_raw['과목'].unique())) if '과목' in df_raw.columns else ["전체"]
    selected_subject = st.sidebar.selectbox("과목 선택", subject_list)
    
    if selected_subject != "전체":
        filtered_df = df_raw[df_raw['과목'] == selected_subject]
        main_cat_list = ["전체"] + sorted(list(filtered_df['대카테고리'].unique()))
    else:
        filtered_df = df_raw
        main_cat_list = ["전체"] + sorted(list(df_raw['대카테고리'].unique())) if '대카테고리' in df_raw.columns else ["전체"]
    
    selected_main_cat = st.sidebar.selectbox("대카테고리 선택", main_cat_list)
    
    if selected_main_cat != "전체":
        filtered_df = filtered_df[filtered_df['대카테고리'] == selected_main_cat]

    freq_filter = st.sidebar.radio("빈출도 필터", ["전체", "3회 이상 출제", "5회 이상 출제"])
    if freq_filter == "3회 이상 출제":
        filtered_df = filtered_df[filtered_df['빈출'] >= 3]
    elif freq_filter == "5회 이상 출제":
        filtered_df = filtered_df[filtered_df['빈출'] >= 5]
        
    sort_option = st.sidebar.checkbox("빈출 높은 순으로 정렬")
    if sort_option:
        filtered_df = filtered_df.sort_values(by='빈출', ascending=False)

    df = filtered_df

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

    for sub_id, group in df.groupby('sub_cat_id', sort=not sort_option):
        group_concept_html = ""
        group_problem_html = ""
        
        first_row = group.iloc[0]
        sub_cat_name = str(first_row.get('소카테고리', '')).strip()
        
        sub_num_raw = str(first_row.get('숫소', '')).strip()
        try:
            sub_num = str(int(float(sub_num_raw))) if sub_num_raw and sub_num_raw != "nan" else ""
        except:
            sub_num = sub_num_raw
            
        category_title = f"{sub_num}. {sub_cat_name}" if sub_num else sub_cat_name

        for _, row in group.iterrows():
            cat = str(row.get('구분', '')).strip()
            concept_raw = str(row.get('개념', '')).strip()
            problem_raw = str(row.get('문제', '')).strip()
            answer_raw = str(row.get('정답', '')).strip()
            info = str(row.get('출제', '')).strip()
            freq_val = row.get('빈출', 0)
            
            # 빈출 뱃지: 테두리 박스 스타일 유지
            freq_badge = f'<span style="color: #94a3b8; font-size: 0.8em; margin-left: 8px; font-weight: normal; border: 1px solid #94a3b8; padding: 1px 4px; border-radius: 3px;">{freq_val}회</span>' if freq_val > 0 else ""

            raw_num_gu = row.get('숫구', '')
            try:
                num_gu_val = str(int(float(raw_num_gu))) if str(raw_num_gu).strip() and str(raw_num_gu) != "nan" else str(raw_num_gu).strip()
            except:
                num_gu_val = str(raw_num_gu).strip()
            num_gu_display = f"{num_gu_val})" if num_gu_val else ""

            raw_num_mun = row.get('숫문', '')
            try:
                num_mun_val = str(int(float(raw_num_mun))) if str(raw_num_mun).strip() and str(raw_num_mun) != "nan" else str(raw_num_mun).strip()
            except:
                num_mun_val = str(raw_num_mun).strip()
            num_mun_display = f"{num_mun_val}. " if num_mun_val else ""

            if cat or concept_raw:
                c_body = markdown.markdown(concept_raw, extensions=md_extensions)
                group_concept_html += f"""
                <div class="content-block">
                    <div class="category-title">{num_gu_display} {cat} {freq_badge}</div>
                    <div class="concept-body">{c_body}</div>
                </div>
                """

            if problem_raw:
                p_body = markdown.markdown(problem_raw, extensions=md_extensions)
                a_body = markdown.markdown(answer_raw, extensions=md_extensions)
                info_tag = f'<div class="info-tag">[{info} 출제]</div>' if info else ""
                group_problem_html += f"""
                <div class="content-block problem-block">
                    {info_tag}
                    <div class="problem-body"><strong>{num_mun_display}{p_body.replace("<p>", "").replace("</p>", "")}</strong></div>
                    <div class="answer-body">{a_body}</div>
                </div>
                """

        # 섹션 간격 유지 (10px)
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
            
            .print-button-container {{
                padding: 10px 20px;
                background: white;
                border-bottom: 1px solid #eee;
                display: block;
            }}
            .btn-print {{
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
            }}
            
            .master-table {{ width: 100%; border-collapse: collapse; border: none; }}
            .master-thead {{ display: table-header-group; }} 
            
            .header-box {{
                display: flex; background-color: #f8f9fa;
                border-top: 1px solid #dee2e6; border-bottom: 1px solid #dee2e6;
                font-weight: bold; 
                /* 텍스트 정렬을 좌측으로 변경 */
                text-align: left; 
                position: sticky; top: 0; z-index: 100;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            /* 비율 6:4 엄격 고정 및 좌측 정렬 패딩 조정 */
            .header-box .concept-h {{ 
                width: 60%; 
                padding: 12px 12px 12px 30px; /* 본문 간격과 맞추기 위해 좌측 패딩 30px 적용 */
                box-sizing: border-box; 
                border-right: 1px solid #dee2e6; 
            }}
            .header-box .problem-h {{ 
                width: 40%; 
                padding: 12px 12px 12px 25px; /* 본문 간격과 맞추기 위해 좌측 패딩 25px 적용 */
                box-sizing: border-box; 
            }}

            .section-container {{ margin-bottom: 10px; }}
            .section-header {{
                width: 100%; background-color: #edf2f7;
                padding: 8px 20px; font-weight: bold; font-size: 1.0em;
                color: #718096; border-left: 5px solid #cbd5e0;
                box-sizing: border-box; 
                margin-top: 5px;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            .sub-section {{ display: flex; width: 100%; page-break-inside: auto; }}
            .column {{ display: flex; flex-direction: column; padding: 20px; box-sizing: border-box; }}
            .concept-col {{ width: 60%; border-right: 1px solid #edf2f7; padding-left: 30px; }}
            .problem-col {{ width: 40%; background-color: #fcfcfc; padding-left: 25px; -webkit-print-color-adjust: exact; }}
            .content-block {{ width: 100%; margin-bottom: 12px; page-break-inside: avoid; }}
            .category-title {{ font-weight: bold; font-size: 1.0em; color: #1a202c; margin-bottom: 8px; display: flex; align-items: center; }}
            .concept-body {{ color: #4a5568; font-size: 0.98em; }}
            .problem-block {{ font-size: 0.92em; border-bottom: 1px dashed #e2e8f0; padding-bottom: 15px; }}
            .info-tag {{ color: #a0aec0; font-weight: bold; font-size: 0.85em; margin-bottom: 6px; }}
            .problem-body {{ margin-bottom: 8px; color: #2d3748; }}
            .problem-body strong {{ font-weight: 700; }}
            .answer-body {{ color: #4a5568; padding-left: 2px; }}

            /* 기존 마크다운 표 스타일 (절대 유지) */
            table {{ border-collapse: collapse; width: 100%; margin: 12px 0; border-top: 2px solid #cbd5e0; }}
            th, td {{ border-bottom: 1px solid #e2e8f0; padding: 10px 8px; font-size: 0.9em; text-align: center; }}
            th {{ background-color: #f7fafc; color: #4a5568; font-weight: bold; -webkit-print-color-adjust: exact; }}
            tr:last-child td {{ border-bottom: 2px solid #cbd5e0; }}

            @media print {{
                .print-button-container {{ display: none !important; }}
                .header-box {{ position: static; display: flex !important; }}
                .section-header {{ background-color: #edf2f7 !important; color: #718096 !important; }}
                .problem-col {{ background-color: #fcfcfc !important; }}
                body {{ padding: 0; margin: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="print-button-container">
            <button class="btn-print" onclick="window.print()">🖨️ PDF로 저장 (인쇄하기)</button>
            <span style="font-size: 0.8em; color: #666; margin-left: 10px;">* 모든 페이지 상단에 헤더가 고정됩니다.</span>
        </div>
        
        <table class="master-table">
            <thead class="master-thead">
                <tr>
                    <td colspan="2" style="padding: 0; border: none;">
                        <div class="header-box">
                            <div class="concept-h">개념</div>
                            <div class="problem-h">문제</div>
                        </div>
                    </td>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="2" style="padding: 0; border: none;">
                        <div class="main-container">
                            {sections_html}
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """

    iframe_height = max(2000, len(df) * 150)
    components.html(full_html_page, height=iframe_height, scrolling=True)
else:
    st.error("데이터를 불러오지 못했습니다.")
