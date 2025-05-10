# rda_agent/llm/response_parser.py

import pandas as pd
import re
from ast import literal_eval

def normalize_definition_format(text):
    """
    Converts `(x, Node0)` → `(x,0)`
    """
    return re.sub(r"\( *(\w+) *, *Node(\d+) *\)", r"(\1,\2)", text)

def flatten_union_sets(cell_text):
    """
    If the cell contains a union like:
    {(x,0), (y,2)} ∪ {(y,4)}
    → {(x,0), (y,2), (y,4)}
    """
    if '∪' in cell_text:
        sets = [s.strip().replace("∅", "set()") for s in cell_text.split('∪')]
        try:
            unified = set()
            for s in sets:
                unified |= literal_eval(s)
            return str(unified)
        except Exception:
            return cell_text  # fallback if parsing fails
    return cell_text


def extract_rda_table(text):
    lines = [line.strip() for line in text.splitlines() if line.startswith("|")]
    if not lines or len(lines) < 2:
        return None

    headers = [h.strip() for h in lines[0].split("|")[1:-1]]
    data_rows = []

    for row in lines[1:]:
        cols = [c.strip() for c in row.split("|")[1:-1]]
        if len(cols) == len(headers):
            data_rows.append(cols)

    df = pd.DataFrame(data_rows, columns=headers)
    #remove the first row after the header
    
    df = df.iloc[1:]
    # Attempt to sort by 'Node' column numerically
    if "Node" in df.columns:
        try:
            df["Node"] = df["Node"].str.extract(r"(\\d+)").astype(float).astype(int)
            df = df.sort_values(by="Node").reset_index(drop=True)
        except Exception:
            pass  # leave unsorted if Node column isn't cleanly parseable

    return df

