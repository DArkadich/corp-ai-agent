from typing import Dict, Any
from langgraph.graph import StateGraph, END
from openai import OpenAI


def build_graph(openai_client: OpenAI, model: str, rag_tool):
    def decide(state: Dict[str, Any]) -> str:
        q = state["input"].lower()
        if any(x in q for x in ["документ", "файл", "pdf", "инструкция", "политика", "policy"]):
            return "rag"
        return "llm"

    def rag_node(state: Dict[str, Any]) -> Dict[str, Any]:
        q = state["input"]
        rag = rag_tool.run(q, k=5)
        prompt = f"Отвечай кратко и по делу. Используй контекст:\n{rag['context']}\n\nВопрос: {q}\nОтвет:"
        r = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = r.choices[0].message.content
        return {"output": answer, "sources": rag["chunks"]}

    def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
        q = state["input"]
        r = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": q}]
        )
        return {"output": r.choices[0].message.content, "sources": []}

    def passthrough(state: Dict[str, Any]) -> Dict[str, Any]:
        return state

    g = StateGraph(dict)
    g.add_node("route", passthrough)
    g.add_node("rag", rag_node)
    g.add_node("llm", llm_node)

    g.add_conditional_edges("route", decide, {"rag": "rag", "llm": "llm"})
    g.add_edge("rag", END)
    g.add_edge("llm", END)
    g.set_entry_point("route")

    return g.compile()
