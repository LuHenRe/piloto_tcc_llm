# codigo_alvo.py
from datetime import date

def calcular_desconto_pedido(valor_total: float, cupom: str | None, cliente_vip: bool, data_pedido: date) -> float:
    if valor_total <= 0:
        raise ValueError("O valor total do pedido deve ser maior que zero.")

    desconto = 0.0

    if cliente_vip:
        desconto += 0.10

    if cupom:
        cupom_limpo = cupom.strip().upper()
        if cupom_limpo == "BEMVINDO15":
            if valor_total >= 100.0:
                desconto += 0.15
            else:
                raise ValueError("Cupom BEMVINDO15 exige pedido mínimo de R$ 100,00.")
        elif cupom_limpo == "BLACKFRIDAY":
            if data_pedido.month == 11:
                desconto += 0.25
            else:
                raise ValueError("Cupom BLACKFRIDAY válido apenas em novembro.")
        else:
            raise ValueError("Cupom inválido.")

    # Teto máximo de desconto acumulado é 30%
    desconto_final = min(desconto, 0.30)
    return round(valor_total * (1 - desconto_final), 2)