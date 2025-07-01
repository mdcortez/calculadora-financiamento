# Parte 1 - Importação e Configuração Inicial

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from math import pow
from io import BytesIO
from utils import calcular_taxa
from utils import escolher_sistema, gerar_tabela_amortizacao, gerar_saldos
from utils import gerar_resumo_amortizacao
from utils import formatar_valor_br
from utils import formatar_dataframe_br




# Configuração da página
st.set_page_config(
    page_title="Calculadora de Financiamento",
    layout="centered",
    initial_sidebar_state="auto"
)

# Título principal
st.title("🏦 Calculadora de Financiamento - HP 12c + SAC x PRICE")

# Parte 2 - Entradas e seleção de varíavel

# 🔄 Botão para limpar campos
if st.button("🔄 Limpar campos"):
    for k in ["pv", "fv", "n", "i", "pmt"]:
        st.session_state[k] = None
    st.rerun()

# 🎯 Seleção da variável que o usuário deseja calcular
variavel_alvo = st.selectbox(
    "Qual variável deseja calcular?",
    ["Valor Presente (PV)", "Valor Futuro (FV)", "Número de Períodos (n)",
     "Taxa de Juros (% ao período)", "Prestação (PMT)"]
)
alvo = {
    "Valor Presente (PV)": "pv",
    "Valor Futuro (FV)": "fv",
    "Número de Períodos (n)": "n",
    "Taxa de Juros (% ao período)": "i",
    "Prestação (PMT)": "pmt"
}[variavel_alvo]

# 📥 Função para criar campos dinamicamente, exceto o campo que será calculado
def campo(label, key, fmt):
    return None if key == alvo else st.number_input(label, format=fmt, step=0.01, value=None, key=key)

# 🧾 Entradas dos campos
pv = campo("Valor Presente (PV)", "pv", "%.2f")
fv = campo("Valor Futuro (FV)", "fv", "%.2f")
n = campo("Número de Períodos (n)", "n", "%.0f")
i = campo("Taxa de Juros (% ao período)", "i", "%.4f")
pmt = campo("Prestação (PMT)", "pmt", "%.2f")

# Parte 3 - Cálculo HP 12c e validação dos inputs

# 📊 Botão para calcular a variável selecionada
if st.button("📊 Calcular variável escolhida"):
    valores = {"pv": pv, "fv": fv, "n": n, "i": i, "pmt": pmt}
    preenchidos = sum(1 for k, v in valores.items() if k != alvo and v is not None)

    if preenchidos != 4:
        st.warning("⚠️ Preencha exatamente quatro campos para calcular o quinto.")
    else:
        try:
            i_dec = i / 100 if i else None
            fator = pow(1 + i_dec, n) if i_dec and n else None
            match alvo:
                case "pv":
                    res = -pmt * (1 - 1 / fator) / i_dec - fv / fator
                    st.success(f"📍 Valor Presente calculado: R$ {res:,.2f}")
                case "fv":
                    res = -pmt * ((fator - 1) / i_dec) - pv * fator
                    st.success(f"📍 Valor Futuro calculado: R$ {res:,.2f}")
                case "pmt":
                    res = ((fv - pv * fator) * i_dec) / (fator - 1)
                    st.success(f"📍 Prestação calculada: R$ {res:,.2f}")
                case "i":
                    res = calcular_taxa(pv, fv, n, pmt)
                    st.success(f"📍 Taxa de Juros estimada: {res:.4f}% ao período")
                case "n":
                    st.warning("⚠️ Cálculo de número de períodos (n) ainda não implementado.")
        except Exception as e:
            st.error(f"❌ Erro ao calcular: {e}")

# Parte 4 — Tabela de Amortização e Exportação Excel

from utils import (
    escolher_sistema,
    gerar_tabela_amortizacao,
    gerar_saldos,
    gerar_resumo_amortizacao,
    formatar_excel_amortizacao,
    formatar_dataframe_br,
    formatar_valor_br
)

# 🔻 Separador visual
st.markdown("---")
st.subheader("📋 Tabela de Amortização + Comparativo SAC x PRICE")

# Verificação mínima antes de gerar a tabela
if pv and n and i:
    sistema_escolhido = escolher_sistema("Escolha o sistema de amortização:")

    # Geração da tabela de amortização
    df = gerar_tabela_amortizacao(pv, int(n), i, sistema_escolhido)

    # Tabela formatada para exibição em padrão BR
    df_formatada = formatar_dataframe_br(df, ["Valor Parcela", "Amortização", "Juros", "Saldo Devedor"])
    st.dataframe(df_formatada, use_container_width=True)

    # Gráfico comparativo entre SAC e PRICE
    saldo_sac = gerar_saldos(pv, n, i, "SAC")
    saldo_price = gerar_saldos(pv, n, i, "PRICE")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(1, int(n)+1)), y=saldo_sac, mode="lines+markers", name="SAC"))
    fig.add_trace(go.Scatter(x=list(range(1, int(n)+1)), y=saldo_price, mode="lines+markers", name="PRICE"))
    fig.update_layout(
        title="📈 Evolução do Saldo Devedor - SAC x PRICE",
        xaxis_title="Parcela",
        yaxis_title="Saldo (R$)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Resumo do financiamento formatado
    resumo = gerar_resumo_amortizacao(df)

    st.markdown("### 📌 Resumo do Financiamento")
    st.markdown(f"""
    - **Número de parcelas:** {resumo['Parcelas']}
    - **Total pago:** {formatar_valor_br(resumo['Total Pago'])}
    - **Total amortizado (principal):** {formatar_valor_br(resumo['Total Amortizado'])}
    - **Total em juros:** {formatar_valor_br(resumo['Total Juros'])}
    - **Percentual de juros sobre o total pago:** {resumo['Percentual em Juros']:.2f}%
    """)

    # Exportação para Excel
    buffer = formatar_excel_amortizacao(df, sistema_escolhido)
    st.download_button(
        label="📥 Baixar planilha em Excel",
        data=buffer.getvalue(),
        file_name="amortizacao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="baixar_excel"
    )
else:
    st.info("Preencha Valor Presente, Número de Períodos e Taxa de Juros para gerar a tabela, gráfico e exportação.")

# rodar o aplicativo no terminal: