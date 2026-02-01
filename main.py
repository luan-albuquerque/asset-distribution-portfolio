import pandas as pd
import numpy as np

from config import (
    COTACOES,
    ACOES_VALORES,
    RF_VALORES
)

# =============================
# CONFIGURAÇÕES
# =============================
APORTE_TOTAL = 3000

# =============================
# ALVOS (%)
# =============================
ACOES_ALVO = {
    "ITSA4": 0.03,
    "TAEE11": 0.039,
    "BBAS3": 0.039,
    "SAPR4": 0.036,
    "CMIG4": 0.03,
    "VIVT3": 0.03,
    "VALE3": 0.024,
    "PSSA3": 0.024,
    "ALUP11": 0.024,
    "CXSE3": 0.024,
}

RF_ALVO = {
    "Tesouro Selic 2031": 0.525,
    "Tesouro Prefixado 2032": 0.175,
}

# =============================
# JUNTA TUDO
# =============================
VALORES = {**ACOES_VALORES, **RF_VALORES}
ALVOS = {**ACOES_ALVO, **RF_ALVO}

# =============================
# CÁLCULO BASE
# =============================
total_atual = sum(VALORES.values())
total_final = total_atual + APORTE_TOTAL

dados = []

for ativo, valor_atual in VALORES.items():
    alvo_pct = ALVOS[ativo]
    valor_ideal = total_final * alvo_pct
    gap = max(valor_ideal - valor_atual, 0)

    dados.append({
        "Ativo": ativo,
        "Valor Atual": valor_atual,
        "% Atual": valor_atual / total_atual,
        "% Alvo": alvo_pct,
        "Valor Ideal": valor_ideal,
        "GAP": gap
    })

df = pd.DataFrame(dados)

# =============================
# DISTRIBUIÇÃO DO APORTE
# =============================
soma_gaps = df["GAP"].sum()
df["Aporte"] = df["GAP"] / soma_gaps * APORTE_TOTAL
df["Aporte"] = df["Aporte"].fillna(0)

# =============================
# COTAÇÃO E QTD TEÓRICA
# =============================
df["Cotacao"] = df["Ativo"].map(COTACOES)
df["Qtd Acoes (teórica)"] = df["Aporte"] / df["Cotacao"]

# =============================
# SEPARAÇÃO
# =============================
df_acoes = df[df["Cotacao"].notna()].copy()
df_rf = df[df["Cotacao"].isna()].copy()

# =============================
# AÇÕES — COMPRA INTEIRA
# =============================
df_acoes["Qtd Inteira"] = np.floor(df_acoes["Aporte"] / df_acoes["Cotacao"])
df_acoes["Valor Usado"] = df_acoes["Qtd Inteira"] * df_acoes["Cotacao"]
df_acoes["Sobra Individual"] = df_acoes["Aporte"] - df_acoes["Valor Usado"]

# Caixa com sobras
caixa = df_acoes["Sobra Individual"].sum()

# Redistribuição para quem ficou com 0
zeros = df_acoes[df_acoes["Qtd Inteira"] == 0].sort_values("Aporte", ascending=False)

for idx, row in zeros.iterrows():
    preco = row["Cotacao"]
    if caixa >= preco:
        df_acoes.loc[idx, "Qtd Inteira"] += 1
        df_acoes.loc[idx, "Valor Usado"] += preco
        caixa -= preco

df_acoes["Aporte Ajustado"] = df_acoes["Valor Usado"]

# =============================
# RENDA FIXA
# =============================
df_rf["Qtd Inteira"] = np.nan
df_rf["Qtd Acoes (teórica)"] = np.nan
df_rf["Valor Usado"] = df_rf["Aporte"]
df_rf["Sobra Individual"] = 0.0
df_rf["Aporte Ajustado"] = df_rf["Aporte"]

# =============================
# RESULTADO FINAL
# =============================
df_acoes["Valor Final"] = df_acoes["Valor Atual"] + df_acoes["Aporte Ajustado"]
df_rf["Valor Final"] = df_rf["Valor Atual"] + df_rf["Aporte Ajustado"]

df_total = pd.concat([df_acoes, df_rf])

novo_total_final = df_total["Valor Final"].sum()
df_total["% Final"] = df_total["Valor Final"] / novo_total_final

# =============================
# EXIBIÇÃO FORMATADA
# =============================
pd.options.display.float_format = "{:,.2f}".format

df_exibir = df_total.copy()

df_exibir["Cotacao"] = df_exibir["Cotacao"].apply(
    lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "-"
)

for col in ["Valor Atual", "Aporte", "Valor Usado", "Sobra Individual", "Valor Final"]:
    df_exibir[col] = df_exibir[col].map("R$ {:,.2f}".format)

df_exibir["Qtd Acoes (teórica)"] = df_total["Qtd Acoes (teórica)"].round(2)
df_exibir["Qtd Inteira"] = df_total["Qtd Inteira"].fillna("-")

df_exibir["% Alvo"] = (df_total["% Alvo"] * 100).map("{:.2f}%".format)
df_exibir["% Final"] = (df_total["% Final"] * 100).map("{:.2f}%".format)
df_exibir["% Atual"] = (df_total["% Atual"] * 100).map("{:.2f}%".format)


df_exibir = df_exibir[[
    "Ativo",
    "% Atual",
    "% Alvo",
    "% Final",
    "Cotacao",
    "Valor Atual",
    "Aporte",
    "Qtd Acoes (teórica)",
    "Qtd Inteira",
    "Valor Usado",
    "Sobra Individual",
    "Valor Final",
]].sort_values("% Final", ascending=False)


print(df_exibir)

# =============================
# RESUMO FINAL
# =============================
print("\n📊 RESUMO GERAL")
print(f"Aporte total: R$ {APORTE_TOTAL:,.2f}")
print(f"Investido em ações: R$ {df_acoes['Valor Usado'].sum():,.2f}")
print(f"Investido em renda fixa: R$ {df_rf['Valor Usado'].sum():,.2f}")
print(f"Sobra final de caixa: R$ {caixa:,.2f}")
print(f"Carteira final: R$ {novo_total_final:,.2f}")
