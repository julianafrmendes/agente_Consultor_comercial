# ==========================================================
# ☕ AGENTE COMERCIAL ANALÍTICO — CAFETERIA
# LangGraph | Estado explícito | Nós simples
# ==========================================================

import os
import json
from typing import TypedDict, List, Optional, Dict

import pandas as pd
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# ==========================================================
# 🔐 SETUP
# ==========================================================

load_dotenv()

llm = ChatOpenAI(
    model="o4-mini",
    api_key=os.getenv("API_KEY")
)

# ==========================================================
# 📊 BASE DE DADOS
# ==========================================================

df_base = pd.read_csv("cafeteria_vendas.csv")
df_base["data"] = pd.to_datetime(df_base["data"], errors="coerce")

# ==========================================================
# 🧠 ESTADO DO AGENTE (CORAÇÃO DO LANGGRAPH)
# ==========================================================

class AgentState(TypedDict):
    messages: List
    foco: Optional[str]
    filtros: Optional[Dict]
    visao: Optional[pd.DataFrame]
    interpretacao: Optional[Dict]
    df: Optional[pd.DataFrame]

# ==========================================================
# 🧱 PREPARAÇÃO DA BASE
# ==========================================================

def preparar_base(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["mes_ano"] = df["data"].dt.to_period("M")
    return df

# ==========================================================
# 👁️ VISÕES
# ==========================================================

def visao_macro(df):
    return (
        df.groupby("mes_ano")
        .agg(
            faturamento=("ticket_total", "sum"),
            volume=("ticket_total", "count")
        )
        .reset_index()
    )


def visao_bebida(df):
    return (
        df.groupby(["mes_ano", "bebida"])
        .agg(faturamento=("ticket_total", "sum"))
        .reset_index()
    )


def visao_combo(df):
    df = df.copy()
    df["combo"] = df["bebida"] + " + " + df["acompanhamento"].fillna("")
    return (
        df.groupby(["mes_ano", "combo"])
        .agg(faturamento=("ticket_total", "sum"))
        .reset_index()
    )


def visao_cliente(df):
    return (
        df.groupby("id_cliente")
        .agg(faturamento=("ticket_total", "sum"))
        .reset_index()
    )

# ==========================================================
# 🧭 NODE 1 — DEFINIR FOCO
# ==========================================================

def definir_foco(state: AgentState):
    pergunta = state["messages"][-1].content

    prompt = f"""
Classifique a pergunta em UM foco:
macro | bebida | combo | cliente | interpretacao

Pergunta:
{pergunta}
"""
    foco = llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
    return {"foco": foco}

# ==========================================================
# 🧠 NODE 2 — EXTRAIR FILTROS
# ==========================================================

def extrair_filtros(state: AgentState):
    pergunta = state["messages"][-1].content

    prompt = f"""
Extraia filtros temporais explícitos.
Formato JSON:
{{ "mes": int | null, "ano": int | null }}

Pergunta:
{pergunta}
"""
    try:
        filtros = json.loads(
            llm.invoke([HumanMessage(content=prompt)]).content
        )
    except:
        filtros = None

    return {"filtros": filtros}

# ==========================================================
# 🧰 NODE 3 — GERAR VISÃO
# ==========================================================

def gerar_visao(state: AgentState):
    df = preparar_base(state["df"])
    filtros = state["filtros"]
    foco = state["foco"]

    if filtros:
        if filtros.get("mes"):
            df = df[df["data"].dt.month == filtros["mes"]]
        if filtros.get("ano"):
            df = df[df["data"].dt.year == filtros["ano"]]

    if foco == "macro":
        visao = visao_macro(df)
    elif foco == "bebida":
        visao = visao_bebida(df)
    elif foco == "combo":
        visao = visao_combo(df)
    elif foco == "cliente":
        visao = visao_cliente(df)
    else:
        visao = None

    return {"visao": visao}

# ==========================================================
# 🧠 NODE 4 — INTERPRETAÇÃO
# ==========================================================

def interpretar(state: AgentState):
    if state["foco"] != "interpretacao":
        return {"interpretacao": None}

    df = preparar_base(state["df"])

    interpretacao = {
        "resumo": [
            "Visão geral do negócio analisada.",
            "Padrões relevantes identificados."
        ]
    }

    return {"interpretacao": interpretacao}

# ==========================================================
# 🗣️ NODE 5 — RESPONDER
# ==========================================================

def responder(state: AgentState):
    prompt = f"""
Você é um analista comercial de cafeterias.

Pergunta:
{state["messages"][-1].content}

Dados:
{state["visao"]}

Interpretação:
{state["interpretacao"]}

Explique de forma clara e objetiva.
"""
    resp = llm.invoke([HumanMessage(content=prompt)])

    return {
        "messages": state["messages"] + [resp]
    }

# ==========================================================
# 🔗 GRAFO
# ==========================================================

graph = StateGraph(AgentState)

graph.add_node("foco", definir_foco)
graph.add_node("filtros", extrair_filtros)
graph.add_node("visao", gerar_visao)
graph.add_node("interpretar", interpretar)
graph.add_node("responder", responder)

graph.set_entry_point("foco")

graph.add_edge("foco", "filtros")
graph.add_edge("filtros", "visao")
graph.add_edge("visao", "interpretar")
graph.add_edge("interpretar", "responder")
graph.add_edge("responder", END)

app = graph.compile()

# ==========================================================
# 🔁 LOOP DE CONVERSA
# ==========================================================

print("\n☕ Agente da Cafeteria pronto! Digite sua pergunta.\n")

messages = []

while True:
    user_input = input("Você: ").strip()
    if user_input.lower() in ["sair", "exit"]:
        break

    messages.append(HumanMessage(content=user_input))

    result = app.invoke({
        "messages": messages,
        "df": df_base
    })

    resposta = result["messages"][-1]
    print("\nAgente:", resposta.content, "\n")

    messages.append(resposta)
