import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Função para formatar valores no padrão brasileiro
def formatar_reais(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

# Função para corrigir valores numéricos e tratar erros
def corrigir_coluna(df, col):
    try:
        # Remover pontos e substituir vírgulas por ponto
        df[col] = df[col].astype(str).str.replace(".", "").str.replace(",", ".")
        # Converter para float, forçando o tratamento de valores não numéricos
        df[col] = pd.to_numeric(df[col], errors='coerce')
    except Exception as e:
        st.error(f"Erro ao processar a coluna {col}: {e}")
    return df

# Função para interpretar perguntas livres
def interpretar_pergunta(pergunta, df):
    pergunta = pergunta.lower()

    # Dicionário de intenções simples
    intencoes = {
        "total de vendas": ["total de vendas", "quanto vendi", "total vendido", "vendas"],
        "total de comissões": ["total comissão", "comissão paga", "quanto comissionei"],
        "clientes únicos": ["quantos clientes", "clientes diferentes", "clientes únicos"],
        "produtos vendidos": ["quais produtos", "produtos vendidos", "lista de produtos"],
        "top afiliados": ["quem vendeu mais", "melhores afiliados", "top afiliados"],
        "faturamento por cidade": ["vendas por cidade", "faturamento cidade", "cidade vendeu"],
    }

    # TF-IDF para matching de perguntas
    corpus = []
    tags = []
    for key, frases in intencoes.items():
        for frase in frases:
            corpus.append(frase)
            tags.append(key)
    
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    pergunta_vec = vectorizer.transform([pergunta])
    
    similaridades = cosine_similarity(pergunta_vec, X)
    idx = np.argmax(similaridades)
    intencao_detectada = tags[idx]

    # Gera a resposta baseada na intenção
    if intencao_detectada == "total de vendas":
        total = df["Total"].sum()
        return f"💰 Total de vendas: {formatar_reais(total)}"
    elif intencao_detectada == "total de comissões":
        total = df["Comissão"].sum()
        return f"💸 Total de comissões pagas: {formatar_reais(total)}"
    elif intencao_detectada == "clientes únicos":
        total = df["Cliente (E-mail)"].nunique()
        return f"👥 Número de clientes únicos: {total}"
    elif intencao_detectada == "produtos vendidos":
        produtos = df["Produto"].unique()
        return "🛍️ Produtos vendidos:\n" + "\n".join(produtos)
    elif intencao_detectada == "top afiliados":
        afiliados = df["Afiliado (Nome)"].value_counts().head(5)
        return "🏆 Top afiliados:\n" + "\n".join([f"{k}: {v} vendas" for k, v in afiliados.items()])
    elif intencao_detectada == "faturamento por cidade":
        cidades = df.groupby("Cliente (Cidade)")["Total"].sum().sort_values(ascending=False).head(5)
        return "🏙️ Faturamento por cidade:\n" + "\n".join([f"{k}: {formatar_reais(v)}" for k, v in cidades.items()])
    else:
        return "🤖 Desculpe, não entendi a pergunta. Tente reformular!"

# Função principal
def main():
    st.set_page_config(page_title="SalesDataAgent 6.0", layout="wide")
    st.title("🤖 SalesDataAgent 6.0 — Análise Inteligente de Vendas")

    uploaded_file = st.file_uploader("Faça upload do seu arquivo CSV", type=["csv"])

    if uploaded_file:
        # Ler o CSV
        df = pd.read_csv(uploaded_file, delimiter=";")

        # Corrigir valores numéricos
        for col in ["Total", "Comissão", "Desconto (Valor)", "Taxas"]:
            if col in df.columns:
                df = corrigir_coluna(df, col)

        # Corrigir datas
        if "Iniciada em" in df.columns:
            df["Iniciada em"] = pd.to_datetime(df["Iniciada em"], errors='coerce')

        st.success("Arquivo carregado com sucesso!")

        # --- FILTROS DINÂMICOS ---
        st.sidebar.header("🔎 Filtros")

        data_min = df["Iniciada em"].min()
        data_max = df["Iniciada em"].max()

        data_inicio, data_fim = st.sidebar.date_input(
            "Período de vendas",
            [data_min, data_max],
            min_value=data_min,
            max_value=data_max
        )

        afiliado = st.sidebar.selectbox("Afiliado", ["Todos"] + sorted(df["Afiliado (Nome)"].dropna().unique().tolist()))
        cidade = st.sidebar.selectbox("Cidade", ["Todos"] + sorted(df["Cliente (Cidade)"].dropna().unique().tolist()))

        # Aplicar filtros
        df_filtrado = df[
            (df["Iniciada em"].dt.date >= data_inicio) & 
            (df["Iniciada em"].dt.date <= data_fim)
        ]

        if afiliado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Afiliado (Nome)"] == afiliado]

        if cidade != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Cliente (Cidade)"] == cidade]

        # --- DASHBOARD ---
        st.subheader("📊 Resumo dos Dados Filtrados")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Vendas", formatar_reais(df_filtrado["Total"].sum()))
        col2.metric("Total de Comissões", formatar_reais(df_filtrado["Comissão"].sum()))
        col3.metric("Clientes Únicos", df_filtrado["Cliente (E-mail)"].nunique())

        # Gráfico de vendas por data
        st.subheader("📈 Vendas ao Longo do Tempo")
        vendas_diarias = df_filtrado.groupby(df_filtrado["Iniciada em"].dt.date)["Total"].sum()

        st.line_chart(vendas_diarias)

        # --- PERGUNTAS LIVRES ---
        st.subheader("🤔 Pergunte algo sobre os dados")

        pergunta = st.text_input("Digite sua pergunta:")

        if pergunta:
            resposta = interpretar_pergunta(pergunta, df_filtrado)
            st.info(resposta)

# Rodar app
if __name__ == "__main__":
    main()
