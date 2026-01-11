
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
        if '개념빈출' in df.columns:
            df['개념빈출'] = pd.to_numeric(df['개념빈출'], errors='coerce').fillna(0).astype(int)
        return df.fillna("")
    except Exception:
        return None

def format_drive_link(link):
    if not link or str(link).lower() == 'nan':
        return ""
    if "drive.google.com" in link:
        file_id_match = re.search(r'd/([^/]+)', link) or re.search(r'id=([^&]+)', link)
        if file_id_match:
            file_id = file_id_match.group(1)
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
    return link

def apply_custom_indent(html_text):
    if not html_text:
        return ""
    # 모든 불렛 기호와 번호를 감지하여 flex 구조로 변환
    pattern = r'<p>(<span class="bullet-marker">.*?</span>|[-①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮❶❷❸❹❺❻❼❽❾❿\*\u2022]|(?:\d+[\)\.]))\s*(.*?)<\/p>'
    replacement = r'<div class="bullet-line"><span class="bullet-marker">\1</span><span class="bullet-content">\2</span></div>'
    return re.sub(pattern, replacement, html_text, flags=re.DOTALL)

def preprocess_markdown(text):
    if not text or str(text).lower() == 'nan': return ""
    text = re.sub(r'^(\s*)-\s', r'\1<span class="bullet-marker">-</span> ', text, flags=re.MULTILINE)
    lines = text.splitlines()
    processed_lines = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue
        if i < len(lines) - 1:
            next_line = lines[i+1].strip()
            if line.startswith('|') and next_line.startswith('|'):
                processed_lines.append(line + "\n")
            else:
                processed_lines.append(line + "\n\n")
        else:
            processed_lines.append(line)
    return "".join(processed_lines)

df_raw = load_data(csv_url)

if df_raw is not None:
    def extract_group_id_robust(row):
        pk_val = str(row.get('pk', '')).strip()
        if pk_val and pk_val.lower() != 'nan':
            parts = pk_val.split('-')
            if len(parts) >= 3: return "-".join(parts[:3]) 
            return pk_val
        fpk_val = str(row.get('fpk', '')).strip()
        if fpk_val and fpk_val.lower() != 'nan':
            parts = fpk_val.split('-')
            if len(parts) >= 3: return "-".join(parts[:3])
            return fpk_val
        return None

    df_raw['sub_cat_id'] = df_raw.apply(extract_group_id_robust, axis=1)
    df_raw['sub_cat_id'] = df_raw['sub_cat_id'].ffill()
    df_raw['sub_cat_id'] = df_raw['sub_cat_id'].fillna("ETC")

st.title("건축기사 요약 노트 (커스텀 디자인 모드)")

if df_raw is not None:
    st.sidebar.header("🔍 필터 설정")
    only_concept = st.sidebar.checkbox("개념만 보기")
    subject_list = ["전체"] + sorted(list(df_raw['과목'].unique())) if '과목' in df_raw.columns else ["전체"]
    selected_subject = st.sidebar.selectbox("과목 선택", subject_list)
    
    filtered_df = df_raw if selected_subject == "전체" else df_raw[df_raw['과목'] == selected_subject]
    main_cat_list = ["전체"] + sorted(list(filtered_df['대카테고리'].unique())) if '대카테고리' in filtered_df.columns else ["전체"]
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
    md_extensions = ['tables', 'fenced_code', 'nl2br'] 
    
    sections_rows_html = ""
    last_main_cat = None

    for sub_id, group in df.groupby('sub_cat_id', sort=not sort_option):
        group_concept_html = ""
        group_problem_html = ""
        valid_rows = group[group['소카테고리'] != ""]
        first_row = valid_rows.iloc[0] if not valid_rows.empty else group.iloc[0]
        current_main_cat = str(first_row.get('대카테고리', '')).strip()

        if current_main_cat and current_main_cat != last_main_cat:
            sections_rows_html += f'<tr style="page-break-after: avoid !important;"><td colspan="2"><div class="main-section-header">{current_main_cat}</div></td></tr>'
            last_main_cat = current_main_cat

        sub_cat_name = str(first_row.get('소카테고리', '')).strip()
        sub_num_raw = str(first_row.get('숫소', '')).strip()
        try:
            sub_num = str(int(float(sub_num_raw))) if sub_num_raw and sub_num_raw != "nan" else ""
        except:
            sub_num = sub_num_raw
        category_title = f"{sub_num}. {sub_cat_name}" if sub_num else sub_cat_name

        first_c = True
        first_p = True

        for _, row in group.iterrows():
            cat = str(row.get('구분', '')).strip()
            concept_raw = str(row.get('개념', '')).strip()
            concept_img_url = str(row.get('개념이미지', '')).strip()
            problem_raw = str(row.get('문제', '')).strip()
            problem_img_url = str(row.get('문제이미지', '')).strip()
            answer_raw = str(row.get('정답', '')).strip()
            info = str(row.get('출제년도', '')).strip()
            freq_val = row.get('개념빈출', 0)
            
            if cat or concept_raw or (concept_img_url and concept_img_url.lower() != "nan"):
                freq_badge = f'<span class="freq-badge">{freq_val}회</span>' if freq_val > 0 else "<span></span>"
                raw_num_gu = row.get('숫구', '')
                try: num_gu_val = str(int(float(raw_num_gu))) if str(raw_num_gu).strip() and str(raw_num_gu) != "nan" else str(raw_num_gu).strip()
                except: num_gu_val = str(raw_num_gu).strip()
                num_gu_display = f"{num_gu_val})" if num_gu_val else ""
                
                c_body = markdown.markdown(preprocess_markdown(concept_raw), extensions=md_extensions)
                c_body = apply_custom_indent(c_body)
                c_img_tag = f'<div class="image-wrapper"><img src="{format_drive_link(concept_img_url)}" class="content-img" loading="lazy"></div>' if concept_img_url and concept_img_url.lower() != "nan" else ""
                
                c_class = "content-block" + (" first-block" if first_c else "")
                first_c = False

                group_concept_html += f"""
                <div class="{c_class}">
                    <div class="category-title">
                        <span>{num_gu_display} {cat}</span>
                        {freq_badge}
                    </div>
                    <div class="concept-body">{c_body}</div>
                    {c_img_tag}
                </div>"""

            if not only_concept and problem_raw and problem_raw.lower() != "nan":
                raw_num_mun = row.get('숫문', '')
                try: num_mun_val = str(int(float(raw_num_mun))) if str(raw_num_mun).strip() and str(raw_num_mun) != "nan" else str(raw_num_mun).strip()
                except: num_mun_val = str(raw_num_mun).strip()
                num_mun_display = f"{num_mun_val}. " if num_mun_val else ""
                
                p_body = markdown.markdown(problem_raw.replace('\n', '  \n'), extensions=md_extensions)
                p_body = apply_custom_indent(p_body)
                a_body = markdown.markdown(preprocess_markdown(answer_raw), extensions=md_extensions)
                a_body = apply_custom_indent(a_body)
                p_img_tag = f'<div class="image-wrapper"><img src="{format_drive_link(problem_img_url)}" class="content-img problem-img" loading="lazy"></div>' if problem_img_url and problem_img_url.lower() != "nan" else ""
                info_tag = f'<div class="info-tag">[{info} 출제년도]</div>' if info else ""
                p_body_cleaned = p_body.replace("<p>", "").replace("</p>", "")
                
                p_class = "content-block problem-block" + (" first-block" if first_p else "")
                first_p = False

                group_problem_html += f'<div class="{p_class}">{info_tag}<div class="problem-body"><strong>{num_mun_display}{p_body_cleaned}</strong></div>{p_img_tag}<div class="answer-body">{a_body}</div></div>'

        sections_rows_html += f"""
        <tr><td colspan="2">
            <div class="section-container">
                <div class="section-header">{category_title}</div>
                <div class="sub-section">
                    <div class="column concept-col">{group_concept_html}</div>
                    {f'<div class="column problem-col">{group_problem_html}</div>' if not only_concept else ''}
                </div>
            </div>
        </td></tr>
        """

    if only_concept:
        h_box_d, c_h_w, p_h_d, c_c_w, c_c_b = "none", "100%", "none", "100%", "none"
        s_break = "break-inside: avoid-column; display: block; width: 100%;"
    else:
        h_box_d, c_h_w, p_h_d, c_c_w, c_c_b = "flex", "60%", "block", "60%", "1px solid #edf2f7"
        s_break = "page-break-inside: auto;" 

    full_html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
        <style>
            .bullet-line {{
                display: flex !important;
                align-items: flex-start !important;
                margin: 4px 0 !important;
                line-height: 1.5;
            }}

            .bullet-marker {{
                display: inline-block !important;
                flex-shrink: 0 !important;
                width: 1.4em !important; 
                text-align: left !important;
                font-weight: normal;
            }}

            .bullet-content {{
                flex: 1 !important;
                word-break: keep-all;
            }}
            
            /* [추가 수정] '*' 기호를 사용한 리스트(ul/li)의 들여쓰기를 절반으로 줄임 */
            .concept-body ul, .answer-body ul, .problem-body ul {{
                padding-left: 2.4em !important;
                margin: 4px 0 !important;
            }}
            .concept-body li, .answer-body li, .problem-body li {{
                margin-bottom: 2px !important;
            }}

            body {{ font-family: 'Noto Sans KR', sans-serif; margin: 0; padding: 0; color: #333; line-height: 1.4; text-align: left; background-color: white; }}
            .print-button-container {{ padding: 10px 20px; background: white; border-bottom: 1px solid #eee; display: block; text-align: left; }}
            .btn-print {{ background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }}
            
            .master-table {{ width: 100%; border-collapse: collapse; border: none; table-layout: fixed; }}
            .master-table, tr, td {{ page-break-inside: auto !important; }}

            .header-box {{ display: {h_box_d}; background-color: #f8f9fa; border-top: 1px solid #dee2e6; border-bottom: 1px solid #dee2e6; font-weight: bold; text-align: center; position: sticky; top: 0; z-index: 100; -webkit-print-color-adjust: exact; }}
            .header-box .concept-h {{ width: {c_h_w}; padding: 4px 12px; box-sizing: border-box; border-right: {c_c_b}; }}
            .header-box .problem-h {{ width: 40%; padding: 4px 12px; box-sizing: border-box; display: {p_h_d}; }}
            
            .main-section-header {{
                width: 100%; background-color: #dbe4ef; padding: 8px 15px; font-weight: bold; font-size: 1.1em; color: #2d3748;
                border-left: 5px solid #4a5568; box-sizing: border-box; margin: 10px 0 5px 0;
                page-break-after: avoid !important; break-after: avoid-page !important; -webkit-print-color-adjust: exact;
            }}

            .section-container {{ margin-bottom: 20px; text-align: left; {s_break} box-sizing: border-box; }}
            
            .section-header {{ 
                width: 100%; background-color: #edf2f7; padding: 10px 15px; font-weight: bold; font-size: 0.95em; color: #718096; 
                border-left: 5px solid #cbd5e0; box-sizing: border-box; margin-bottom: 8px; 
                page-break-after: avoid !important; break-after: avoid-page !important;
                -webkit-print-color-adjust: exact; 
            }}
            
            .sub-section {{ 
                display: flex; width: 100%; align-items: stretch; 
                page-break-before: avoid !important; break-before: avoid-page !important;
            }}
            .column {{ display: flex; flex-direction: column; padding: 2px 10px; box-sizing: border-box; }}
            .concept-col {{ width: {c_c_w}; border-right: {c_c_b}; }}
            .problem-col {{ width: 40%; background-color: #fcfcfc; -webkit-print-color-adjust: exact; }}
            
            .content-block {{ width: 100%; margin-bottom: 15px; page-break-inside: avoid !important; break-inside: avoid !important; }}
            .first-block {{ page-break-before: avoid !important; break-before: avoid-page !important; }}
            
            .category-title {{ 
                font-weight: bold; font-size: 1.0em; color: #1a202c; margin-bottom: 3px; 
                display: flex; align-items: center; justify-content: space-between; 
            }}
            .freq-badge {{
                color: #94a3b8; font-size: 0.8em; font-weight: normal; 
                border: 1px solid #94a3b8; padding: 1px 4px; border-radius: 3px;
                white-space: nowrap;
            }}
            
            .concept-body, .answer-body, .problem-body {{ color: #4a5568; font-size: 0.95em; }}
            .concept-body p, .answer-body p, .problem-body p {{ margin: 2px 0; line-height: 1.5; orphans: 3; widows: 3; }}

            .image-wrapper {{ margin: 5px 0; }}
            .content-img {{ max-width: 80%; height: auto; border-radius: 4px; border: 1px solid #eee; display: inline-block; }}
            .problem-block {{ font-size: 0.9em; border-bottom: 1px dashed #e2e8f0; padding-bottom: 8px; margin-bottom: 8px; }}
            .info-tag {{ color: #a0aec0; font-weight: bold; font-size: 0.8em; margin-bottom: 2px; }}
            
            table:not(.master-table) {{ border-collapse: collapse; width: 100%; margin: 8px 0; border-top: 2px solid #cbd5e0; }}
            th, td {{ border-bottom: 1px solid #e2e8f0; padding: 8px 10px; font-size: 0.85em; text-align: left; }}
            th {{ background-color: #f7fafc; font-weight: bold; }}
            

            @media print {{
                .print-button-container {{ display: none !important; }}
                body {{ background: none; }}
                .master-table {{ table-layout: fixed; }}
                tr {{ page-break-inside: auto !important; }}
                td {{ page-break-inside: auto !important; }}
            }}
        </style>
    </head>
    <body>
        <div class="print-button-container"><button class="btn-print" onclick="window.print()">🖨️ PDF로 저장 (인쇄하기)</button></div>
        <table class="master-table">
            <thead style="display: table-header-group;">
                <tr><td colspan="2"><div class="header-box"><div class="concept-h">개념</div><div class="problem-h">문제</div></div></td></tr>
            </thead>
            <tbody>
                {sections_rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """
    iframe_height = max(2000, len(df) * 180) 
    components.html(full_html_page, height=iframe_height, scrolling=True)
else:
    st.error("데이터를 불러오지 못했습니다.")
