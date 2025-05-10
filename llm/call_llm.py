# llm/call_llm.py

import requests
from cfg_builder import build_cfg_from_code, finalize_gen_kill
import os
from dotenv import load_dotenv

#load env
load_dotenv()
def load_prompt_template():
    with open("prompts/rda_prompt_template.txt", "r") as f:
        return f.read()

def call_ollama(prompt, model):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    return response.json()["response"]

def call_groq(prompt, model="llama-3.3-70b-versatile"):
    # print("API Key: ", os.getenv('GROQ_API_KEY_1'))
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        },
    )

    res_json = response.json()

    # Debug log if something goes wrong
    if "choices" not in res_json:
        raise ValueError(f"Unexpected response format from Groq API: {res_json}")
    print(res_json["choices"][0]["message"]["content"])
    return res_json["choices"][0]["message"]["content"]


def build_structured_prompt(full_code, node_id, code_line, in_set, gen_set, kill_set, out_set):
    return f"""
You are a static program analysis expert.

Here is the complete program:

{full_code}

Now analyze the following Reaching Definition Analysis entry:

- Node: {node_id}
- Code: {code_line}
- IN: {in_set}
- GEN: {gen_set}
- KILL: {kill_set}
- OUT: {out_set}

Determine if this RDA entry is semantically correct. If there are any errors, explain and provide corrected values. Be precise and use formal justification.
"""


def get_rda_analysis(prompt, model="llama-3.3-70b-versatile"):
    """Handles natural language prompt for RDA verification."""
    return call_groq(prompt, model=model)


def verify_rda_table_with_llm(code, df_engine, model="llama-3.3-70b-versatile"):
    """
    For each row in the engine's RDA table, ask the LLM if it's semantically valid.
    Returns a dictionary: {node_id: LLM_response}
    """
    verification_results = {}

    for _, row in df_engine.iterrows():
        node_id = row["Node"]
        code_line = row["Code"]
        in_set = row["IN"]
        gen_set = row["GEN"]
        kill_set = row["KILL"]
        out_set = row["OUT"]

        prompt = build_structured_prompt(code, node_id, code_line, in_set, gen_set, kill_set, out_set)
        response = call_groq(prompt, model=model)
        verification_results[node_id] = response

    return verification_results
