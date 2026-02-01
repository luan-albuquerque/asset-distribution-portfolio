from api_actions import get_ativos
from api_tesouro import get_tesouro

# =============================
# CONFIGURAÇÕES
# =============================

COTACOES = {
    "ITSA3": 0,
    "TAEE11": 0,
    "BBAS3": 0,
    "SAPR4": 0,
    "CMIG4": 0,
    "VIVT3": 0,
    "VALE3": 0,
    "PSSA3": 0,
    "ALUP11": 0,
    "CXSE3": 0,
}

ACOES_VALORES = {
    "ITSA3": 0,
    "TAEE11": 0,
    "BBAS3": 0,
    "SAPR4": 0,
    "CMIG4": 0,
    "VIVT3": 0,
    "VALE3": 0,
    "PSSA3": 0,
    "ALUP11": 0,
    "CXSE3": 0,
}

RF_VALORES = {
    "Tesouro Selic 2031": 0,
    "Tesouro Prefixado 2032": 0,
}

# =============================
# ATUALIZAÇÃO AUTOMÁTICA
# =============================

def atualizar_acoes():
    ativos = get_ativos()

    for ativo in ativos:
        ticker = ativo.get("ticker_name")

        # Atualiza COTAÇÕES pelo current_price
        if ticker in COTACOES and ativo.get("current_price") is not None:
            COTACOES[ticker] = float(ativo["current_price"])

        # Atualiza ACOES_VALORES pelo equity_total
        if ticker in ACOES_VALORES and ativo.get("equity_total") is not None:
            ACOES_VALORES[ticker] = float(ativo["equity_total"])


def atualizar_tesouro():
    titulos = get_tesouro()

    for titulo in titulos:
        nome = titulo.get("ticker_name")

        if nome in RF_VALORES and titulo.get("equity_total") is not None:
            RF_VALORES[nome] = float(titulo["equity_total"])


def atualizar_tudo():
    atualizar_acoes()
    atualizar_tesouro()


atualizar_tudo()
