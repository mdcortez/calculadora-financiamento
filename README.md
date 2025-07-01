# 💰 Calculadora de Financiamento HP 12c — Streamlit

Este é um app web desenvolvido em Python com Streamlit que simula os cálculos de financiamento inspirados na calculadora HP 12c. Ele permite:

- Cálculo de qualquer uma das variáveis financeiras principais (`PV`, `FV`, `PMT`, `i`, `n`)
- Escolha entre os sistemas de amortização **SAC** e **PRICE**
- Geração de tabela de amortização detalhada 📋
- Visualização gráfica da evolução do saldo devedor 📈
- Resumo do financiamento com totais e percentuais 📊
- Exportação para planilha Excel formatada com título, gráfico e estilo 📥

---

## 🚀 Como executar

### ✅ Pré-requisitos

- Python 3.8 ou superior
- Bibliotecas:
  - `streamlit`
  - `pandas`
  - `plotly`
  - `xlsxwriter`

  - 
🧠 Funcionalidades
- Interface amigável e responsiva
- Cálculos equivalentes à HP 12c
- Validação automática de campos
- Comparação gráfica entre SAC e PRICE
- Exportação para Excel com:
- Título personalizado
- Cabeçalhos coloridos
- Gráfico embutido
- Formatação BR (R$ e vírgulas)

📁 Estrutura do projeto
calculadora_financiamento/
├── novoapp12c.py        # Interface principal do Streamlit
├── utils.py             # Funções auxiliares: cálculo, exportação, formatação
├── README.md            # Este arquivo
└── requirements.txt     # (opcional) dependências do projeto

🛠️ Autor
Desenvolvido por Maiko com apoio do Copilot 🤖💙
Contribuições são bem-vindas!




Instale com:

```bash
pip install streamlit pandas plotly xlsxwriter

streamlit run novoapp12c.py


