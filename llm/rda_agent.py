# rda_agent/llm/rda_agent.py
class RDAAgent:
    def __init__(self, model="meta-llama/llama-4-scout-17b-16e-instruct"):
        self.model = model

    def analyze(self, code: str, language: str = "Python") -> str:
        from llm.call_llm import get_rda_analysis
        return get_rda_analysis(code, language)
