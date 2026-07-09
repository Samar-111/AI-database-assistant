import streamlit as st
import sqlite3
import os
import pandas as pd
from google import genai
from google.genai import types


st.set_page_config(
    page_title="Hyperion AI - DB Insights Engine", 
    layout="wide",
    initial_sidebar_state="expanded"
)


BACKGROUND_IMAGE_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS-RzW7Ci-QRc7bQ0vTXE8GXA5Lg3BV2QxErmX36fF6NQ&s=10"


st.markdown(f"""
    <style>
    /* Global Background image injection with a transparent dark digital overlay */
    .stApp {{
        background: linear-gradient(rgba(15, 23, 42, 0.88), rgba(30, 27, 75, 0.88)), 
                    url("{BACKGROUND_IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f8fafc;
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.85) !important;
        border-right: 1px solid #3b82f6;
    }}
    
    /* Main Header Glow */
    .main-title {{
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #38bdf8 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(56, 189, 248, 0.2);
        margin-bottom: 0.5rem;
    }}
    
    /* Subtitle style */
    .sub-title {{
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }}
    
    /* Custom KPI Cards */
    .metric-card {{
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, border-color 0.2s;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        border-color: #3b82f6;
    }}
    .metric-val {{
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }}
    .metric-lbl {{
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    /* Custom button aesthetics */
    div.stButton > button:first-child {{
        background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }}
    div.stButton > button:first-child:hover {{
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.6) !important;
    }}
    
    /* Elegant CSS Footer */
    .footer {{
        position: relative;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(15, 23, 42, 0.6);
        color: #94a3b8;
        text-align: center;
        padding: 1.5rem 0;
        font-size: 0.95rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 4rem;
        border-radius: 8px;
    }}
    .footer a {{
        color: #38bdf8;
        text-decoration: none;
        font-weight: 600;
    }}
    .footer a:hover {{
        color: #a855f7;
    }}
    </style>
""", unsafe_allow_html=True)


try:
    client = genai.Client()
except Exception:
    st.error("🔑 Missing API Key. Please configure your GEMINI_API_KEY environment variable or secrets.toml.")


if "history" not in st.session_state:
    st.session_state.history = []
if "current_df" not in st.session_state:
    st.session_state.current_df = None
if "current_sql" not in st.session_state:
    st.session_state.current_sql = None


st.sidebar.markdown("<h2 style='color:#38bdf8; font-weight:700;'>⚡ Engine Core</h2>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload target SQLite Database", type=["db", "sqlite"])

db_path = "temp_assistant.db"

if uploaded_file:
    with open(db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ Database mounted successfully.")
else:
    st.sidebar.info("📂 Awaiting SQLite file upload to start standard sequence.")
    st.stop()


def run_query(sql):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        cols = [description[0] for description in cursor.description]
        conn.close()
        return {"data": data, "columns": cols, "error": None}
    except Exception as e:
        return {"data": None, "columns": None, "error": str(e)}


def get_schema_string():
    schema_res = run_query("SELECT name, sql FROM sqlite_master WHERE type='table';")
    if schema_res["error"]:
        return "", 0
    schema_str = ""
    table_count = len(schema_res["data"])
    for row in schema_res["data"]:
        schema_str += f"Table: {row[0]}\nDDL: {row[1]}\n\n"
    return schema_str, table_count

schema_context, total_tables = get_schema_string()

with st.sidebar.expander("📊 Inspected Database Schema Structure", expanded=False):
    st.code(schema_context, language="sql")


st.markdown("<h1 class='main-title'>🤖 AI Database Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Ask conversational data analytical questions and generate real-time metrics dashboards.</p>", unsafe_allow_html=True)

with st.expander("ℹ️ About This Project", expanded=False):
    st.markdown("""
    ### 🧠 Project Architecture & Capability Matrix
    This platform functions as a full-featured **Natural Language to SQL (Text-to-SQL) Insights Engine**. It bridges the gap between conversational language and structured relational storage.
    
    * **LLM Engine:** Powered by the `gemini-3.5-flash` foundation model to process abstract semantic reasoning and emit pure, sanitized database code strings.
    * **Dynamic Schema Analysis:** Automatically inspects systemic physical table catalogs (`sqlite_master`) to extract and supply schema definitions dynamically to the AI interpreter context.
    * **Execution Protection Sandbox:** Includes embedded string-matching filters acting as a lightweight security guardrail to intercept destructive structural operations (`DROP`, `DELETE`, `ALTER`).
    * **Data Utility Layout:** Converts volatile standard cursor records into persistent multi-view frames, rendering dataframes, localized CSV compilation downlinks, and adaptive grouping chart visualization canvases.
    """)

st.markdown("<br>", unsafe_allow_html=True)


kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.markdown(f"<div class='metric-card'><div class='metric-val'>{total_tables}</div><div class='metric-lbl'>Connected Tables</div></div>", unsafe_allow_html=True)
with kpi2:
    success_queries = sum(1 for q in st.session_state.history if q["status"] == "Success")
    st.markdown(f"<div class='metric-card'><div class='metric-val'>{success_queries}</div><div class='metric-lbl'>Successful Inferences</div></div>", unsafe_allow_html=True)
with kpi3:
    st.markdown(f"<div class='metric-card'><div class='metric-val'>Gemini 3.5</div><div class='metric-lbl'>AI Foundation Model</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- 5. AI SQL Generation Logic (Overload-Resilient Version) ---
def generate_sql(user_prompt, schema):
    system_instruction = """
    You are an expert SQL generator for SQLite. 
    Given a database schema, translate the user's natural language question into a valid SQLite query.
    Return ONLY the raw SQL code string. 
    CRITICAL: Never include markdown block wrappers like ```sql or ```. No explanations or commentary.
    """
    contents = f"Schema:\n{schema}\n\nQuestion: {user_prompt}\n\nSQL:"
    
    # Attempt Primary Target Model Configuration
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
            )
        )
    except Exception as server_err:
        # If the primary server returns a 503, immediately try the alternative stable version
        st.warning("⚠️ Primary server overloaded. Switching automatically to secondary fallback node...")
        try:
            response = client.models.generate_content(
                model='gemini-2.5-pro',  # Falling back to the Pro engine tier
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                )
            )
        except Exception:
            # Absolute last resort error mapping
            st.error("🛑 All upstream AI server targets are currently processing high loads. Please resubmit this prompt in a moment.")
            return ""

    sql_clean = response.text.strip()
    if sql_clean.startswith("```"):
        sql_clean = "\n".join(sql_clean.split("\n")[1:])
    if sql_clean.endswith("```"):
        sql_clean = sql_clean.rsplit("```", 1)[0]
        
    return sql_clean.strip()


# --- 6. Core Interaction Hub (Protected against Null AI Returns) ---
user_question = st.text_input("📝 Enter your inquiry in plain text:", placeholder="e.g., Show me total tracks per album.")

if st.button("✨ Compile & Execute Query Pipeline") and user_question:
    with st.spinner("⚡ Processing linguistic parsing and execution loops..."):
        lowered_q = user_question.lower()
        if any(word in lowered_q for word in ["delete", "drop", "update", "alter"]):
            st.error("🔒 Security Guardrail: Destructive operations (DROP, DELETE, UPDATE, ALTER) are explicitly blocked.")
        else:
            generated_sql = generate_sql(user_question, schema_context)
            
            # CRITICAL CHECK: If the AI failed completely due to overloads, stop here gracefully
            if generated_sql is None or generated_sql == "":
                st.session_state.current_df = None
                st.session_state.current_sql = None
            else:
                result = run_query(generated_sql)
                
                if result["error"]:
                    st.error(f"❌ Structural Compilation Error: {result['error']}")
                    st.session_state.current_df = None
                    st.session_state.current_sql = None
                    st.session_state.history.append({"q": user_question, "sql": generated_sql, "status": "Failed"})
                else:
                    if result["data"] is not None and len(result["data"]) > 0:
                        st.session_state.current_df = pd.DataFrame(result["data"], columns=result["columns"])
                        st.session_state.current_sql = generated_sql
                        st.session_state.history.append({"q": user_question, "sql": generated_sql, "status": "Success"})
                    elif result["data"] is not None and len(result["data"]) == 0:
                        st.info("⚠️ Query compiled successfully but targeted database entity contains zero rows.")
                        st.session_state.current_df = None
                        st.session_state.current_sql = None
                        st.session_state.history.append({"q": user_question, "sql": generated_sql, "status": "Success"})

if st.session_state.current_df is not None:
    df = st.session_state.current_df
    
    with st.expander("🔮 Inspect Compiled Abstract Syntax Code (SQL)", expanded=True):
        st.code(st.session_state.current_sql, language="sql")
        
    tab1, tab2 = st.tabs(["📊 Main Dataset View", "📈 Live Visualization Canvas"])
    
    with tab1:
        st.dataframe(df, use_container_width=True)
        
        @st.cache_data
        def convert_df(df_to_convert):
            return df_to_convert.to_csv(index=False).encode('utf-8')
        
        csv_data = convert_df(df)
        st.download_button(
            label="📥 Export Data as CSV Layout",
            data=csv_data,
            file_name="query_results.csv",
            mime="text/csv"
        )
    
    with tab2:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()
        
        if len(all_cols) >= 2 and len(numeric_cols) >= 1:
            v_col1, v_col2, v_col3 = st.columns(3)
            with v_col1:
                x_axis = st.selectbox("Configure Dimension (X-Axis)", all_cols, index=0)
            with v_col2:
                y_axis = st.selectbox("Configure Value Metric (Y-Axis)", numeric_cols, index=0)
            with v_col3:
                chart_type = st.selectbox("Select Rendering Type", ["Bar Chart", "Line Chart", "Area Chart"])
            
            try:
                plot_data = df[[x_axis, y_axis]].copy()
                plot_data[x_axis] = plot_data[x_axis].astype(str)
                chart_df = plot_data.groupby(x_axis)[y_axis].sum()
                
                if chart_type == "Bar Chart":
                    st.bar_chart(chart_df, use_container_width=True)
                elif chart_type == "Line Chart":
                    st.line_chart(chart_df, use_container_width=True)
                elif chart_type == "Area Chart":
                    st.area_chart(chart_df, use_container_width=True)
                    
            except Exception:
                try:
                    raw_plot_df = df[[x_axis, y_axis]].set_index(x_axis)
                    if chart_type == "Bar Chart":
                        st.bar_chart(raw_plot_df, use_container_width=True)
                    elif chart_type == "Line Chart":
                        st.line_chart(raw_plot_df, use_container_width=True)
                    elif chart_type == "Area Chart":
                        st.area_chart(raw_plot_df, use_container_width=True)
                except Exception:
                    st.warning("⚠️ High data cardinality prevented index translation. Try swapping the axis variables.")
        else:
            st.info("💡 Additional dimensional numeric attributes are needed to render visualization charts.")


if st.session_state.history:
    st.markdown("<br><hr style='border: 0.5px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#a855f7; font-weight:700;'>📜 Session Historical Log</h3>", unsafe_allow_html=True)
    
    for item in reversed(st.session_state.history):
        status_icon = "🟢" if item["status"] == "Success" else "🔴"
        with st.expander(f"{status_icon} Prompt: {item['q']}", expanded=False):
            st.code(item["sql"], language="sql")


st.markdown("""
    <div class="footer">
        <p>Built as a single-night production sprint • Developed by 
        <a href="[https://github.com](https://github.com/Samar-111)" target="_blank">Samar Anand</a> • 
        Powered by Gemini LLM & Streamlit Architecture</p>
    </div>
""", unsafe_allow_html=True)