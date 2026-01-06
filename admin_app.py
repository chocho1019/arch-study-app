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
        df.columns = [col.strip() for col in df.columns]
        
        # [수정] 데이터 전처리: pk가 없고 fpk가 있는 경우 pk 자리에 fpk를 임시로 참조하게 함
        # 이를 통해 문제만 있는 행들도 소카테고리 그룹에 포함됨
        if '개념빈출' in df.columns:
            df['개념빈출'] = pd.to_numeric(df['개념빈출'], errors='coerce').fillna(0).astype(int)
        
        return df.fillna("")
    except Exception:
        return None

# 구글 드라이브 링크 변환 함수
def format_drive_link(link):
    if not link or str(link).lower() == 'nan':
        return ""
    if "drive.google.com" in link:
        file_id_match = re.search(r'd/([^/]+)', link) or re.search(r'id=([^&]+)', link)
        if file_id_match:
            file_id = file_id_match.group(1)
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
    return link

df_raw = load_data(csv_url)

st.title("건축기사 요약 노트 (커스텀 디자인 모드)")

if df_raw is not None:
    # --- 필터 영역 ---
    st.sidebar.header("🔍 필터 설정")
    only_concept = st.sidebar.checkbox("개념만 보기")
    
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
        filtered_df = filtered_df[filtered_df['개념빈출'] >= 3]
    elif freq_filter == "5회 이상 출제":
        filtered_df = filtered_df[filtered_df['개념빈출'] >= 5]
        
    sort_option = st.sidebar.checkbox("빈출 높은 순으로 정렬")
    if sort_option:
        filtered_df = filtered_df.sort_values(by='개념빈출', ascending=False)

    df = filtered_df

    # [수정] 그룹화를 위한 ID 추출 로직 강화
    # pk가 있으면 pk를 사용하고, 없으면 fpk를 사용하여 소카테고리 ID(예: A-01-01)를 추출합니다.
    def get_group_id(row):
        pk_val = str(row.get('pk', '')).strip()
        fpk_val = str(row.get('fpk', '')).strip()
        # pk가 우선, 없으면 fpk 참조
        target_id = pk_val if pk_val and pk_val != "nan" else fpk_val
        parts = target_id.split('-')
        if len(parts) >= 3:
            return "-".join(parts[:3])
        return "ETC"

    df['sub_cat_id'] = df.apply(get_group_id, axis=1)
    
    md_extensions = ['tables', 'fenced_code', 'nl2br']
    sections_html = ""

    # 소카테고리별로 그룹화하여 순회
    for sub_id, group in df.groupby('sub_cat_id', sort=not sort_option):
        group_concept_html = ""
        group_problem_html = ""
        
        # 해당 그룹의 제목(소카테고리 이름)을 가져오기 위해 pk가 있는 행을 우선 탐색
        valid_rows = group[group['소카테고리'] != ""]
        first_row = valid_rows.iloc[0] if not valid_rows.empty else group.iloc[0]
        
        sub_cat_name = str(first_row.get('소카테고리', '')).strip()
        sub_num_raw = str(first_row.get('숫소', '')).strip()
        try:
            sub_num = str(int(float(sub_num_raw))) if sub_num_raw and sub_num_raw != "nan" else ""
        except:
            sub_num = sub_num_raw
        category_title = f"{sub_num}. {sub_cat_name}" if sub_num else sub_cat_name

        for _, row in group.iterrows():
            # 데이터 추출
            cat = str(row.get('구분', '')).strip()
            concept_raw = str(row.get('개념', '')).strip()
            concept_img_url = str(row.get('개념이미지', '')).strip()
            problem_raw = str(row.get('문제', '')).strip()
            problem_img_url = str(row.get('문제이미지', '')).strip()
            answer_raw = str(row.get('정답', '')).strip()
            info = str(row.get('출제년도', '')).strip()
            freq_val = row.get('개념빈출', 0)
            
            # 1. 개념 영역 렌더링 (내용이 있는 경우만)
            if cat or concept_raw or (concept_img_url and concept_img_url.lower() != "nan"):
                freq_badge = f'<span style="color: #94a3b8; font-size: 0.8em; margin-left: 8px; font-weight: normal; border: 1px solid #94a3b8; padding: 1px 4px; border-radius: 3px;">{freq_val}회</span>' if freq_val > 0 else ""
                
                raw_num_gu = row.get('숫구', '')
                try:
                    num_gu_val = str(int(float(raw_num_gu))) if str(raw_num_gu).strip() and str(raw_num_gu) != "nan" else str(raw_num_gu).strip()
                except:
                    num_gu_val = str(raw_num_gu).strip()
                num_gu_display = f"{num_gu_val})" if num_gu_val else ""

                c_body = markdown.markdown(concept_raw, extensions=md_extensions)
                c_img_tag = ""
                if concept_img_url and concept_img_url.lower() != "nan":
                    c_direct_url = format_drive_link(concept_img_url)
                    c_img_tag = f'<div class="image-wrapper"><img src="{c_direct_url}" class="content-img" loading="lazy"></div>'
                
                group_concept_html += f"""
                <div class="content-block">
                    <div class="category-title">{num_gu_display} {cat} {freq_badge}</div>
                    <div class="concept-body">{c_body}</div>
                    {c_img_tag}
                </div>
                """

            # 2. 문제 영역 렌더링 (문제 내용이 있는 모든 행)
            if problem_raw and problem_raw.lower() != "nan":
                raw_num_mun = row.get('숫문', '')
                try:
                    num_mun_val = str(int(float(raw_num_mun))) if str(raw_num_mun).strip() and str(raw_num_mun) != "nan" else str(raw_num_mun).strip()
                except:
                    num_mun_val = str(raw_num_mun).strip()
                num_mun_display = f"{num_mun_val}. " if num_mun_val else ""

                p_body = markdown.markdown(problem_raw, extensions=md_extensions)
                a_body = markdown.markdown(answer_raw, extensions=md_extensions)
                
                p_img_tag = ""
                if problem_img_url and problem_img_url.lower() != "nan":
                    p_direct_url = format_drive_link(problem_img_url)
                    p_img_tag = f'<div class="image-wrapper"><img src="{p_direct_url}" class="content-img problem-img" loading="lazy"></div>'
                
                info_tag = f'<div class="info-tag">[{info} 출제년도]</div>' if info else ""
                group_problem_html += f"""
                <div class="content-block problem-block">
                    {info_tag}
                    <div class="problem-body"><strong>{num_mun_display}{p_body.replace("<p>", "").replace("</p>", "")}</strong></div>
                    {p_img_tag}
                    <div class="answer-body">{a_body}</div>
                </div>
                """

        # 소카테고리 컨테이너 생성
        sections_html += f"""
        <div class="section-container">
            <div class="section-header">{category_title}</div>
            <div class="sub-section">
                <div class="column concept-col">{group_concept_html}</div>
                <div class="column problem-col">{group_problem_html}</div>
            </div>
        </div>
        """

    # 스타일 설정 및 HTML 조립 (기존과 동일)
    if only_concept:
        main_container_style = "column-count: 2; column-gap: 40px; column-rule: 1px solid #edf2f7; padding: 20px;"
        header_box_display = "none"
        print_column_count = "2"
        c_h_width = "100%"
        p_h_display = "none"
        c_col_width = "100%"
        c_col_border = "none"
        p_col_display = "none"
        section_break_style = "break-inside: avoid; display: inline-block; width: 100%;"
    else:
        main_container_style = ""
        header_box_display = "flex"
        print_column_count = "1"
        c_h_width = "60%"
        p_h_display = "block"
        c_col_width = "60%"
        c_col_border = "1px solid #edf2f7"
        p_col_display = "flex"
        section_break_style = "page-break-inside: avoid;"

    full_html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 0; color: #333; line-height: 1.6; text-align: left; }}
            .print-button-container {{ padding: 10px 20px; background: white; border-bottom: 1px solid #eee; display: block; text-align: left; }}
            .btn-print {{ background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }}
            .master-table {{ width: 100%; border-collapse: collapse; border: none; table-layout: fixed; }}
            .master-thead {{ display: table-header-group; }} 
            .header-box {{ display: {header_box_display}; background-color: #f8f9fa; border-top: 1px solid #dee2e6; border-bottom: 1px solid #dee2e6; font-weight: bold; text-align: center; position: sticky; top: 0; z-index: 100; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .header-box .concept-h {{ width: {c_h_width}; padding: 4px 12px; box-sizing: border-box; border-right: {c_col_border}; }}
            .header-box .problem-h {{ width: 40%; padding: 4px 12px; box-sizing: border-box; display: {p_h_display}; }}
            .main-container {{ text-align: left; {main_container_style} }}
            .section-container {{ margin-bottom: 15px; text-align: left; {section_break_style} }}
            .section-header {{ width: 100%; background-color: #edf2f7; padding: 8px 20px; font-weight: bold; font-size: 1.0em; color: #718096; border-left: 5px solid #cbd5e0; box-sizing: border-box; margin-top: 5px; text-align: left; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .sub-section {{ display: flex; width: 100%; text-align: left; }}
            .column {{ display: flex; flex-direction: column; padding: 20px; box-sizing: border-box; text-align: left; }}
            .concept-col {{ width: {c_col_width}; border-right: {c_col_border}; padding-left: 30px; }}
            .problem-col {{ width: 40%; background-color: #fcfcfc; padding-left: 25px; display: {p_col_display}; -webkit-print-color-adjust: exact; }}
            .content-block {{ width: 100%; margin-bottom: 12px; page-break-inside: avoid; text-align: left; }}
            .category-title {{ font-weight: bold; font-size: 1.0em; color: #1a202c; margin-bottom: 8px; display: flex; align-items: center; justify-content: flex-start; }}
            .concept-body {{ color: #4a5568; font-size: 0.98em; text-align: left; }}
            .image-wrapper {{ margin: 10px 0; text-align: left; }}
            .content-img {{ max-width: 100%; height: auto; border-radius: 4px; border: 1px solid #eee; display: block; }}
            .problem-img {{ border: 1px solid #e2e8f0; margin-bottom: 10px; }}
            .problem-block {{ font-size: 0.92em; border-bottom: 1px dashed #e2e8f0; padding-bottom: 15px; text-align: left; }}
            .info-tag {{ color: #a0aec0; font-weight: bold; font-size: 0.85em; margin-bottom: 6px; text-align: left; }}
            .problem-body {{ margin-bottom: 8px; color: #2d3748; text-align: left; }}
            .answer-body {{ color: #4a5568; padding-left: 2px; text-align: left; }}
            table {{ border-collapse: collapse; width: 100%; margin: 12px 0; border-top: 2px solid #cbd5e0; }}
            th, td {{ border-bottom: 1px solid #e2e8f0; padding: 4px 8px; font-size: 0.9em; text-align: left; }}
            th {{ background-color: #f7fafc; color: #4a5568; font-weight: bold; text-align: center; -webkit-print-color-adjust: exact; }}
            tr:last-child td {{ border-bottom: 2px solid #cbd5e0; }}
            @media print {{
                .print-button-container {{ display: none !important; }}
                .header-box {{ position: static; display: {header_box_display} !important; }}
                .section-header {{ background-color: #edf2f7 !important; color: #718096 !important; }}
                .problem-col {{ background-color: #fcfcfc !important; }}
                body {{ padding: 0; margin: 0; }}
                .main-container {{ column-count: {print_column_count} !important; -webkit-column-count: {print_column_count} !important; }}
            }}
        </style>
    </head>
    <body>
        <div class="print-button-container">
            <button class="btn-print" onclick="window.print()">🖨️ PDF로 저장 (인쇄하기)</button>
            <span style="font-size: 0.8em; color: #666; margin-left: 10px;">* 설정된 필터에 맞춰 인쇄됩니다.</span>
        </div>
        <br>
        <table class="master-table">
            <thead class="master-thead">
                <tr>
                    <td style="padding: 0; border: none;">
                        <div class="header-box">
                            <div class="concept-h">개념</div>
                            <div class="problem-h">문제</div>
                        </div>
                    </td>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 0; border: none;">
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

    iframe_height = max(2000, len(df) * 250) 
    components.html(full_html_page, height=iframe_height, scrolling=True)
else:
    st.error("데이터를 불러오지 못했습니다.")
