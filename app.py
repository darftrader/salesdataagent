import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Carregar dados
@st.cache_data
def carregar_dados(caminho_csv):
    df = pd.read_csv(caminho_csv, delimiter=";")
    if 'Iniciada em' in df.columns:
        df['Iniciada em'] = pd.to_datetime(df['Iniciada em'], errors='coerce')
    if 'Finalizada em' in df.columns:
        df['Finalizada em'] = pd.to_datetime(df['Finalizada em'], errors='coerce')
    return df

# 2. Funções automáticas de insights
def gerar_insights(df):
    insights = []

    # Total de vendas
    if 'Total' in df.columns:
        total_vendas = df['Total'].sum()
        insights.append(f"💰 Total de vendas: R$ {total_vendas:,.2f}")

    # Desconto total aplicado
    if 'Desconto (Valor)' in df.columns:
        total_desconto = df['Desconto (Valor)'].sum()
        insights.append(f"💸 Total de descontos aplicados: R$ {total_desconto:,.2f}")

    # Comissão dos afiliados
    if 'Comissão' in df.columns:
        total_comissao = df['Comissão'].sum()
        insights.append(f"💼 Total de comissões dos afiliados: R$ {total_comissao:,.2f}")

    # Vendas por Status (Finalizado, Estornado, etc.)
    if 'Status' in df.columns:
        status_count = df['Status'].value_counts()
        insights.append("📊 Contagem de transações por Status:")
        for status, count in status_count.items():
            insights.append(f"  {status}: {count}")

    # Vendas por Método de Pagamento
    if 'Método de Pagamento' in df.columns:
        metodo_pagamento = df['Método de Pagamento'].value_counts()
        insights.append("💳 Vendas por Método de Pagamento:")
        for metodo, count in metodo_pagamento.items():
            insights.append(f"  {metodo}: {count}")

    # Quantidade de clientes distintos
    if 'Cliente (E-mail)' in df.columns:
        clientes_distintos = df['Cliente (E-mail)'].nunique()
        insights.append(f"👥 Número de clientes distintos: {clientes_distintos}")

    # Vendas por Cidade (Top 5)
    if 'Cliente (Cidade)' in df.columns:
        vendas_cidade = df.groupby('Cliente (Cidade)').size().nlargest(5)
        insights.append("🏙️ Vendas por Cidade (Top 5):")
        for cidade, count in vendas_cidade.items():
            insights.append(f"  {cidade}: {count} vendas")

    # Vendas por Estado (Top 5)
    if 'Cliente (Estado)' in df.columns:
        vendas_estado = df.groupby('Cliente (Estado)').size().nlargest(5)
        insights.append("🏠 Vendas por Estado (Top 5):")
        for estado, count in vendas_estado.items():
            insights.append(f"  {estado}: {count} vendas")

    # Vendas por Afiliado
    if 'Afiliado (Nome)' in df.columns:
        vendas_afiliado = df.groupby('Afiliado (Nome)').size().nlargest(5)
        insights.append("👥 Vendas por Afiliado (Top 5):")
        for afiliado, count in vendas_afiliado.items():
            insights.append(f"  {afiliado}: {count} vendas")

    # Vendas por Parcelamento Sem Juros
    if 'Parcelamento sem juros' in df.columns:
        vendas_parcelamento = df['Parcelamento sem juros'].value_counts()
        insights.append("💳 Vendas com Parcelamento sem Juros:")
        for parcelamento, count in vendas_parcelamento.items():
            insights.append(f"  {parcelamento}: {count}")

    return insights

# 3. Função para gerar gráfico
def gerar_grafico(df):
    if 'Iniciada em' in df.columns and 'Total' in df.columns:
        df_temp = df.copy()
        df_temp.set_index('Iniciada em', inplace=True)
        vendas_diarias = df_temp['Total'].resample('D').sum()

        fig, ax = plt.subplots()
        vendas_diarias.plot(ax=ax, marker='o', title='Vendas Diárias')
        ax.set_ylabel('Total Vendido')
        ax.set_xlabel('Data')
        ax.grid(True)
        return fig
    else:
        return None

# 4. Streamlit App
def main():
    st.title("🤖 Agente PRO de Insights Automáticos para CSV")

    caminho_csv = st.file_uploader("📄 Envie seu arquivo CSV", type=["csv"])

    if caminho_csv:
        df = carregar_dados(caminho_csv)
        st.success("✅ Dados carregados!")

        st.subheader("🔎 Insights automáticos:")

        insights = gerar_insights(df)
        for insight in insights:
            st.info(insight)

        st.subheader("📊 Gráfico de Vendas Diárias:")

        fig = gerar_grafico(df)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("Não foi possível gerar o gráfico (faltam colunas 'Iniciada em' ou 'Total').")

        if st.checkbox("🔍 Mostrar tabela completa"):
            st.dataframe(df)

if __name__ == "__main__":
    main()
