import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Função para carregar dados
def carregar_dados(caminho_csv):
    df = pd.read_csv(caminho_csv, delimiter=";")
    
    # Converter datas
    for coluna in ['Iniciada em', 'Finalizada em', 'Estornada em']:
        if coluna in df.columns:
            df[coluna] = pd.to_datetime(df[coluna], errors='coerce')
    
    return df

# 2. Função para gerar insights
def gerar_insights(df):
    insights = []

    # Conversões seguras para números
    colunas_numericas = ['Total', 'Comissão', 'Desconto (Valor)', 'Taxas', 'Parcelamento sem juros']
    for coluna in colunas_numericas:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

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

    # Vendas por Status
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

    # Número de clientes distintos
    if 'Cliente (E-mail)' in df.columns:
        clientes_distintos = df['Cliente (E-mail)'].nunique()
        insights.append(f"👥 Número de clientes distintos: {clientes_distintos}")

    # Vendas por Cidade
    if 'Cliente (Cidade)' in df.columns:
        vendas_cidade = df['Cliente (Cidade)'].value_counts().nlargest(5)
        insights.append("🏙️ Vendas por Cidade (Top 5):")
        for cidade, count in vendas_cidade.items():
            insights.append(f"  {cidade}: {count} vendas")

    # Vendas por Estado
    if 'Cliente (Estado)' in df.columns:
        vendas_estado = df['Cliente (Estado)'].value_counts().nlargest(5)
        insights.append("🏠 Vendas por Estado (Top 5):")
        for estado, count in vendas_estado.items():
            insights.append(f"  {estado}: {count} vendas")

    # Vendas por Afiliado
    if 'Afiliado (Nome)' in df.columns:
        vendas_afiliado = df['Afiliado (Nome)'].value_counts().nlargest(5)
        insights.append("🤝 Vendas por Afiliado (Top 5):")
        for afiliado, count in vendas_afiliado.items():
            insights.append(f"  {afiliado}: {count} vendas")

    # Parcelamento sem juros
    if 'Parcelamento sem juros' in df.columns:
        parcelamento = df['Parcelamento sem juros'].value_counts()
        insights.append("💳 Vendas com Parcelamento sem Juros:")
        for parcela, count in parcelamento.items():
            insights.append(f"  {parcela}: {count}")

    return insights

# 3. Função para gerar gráfico de vendas diárias
def gerar_grafico(df):
    if 'Iniciada em' in df.columns and 'Total' in df.columns:
        df_temp = df.copy()
        df_temp = df_temp.set_index('Iniciada em')
        vendas_diarias = df_temp['Total'].resample('D').sum()

        fig, ax = plt.subplots(figsize=(10, 5))
        vendas_diarias.plot(ax=ax, marker='o', title='Vendas Diárias')
        ax.set_ylabel('Total Vendido')
        ax.set_xlabel('Data')
        ax.grid(True)
        return fig
    else:
        return None

# 4. Função principal
def main():
    st.set_page_config(page_title="Agente de Análise de Vendas", layout="wide")
    st.title("🤖 Agente de Análise de Vendas")

    arquivo = st.file_uploader("Faça upload do arquivo CSV", type=["csv"])

    if arquivo is not None:
        df = carregar_dados(arquivo)
        
        st.subheader("📋 Pré-visualização dos Dados")
        st.dataframe(df.head(20))

        insights = gerar_insights(df)

        st.subheader("🔍 Insights Automáticos")
        for insight in insights:
            st.markdown(f"- {insight}")

        st.subheader("📈 Gráfico de Vendas Diárias")
        fig = gerar_grafico(df)
        if fig:
            st.pyplot(fig)
        else:
            st.write("Não foi possível gerar o gráfico. Verifique se o CSV tem as colunas corretas.")

if __name__ == "__main__":
    main()
