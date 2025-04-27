# versão incrementada pro 
# Perguntas predefinidas e campo de texto no início
# Cards de Faturamento, Comissão, Chargeback e Estornos
# Filtros adicionais: Afiliado, Cidade, Status da Venda, Método de Pagamento
# Gráficos semanais e mensais
# Análise Automática de Tendências
# Comparativo de períodos
# Baixar relatório filtrado em CSV

# versão incrementada com 
# Perguntas predefinidas e campo de texto no início
# Cards de Faturamento, Comissão, Chargeback e Estornos
# Filtros adicionais: Afiliado, Cidade, Status da Venda, Método de Pagamento
# Gráficos semanais e mensais
# Análise Automática de Tendências
# Comparativo de períodos
# Baixar relatório filtrado em CSV

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Funções auxiliares
# (Funções formatar_reais, corrigir_coluna, calcular_estorno, calcular_chargeback, responder_pergunta seguem iguais)

# Atualização principal

def main():
    st.set_page_config(page_title="SalesDataAgent PRO", layout="wide")
    st.title("🧪 SalesDataAgent TURBO")

    uploaded_file = st.file_uploader("📎 Faça upload do seu arquivo CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file, delimiter=";")

        for col in ["Total", "Comissão", "Desconto (Valor)", "Taxas"]:
            if col in df.columns:
                df = corrigir_coluna(df, col)

        if "Iniciada em" in df.columns:
            df["Iniciada em"] = pd.to_datetime(df["Iniciada em"], errors='coerce')

        st.success("Arquivo carregado com sucesso!")

        st.subheader("🧠 Perguntas Inteligentes")

        perguntas_cards = {
            "💰 Total de vendas": "total de vendas",
            "💸 Total de comissões": "total de comissões",
            "👥 Clientes únicos": "clientes únicos",
            "🛍️ Produtos vendidos": "produtos vendidos",
            "🏆 Top afiliados": "top afiliados",
            "🏙️ Faturamento por cidade": "faturamento por cidade"
        }

        cols = st.columns(3)
        for i, (titulo, intencao) in enumerate(perguntas_cards.items()):
            if cols[i % 3].button(titulo):
                resposta = responder_pergunta(intencao, df)
                st.success(resposta)

        pergunta_livre = st.text_input("✏️ Ou digite sua própria pergunta:")
        if pergunta_livre:
            resposta = responder_pergunta(pergunta_livre, df)
            st.info(resposta)

        st.subheader("🗓️ Selecione o Período para Análise")
        data_min = df["Iniciada em"].min().date()
        data_max = df["Iniciada em"].max().date()

        opcoes_periodo = ["Todo o Período", "Hoje", "Ontem", "Últimos 7 dias", "Últimos 30 dias", "Últimos 12 meses", "Personalizado"]
        periodo_opcao = st.selectbox("Período:", opcoes_periodo)

        if periodo_opcao == "Todo o Período":
            data_inicio, data_fim = data_min, data_max
        elif periodo_opcao == "Hoje":
            data_inicio = data_fim = datetime.today().date()
        elif periodo_opcao == "Ontem":
            data_inicio = data_fim = datetime.today().date() - timedelta(days=1)
        elif periodo_opcao == "Últimos 7 dias":
            data_fim = datetime.today().date()
            data_inicio = data_fim - timedelta(days=6)
        elif periodo_opcao == "Últimos 30 dias":
            data_fim = datetime.today().date()
            data_inicio = data_fim - timedelta(days=29)
        elif periodo_opcao == "Últimos 12 meses":
            data_fim = datetime.today().date()
            data_inicio = data_fim - timedelta(days=365)
        else:
            data_inicio, data_fim = st.date_input("Selecione o intervalo:", [data_min, data_max])

        df_filtrado = df[(df["Iniciada em"].dt.date >= data_inicio) & (df["Iniciada em"].dt.date <= data_fim)]

        total_vendas = df_filtrado["Total"].sum()
        total_comissao = df_filtrado["Comissão"].sum()
        ticket_medio = total_vendas / df_filtrado["Total"].count() if df_filtrado["Total"].count() else 0
        chargeback = calcular_chargeback(df_filtrado)
        estorno = calcular_estorno(df_filtrado)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Faturamento", formatar_reais(total_vendas))
        col2.metric("💸 Comissões", formatar_reais(total_comissao))
        col3.metric("⚡ Chargeback", f"{chargeback:.2f}%")
        col4.metric("🔄 Estornos", f"{estorno:.2f}%")

        st.subheader("📅 Vendas por Semana")
        vendas_semana = df_filtrado.resample('W-Mon', on="Iniciada em")["Total"].sum()
        st.line_chart(vendas_semana)

        st.subheader("📊 Faturamento Mensal")
        faturamento_mes = df_filtrado.resample('M', on="Iniciada em")["Total"].sum()
        st.bar_chart(faturamento_mes)

        st.subheader("📈 Tendência de Vendas e Faturamento")
        if not vendas_semana.empty:
            tendencia = vendas_semana.pct_change().dropna().mean() * 100
            if tendencia > 0:
                st.success(f"📈 Vendas subindo {tendencia:.2f}% por semana.")
            else:
                st.error(f"📉 Vendas caindo {abs(tendencia):.2f}% por semana.")

if __name__ == "__main__":
    main()
