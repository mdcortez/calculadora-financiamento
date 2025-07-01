from io import BytesIO
import xlsxwriter
import pandas as pd

def formatar_excel_amortizacao(df, sistema_escolhido):
    import pandas as pd
    from io import BytesIO
    import xlsxwriter

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Amortizacao", index=False, startrow=2)

        workbook = writer.book
        worksheet = writer.sheets["Amortizacao"]

        # Estilos
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'center'})
        money_fmt = workbook.add_format({'num_format': 'R$ #,##0.00', 'align': 'center'})
        int_fmt = workbook.add_format({'align': 'center'})
        title_fmt = workbook.add_format({'bold': True, 'font_size': 14})

        # Título
        worksheet.merge_range('A1:E1', f"Tabela de Amortização - Sistema: {sistema_escolhido}", title_fmt)

        # Cabeçalhos
        for col_num, col_name in enumerate(df.columns):
            worksheet.write(2, col_num, col_name, header_fmt)

        # Larguras e formatos
        for col_num, col_name in enumerate(df.columns):
            if col_name in ["Valor Parcela", "Amortização", "Juros", "Saldo Devedor"]:
                worksheet.set_column(col_num, col_num, 18, money_fmt)
            elif col_name == "Parcela":
                worksheet.set_column(col_num, col_num, 10, int_fmt)
            else:
                worksheet.set_column(col_num, col_num, 16)

        # Congelar a linha de cabeçalho
        worksheet.freeze_panes(3, 0)

        # Gráfico
        chart = workbook.add_chart({'type': 'line'})
        chart.add_series({
            'name': sistema_escolhido,
            'categories': ['Amortizacao', 3, 0, 3 + len(df) - 1, 0],
            'values':     ['Amortizacao', 3, 4, 3 + len(df) - 1, 4],
            'line':       {'color': '#4472C4'}
        })
        chart.set_title({'name': 'Evolução do Saldo Devedor'})
        chart.set_x_axis({'name': 'Parcela'})
        chart.set_y_axis({'name': 'Saldo (R$)'})
        chart.set_size({'width': 720, 'height': 360})
        worksheet.insert_chart('G4', chart)

    # 🔁 Reposiciona o buffer para o início e retorna
    buffer.seek(0)
    return buffer

def calcular_taxa(pv, fv, n, pmt, tol=0.01):
    melhor_i, menor_erro = None, float("inf")
    i = 0.0001
    while i <= 2.0:
        try:
            fator = pow(1 + i, n)
            calc_pv = -pmt * (1 - 1 / fator) / i - fv / fator
            erro = abs(calc_pv - pv)
            if erro < menor_erro:
                melhor_i, menor_erro = i, erro
            if erro <= tol:
                break
        except:
            pass
        i += 0.0001
    if melhor_i is None:
        raise ValueError("Não foi possível encontrar taxa.")
    return melhor_i * 100

import streamlit as st

def escolher_sistema(label="Sistema de Amortização"):
    sistemas = [
        ("SAC", "SAC - Sistema de Amortização Constante"),
        ("PRICE", "PR\u200cICE - Sistema Francês (Parcelas Fixas)")  # \u200c quebra a tradução automática
    ]
    return st.selectbox(
        label,
        options=[s[0] for s in sistemas],
        format_func=lambda x: dict(sistemas)[x]
    )
def gerar_tabela_amortizacao(pv, n, i, sistema):
    import pandas as pd
    from math import pow

    saldo = pv
    taxa = i / 100
    linhas = []

    if sistema == "PRICE":
        fator = (pow(1 + taxa, n) - 1) / (taxa * pow(1 + taxa, n))
        parcela = pv / fator
        for p in range(1, int(n) + 1):
            juros = saldo * taxa
            amort = parcela - juros
            saldo -= amort
            linhas.append([p, round(parcela, 2), round(amort, 2), round(juros, 2), max(round(saldo, 2), 0)])
    else:  # SAC
        amort = pv / n
        for p in range(1, int(n) + 1):
            juros = saldo * taxa
            parcela = amort + juros
            saldo -= amort
            linhas.append([p, round(parcela, 2), round(amort, 2), round(juros, 2), max(round(saldo, 2), 0)])

    return pd.DataFrame(linhas, columns=["Parcela", "Valor Parcela", "Amortização", "Juros", "Saldo Devedor"])

def gerar_saldos(pv, n, i, sistema):
    from math import pow

    saldo = pv
    taxa = i / 100
    saldos = []

    if sistema == "PRICE":
        fator = (pow(1 + taxa, n) - 1) / (taxa * pow(1 + taxa, n))
        parcela = pv / fator
        for _ in range(int(n)):
            juros = saldo * taxa
            amort = parcela - juros
            saldo -= amort
            saldos.append(round(saldo, 2))
    else:  # SAC
        amort = pv / n
        for _ in range(int(n)):
            juros = saldo * taxa
            saldo -= amort
            saldos.append(round(saldo, 2))

    return saldos

def gerar_resumo_amortizacao(df):
    total_parcelas = df["Valor Parcela"].sum()
    total_juros = df["Juros"].sum()
    total_amortizado = df["Amortização"].sum()
    parcelas = len(df)

    return {
        "Parcelas": parcelas,
        "Total Pago": total_parcelas,
        "Total Amortizado": total_amortizado,
        "Total Juros": total_juros,
        "Percentual em Juros": (total_juros / total_parcelas) * 100 if total_parcelas else 0
    }
def formatar_valor_br(valor, prefixo="R$"):
    try:
        return f"{prefixo} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

def formatar_dataframe_br(df, colunas=None, prefixo="R$"):
    def formatar_valor(valor):
        try:
            return f"{prefixo} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return valor

    df_formatado = df.copy()

    if colunas is None:
        # Detecta automaticamente colunas numéricas
        colunas = df.select_dtypes(include=["float", "int"]).columns

    for col in colunas:
        df_formatado[col] = df_formatado[col].apply(formatar_valor)

    return df_formatado