# ☕ Agente Consultor Comercial — Cafeteria

Este projeto implementa um **agente analítico conversacional** para uma cafeteria, capaz de responder perguntas de negócio como um **analista comercial experiente**.

O agente utiliza **LangGraph** para estruturar seu raciocínio em nós (estado, decisão, análise e resposta), mantendo **memória da conversa**, foco analítico e separação clara de responsabilidades.

---

## 🎯 Objetivo

Ajudar na análise comercial de uma cafeteria, respondendo perguntas como:

- O faturamento está crescendo ou retraindo?
- Alguma bebida perdeu tração ao longo do tempo?
- Existem combos de alto valor e baixa frequência?
- O consumo está concentrado em poucos clientes?
- O que explica uma queda recente nas vendas?

Tudo isso a partir de uma **base de vendas estruturada** e com respostas explicáveis.

---

## 🧠 Arquitetura do Agente

O agente foi pensado como um **sistema cognitivo**, organizado em nós:

1. **Detecção de foco**  
   Classifica a pergunta em:
   - `macro`
   - `bebida`
   - `combo`
   - `cliente`
   - `interpretacao`

2. **Extração de filtros temporais**  
   Identifica mês e/ou ano mencionados na pergunta.

3. **Preparação da base de dados**  
   Padroniza datas e cria a granularidade `mês-ano`.

4. **Geração de visões analíticas**
   - Visão macro do negócio
   - Visão por bebida
   - Visão por combo
   - Visão por cliente

5. **Interpretação executiva (quando solicitada)**  
   Consolida insights de forma estratégica.

6. **Resposta final**  
   O agente responde de forma clara, objetiva e sem exageros.

Toda a orquestração é feita com **LangGraph**, garantindo controle de estado e fluxo.

---

## 🧰 Tecnologias Utilizadas

- Python
- Pandas
- LangChain
- LangGraph
- OpenAI (via `ChatOpenAI`)
- dotenv
- Git & GitHub

---

## 📂 Estrutura do Projeto

```text
agente_cafeteria/
├── agente_cafeteria.py     
├── cafeteria_vendas.csv    
├── requirements.txt        
├── .gitignore             
└── README.md              
```

---
“ Adoraria receber seu feedback sobre a performance, facilidade de uso e resultado. Se você testar, por favor deixe seus comentários.


