import streamlit as st
import pandas as pd

from cfg_builder import build_cfg_from_code, finalize_gen_kill
from dataflow import compute_reaching_definitions
from utils.graph_visualizer import plot_cfg
from llm.call_llm import verify_rda_table_with_llm

st.title("🔍 Reaching Definition Analysis (CFG-Based Only)")

# Sidebar for language and test mode
use_test_code = st.sidebar.toggle("Use Built-in Test Code", value=False)
uploaded_file = st.file_uploader("Upload a code file", type=["py", "js", "java"])
language = st.selectbox("Select Language", ["Python", "JavaScript", "Java"])
model = st.sidebar.text_input("Model Name", value="llama-3.3-70b-versatile")

# Load code
if use_test_code:
    code = '''
x = 1
if x > 0:
    y = x + 1
else:
    y = x - 1
z = y
'''
    st.info("Using built-in test code:")
    st.code(code, language="python")
elif uploaded_file:
    code = uploaded_file.read().decode("utf-8")
    st.code(code, language=language.lower())
else:
    code = None

if code:
    cfg = build_cfg_from_code(code, language)
    if cfg:
        finalize_gen_kill(cfg)
        compute_reaching_definitions(cfg)
        plot_cfg(cfg)
        st.image("cfg.png", caption="Control Flow Graph", use_column_width=True)

        st.subheader("📐 Static Dataflow Engine Output")
        data = []
        for node in cfg.nodes:
            data.append({
                "Node": node.id,
                "Code": node.code.strip(),
                "IN": str(node.in_set),
                "GEN": str(node.gen),
                "KILL": str(node.kill),
                "OUT": str(node.out_set)
            })
        df_engine = pd.DataFrame(data)
        st.dataframe(df_engine)
        st.subheader("🤖 Auto-Verification of RDA Table by LLM")

        if "rda_verification" not in st.session_state:
            st.session_state.rda_verification = {}

        if st.button("🔍 Run LLM Verification for All Nodes"):
            with st.spinner("Querying LLM for all nodes..."):
                try:
                    model_name = "llama-3.3-70b-versatile"
                    st.session_state.rda_verification = verify_rda_table_with_llm(
                        code=code,
                        df_engine=df_engine,
                        model=model_name
                    )
                    st.success("LLM verification completed.")
                except Exception as e:
                    st.error(f"❌ LLM verification failed: {e}")

        # === Display Results ===
        if st.session_state.get("rda_verification"):
                st.subheader("📃 LLM Semantic Evaluation per Node")

                total_nodes = len(st.session_state["rda_verification"])
                correct_count = 0
                summary_data = []

                for node_id, response in st.session_state["rda_verification"].items():
                    st.markdown(f"#### 🧩 Node {node_id}")
                    st.text_area("LLM Feedback", response, height=180, key=f"llm_response_{node_id}")

                    response_lower = response.lower()
                    if any(phrase in response_lower for phrase in [
                        "rda entry is correct",
                        "semantically correct",
                        "is valid",
                        "no issues found",
                        "no errors",
                        "correct based on the provided information"
                    ]):
                        correct_count += 1
                        status = "✅ Likely Correct"
                    else:
                        status = "❌ Needs Review"

                    summary_data.append({"Node": node_id, "Status": status})

                st.subheader("🧾 RDA Verification Summary")
                df_summary = pd.DataFrame(summary_data)
                st.dataframe(df_summary)

                percent_correct = (correct_count / total_nodes) * 100 if total_nodes else 0
                st.markdown(f"### ✅ Overall Correctness: `{percent_correct:.1f}%` of nodes passed LLM review.")
