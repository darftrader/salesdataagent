# versão incrementada com 
# Cards de métricas (Faturamento, Comissão, Clientes Únicos, Churn Rate)
# Gráficos semanais e mensais
# Comparativo de períodos com delta %
# Cálculo de churn automático usando o último status por código de venda
# Exportação de relatório filtrado
# Perguntas rápidas e perguntas livres (mantidas!)

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Função para formatar valores no padrão brasileiro
def formatar_reais(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

# Função para corrigir valores numéricos
def corrigir_coluna(df, col):
    try:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("R\$", "", regex=True)
            .str.replace("\xa0", "", regex=True)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors='coerce')
    except Exception as e:
        st.error(f"Erro ao processar a coluna {col}: {e}")
    return df

# Função para interpretar perguntas livres
def interpretar_pergunta(pergunta, df):
    pergunta = pergunta.lower()
    intencoes = {
        "total de vendas": ["total de vendas", "quanto vendi", "total vendido", "vendas realizadas", "quanto foi faturado", "faturamento total", "valor arrecadado"],
        "total de comissões": ["total comissão", "comissão paga", "quanto comissionei", "quanto paguei de comissão", "comissões totais", "valor de comissão"],
        "clientes únicos": ["quantos clientes", "clientes diferentes", "clientes únicos", "quantos compradores", "número de clientes", "quantas pessoas compraram"],
        "produtos vendidos": ["quais produtos", "produtos vendidos", "lista de produtos", "o que foi vendido", "produtos comercializados", "produtos comprados"],
        "top afiliados": ["quem vendeu mais", "melhores afiliados", "top afiliados", "quem gerou mais vendas", "afiliado que mais vendeu", "ranking de afiliados"],
        "faturamento por cidade": ["vendas por cidade", "faturamento cidade", "cidade vendeu", "qual cidade vendeu mais", "ranking cidades vendas", "vendas por localização"],
        "ticket médio": ["ticket médio", "valor médio de venda", "quanto é o ticket médio", "média por venda", "ticket médio vendas"],
        "quantidade de vendas": ["quantidade de vendas", "quantas vendas fiz", "número de vendas", "vendas totais", "total de pedidos"]
    }

    corpus, tags = [], []
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
        return "🌍 Faturamento por cidade:\n" + "\n".join([f"{k}: {formatar_reais(v)}" for k, v in cidades.items()])
    elif intencao_detectada == "ticket médio":
        vendas = df["Total"].sum()
        quantidade = df["Total"].count()
        ticket_medio = vendas / quantidade if quantidade else 0
        return f"📈 Ticket médio: {formatar_reais(ticket_medio)}"
    elif intencao_detectada == "quantidade de vendas":
        quantidade = df["Total"].count()
        return f"🛒 Quantidade total de vendas: {quantidade}"
    else:
        return "🤖 Desculpe, não entendi a pergunta. Tente reformular!"

# Função para calcular churn rate
def calcular_churn(df):
    if "Código" not in df.columns or "Status" not in df.columns:
        return 0
    df_ultimas = df.sort_values("Iniciada em").groupby("Código").last()
    total_clientes = len(df_ultimas)
    churned = df_ultimas[df_ultimas["Status"].str.lower().isin(["recusada", "cancelada"])]
    churn_rate = (len(churned) / total_clientes) * 100 if total_clientes > 0 else 0
    return churn_rate

# Função principal
def main():
    st.set_page_config(page_title="SalesDataAgent PRO", layout="wide")
    st.title("🧪 SalesDataAgent PRO")

    uploaded_file = st.file_uploader("📎 Faça upload do seu arquivo CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file, delimiter=";")

        for col in ["Total", "Comissão", "Desconto (Valor)", "Taxas"]:
            if col in df.columns:
                df = corrigir_coluna(df, col)

        if "Iniciada em" in df.columns:
            df["Iniciada em"] = pd.to_datetime(df["Iniciada em"], errors='coerce')

        st.success("Arquivo carregado com sucesso!")

        st.sidebar.header("🔍 Filtros")
        data_min = df["Iniciada em"].min()
        data_max = df["Iniciada em"].max()
        data_inicio, data_fim = st.sidebar.date_input("Período de vendas", [data_min, data_max], min_value=data_min, max_value=data_max)

        afiliado = st.sidebar.selectbox("Afiliado", ["Todos"] + sorted(df["Afiliado (Nome)"].dropna().unique().tolist()))
        cidade = st.sidebar.selectbox("Cidade", ["Todos"] + sorted(df["Cliente (Cidade)"].dropna().unique().tolist()))

        df_filtrado = df[(df["Iniciada em"].dt.date >= data_inicio) & (df["Iniciada em"].dt.date <= data_fim)]
        if afiliado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Afiliado (Nome)"] == afiliado]
        if cidade != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Cliente (Cidade)"] == cidade]

        # Cards principais
        total_vendas = df_filtrado["Total"].sum()
        total_comissao = df_filtrado["Comissão"].sum()
        clientes_unicos = df_filtrado["Cliente (E-mail)"].nunique()
        ticket_medio = total_vendas / df_filtrado["Total"].count() if df_filtrado["Total"].count() else 0
        churn = calcular_churn(df_filtrado)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Faturamento", formatar_reais(total_vendas))
        col2.metric("💸 Comissões", formatar_reais(total_comissao))
        col3.metric("👥 Clientes Únicos", clientes_unicos)
        col4.metric("🌐 Churn Rate", f"{churn:.2f}%")

        # Gráficos
        st.subheader("📅 Vendas por Semana")
        vendas_semana = df_filtrado.resample('W-Mon', on="Iniciada em")["Total"].sum()
        st.line_chart(vendas_semana)

        st.subheader("📊 Faturamento Mensal")
        faturamento_mes = df_filtrado.resample('M', on="Iniciada em")["Total"].sum()
        st.bar_chart(faturamento_mes)

        # Comparativo de períodos
        st.subheader("🔄 Comparativo entre Períodos")
        col5, col6 = st.columns(2)
        with col5:
            periodo1 = st.date_input("Início Período 1", data_min)
            fim1 = st.date_input("Fim Período 1", data_max)
        with col6:
            periodo2 = st.date_input("Início Período 2", data_min)
            fim2 = st.date_input("Fim Período 2", data_max)

        vendas_p1 = df_filtrado[(df_filtrado["Iniciada em"].dt.date >= periodo1) & (df_filtrado["Iniciada em"].dt.date <= fim1)]["Total"].sum()
        vendas_p2 = df_filtrado[(df_filtrado["Iniciada em"].dt.date >= periodo2) & (df_filtrado["Iniciada em"].dt.date <= fim2)]["Total"].sum()

        st.metric("Comparativo de Faturamento", f"{formatar_reais(vendas_p2)}", delta=f"{((vendas_p2-vendas_p1)/vendas_p1*100):.2f}%" if vendas_p1 else "0%")

        # Exporta relatório CSV
        st.download_button("📂 Baixar Relatório Filtrado", df_filtrado.to_csv(index=False).encode('utf-8'), "relatorio_pro.csv", "text/csv")

        # Perguntas rápidas e livres
        st.subheader("🧐 Pergunte algo sobre os dados")
        st.markdown("Escolha uma pergunta rápida ou digite sua pergunta:")

        col1, col2 = st.columns(2)
        perguntas_rapidas = {
            "💰 Total de Vendas": "total de vendas",
            "💸 Total de Comissões": "total comissão",
            "👥 Clientes Únicos": "quantos clientes",
            "🛍️ Produtos Vendidos": "quais produtos",
            "🏆 Top Afiliados": "quem vendeu mais",
            "🌍 Faturamento por Cidade": "vendas por cidade",
            "📈 Ticket Médio": "ticket médio",
            "🛒 Quantidade de Vendas": "quantidade de vendas"
        }

        pergunta_selecionada = None
        with col1:
            for nome_exibido, pergunta_real in list(perguntas_rapidas.items())[::2]:
                if st.button(nome_exibido):
                    pergunta_selecionada = pergunta_real
        with col2:
            for nome_exibido, pergunta_real in list(perguntas_rapidas.items())[1::2]:
                if st.button(nome_exibido):
                    pergunta_selecionada = pergunta_real

        pergunta_manual = st.text_input("Ou digite sua pergunta:")
        if pergunta_selecionada:
            resposta = interpretar_pergunta(pergunta_selecionada, df_filtrado)
            st.info(resposta)
        elif pergunta_manual:
            resposta = interpretar_pergunta(pergunta_manual, df_filtrado)
            st.info(resposta)

if __name__ == "__main__":
    main()
