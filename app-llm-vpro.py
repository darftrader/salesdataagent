# versão incrementada pro 
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
def formatar_reais(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

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

def calcular_estorno(df):
    if "Código" not in df.columns or "Status" not in df.columns:
        return 0
    df_ultimas = df.sort_values("Iniciada em").groupby("Código").last()
    total_clientes = len(df_ultimas)
    estornados = df_ultimas[df_ultimas["Status"].str.lower() == "estornada"]
    estorno_rate = (len(estornados) / total_clientes) * 100 if total_clientes > 0 else 0
    return estorno_rate

def calcular_chargeback(df):
    if "Status" not in df.columns:
        return 0
    total_vendas = len(df)
    chargebacks = df[df["Status"].str.lower() == "recusada"]
    chargeback_rate = (len(chargebacks) / total_vendas) * 100 if total_vendas > 0 else 0
    return chargeback_rate

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

        data_min = df["Iniciada em"].min().date()
        data_max = df["Iniciada em"].max().date()

        st.subheader("🔎 Análise Automática de Tendências")
        vendas_semana = df.resample('W-Mon', on="Iniciada em")["Total"].sum()
        faturamento_mes = df.resample('M', on="Iniciada em")["Total"].sum()

        if not vendas_semana.empty and vendas_semana.shape[0] > 1:
            tendencia_vendas = vendas_semana.pct_change().dropna().mean() * 100
            if np.isfinite(tendencia_vendas):
                if tendencia_vendas > 0:
                    st.success(f"📈 As vendas estão crescendo em média {tendencia_vendas:.2f}% por semana.")
                elif tendencia_vendas < 0:
                    st.error(f"📉 As vendas estão caindo em média {abs(tendencia_vendas):.2f}% por semana.")
                else:
                    st.info("➖ As vendas estão estáveis nas últimas semanas.")

        if not faturamento_mes.empty and faturamento_mes.shape[0] > 1:
            tendencia_ticket = faturamento_mes.pct_change().dropna().mean() * 100
            if np.isfinite(tendencia_ticket):
                if tendencia_ticket > 0:
                    st.success(f"📈 O faturamento mensal aumentou em média {tendencia_ticket:.2f}%.")
                elif tendencia_ticket < 0:
                    st.error(f"📉 O faturamento mensal caiu em média {abs(tendencia_ticket):.2f}%.")
                else:
                    st.info("➖ O faturamento mensal está estável.")

        st.subheader("🤔 Perguntas Predefinidas")
        st.info("Escolha uma pergunta rápida ou digite sua própria pergunta acima dos dados!")

        opcoes_periodo = ["Todo o Período", "Hoje", "Ontem", "Últimos 7 dias", "Últimos 30 dias", "Últimos 12 meses", "Personalizado"]
        periodo_opcao = st.selectbox("Selecionar período:", opcoes_periodo)

        if periodo_opcao == "Todo o Período":
            data_inicio, data_fim = data_min, data_max
            comparativo_inicio, comparativo_fim = data_min, data_max
        elif periodo_opcao == "Hoje":
            data_inicio = datetime.today().date()
            data_fim = datetime.today().date()
            comparativo_inicio = data_inicio - timedelta(days=1)
            comparativo_fim = data_fim - timedelta(days=1)
        elif periodo_opcao == "Ontem":
            data_inicio = (datetime.today() - timedelta(days=1)).date()
            data_fim = (datetime.today() - timedelta(days=1)).date()
            comparativo_inicio = (datetime.today() - timedelta(days=2)).date()
            comparativo_fim = (datetime.today() - timedelta(days=2)).date()
        elif periodo_opcao == "Últimos 7 dias":
            data_fim = datetime.today().date()
            data_inicio = data_fim - timedelta(days=6)
            comparativo_fim = data_inicio - timedelta(days=1)
            comparativo_inicio = comparativo_fim - timedelta(days=6)
        elif periodo_opcao == "Últimos 30 dias":
            data_fim = datetime.today().date()
            data_inicio = data_fim - timedelta(days=29)
            comparativo_fim = data_inicio - timedelta(days=1)
            comparativo_inicio = comparativo_fim - timedelta(days=29)
        elif periodo_opcao == "Últimos 12 meses":
            data_fim = datetime.today().date()
            data_inicio = data_fim - timedelta(days=365)
            comparativo_fim = data_inicio - timedelta(days=1)
            comparativo_inicio = comparativo_fim - timedelta(days=365)
        else:
            data_inicio, data_fim = st.date_input("Selecione o intervalo de datas:", [data_min, data_max])
            comparativo_inicio, comparativo_fim = data_inicio, data_fim

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

        st.subheader("🔄 Comparativo entre Períodos")
        vendas_p1 = df[(df["Iniciada em"].dt.date >= comparativo_inicio) & (df["Iniciada em"].dt.date <= comparativo_fim)]["Total"].sum()
        vendas_p2 = df[(df["Iniciada em"].dt.date >= data_inicio) & (df["Iniciada em"].dt.date <= data_fim)]["Total"].sum()

        st.metric("Comparativo de Faturamento", f"{formatar_reais(vendas_p2)}", delta=f"{((vendas_p2-vendas_p1)/vendas_p1*100):.2f}%" if vendas_p1 else "0%")

        st.download_button("📂 Baixar Relatório Filtrado", df_filtrado.to_csv(index=False).encode('utf-8'), "relatorio_pro.csv", "text/csv")

if __name__ == "__main__":
    main()
