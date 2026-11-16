from datetime import date
import pytest
from codigo_alvo import calcular_desconto_pedido


def test_valor_total_invalido():
    with pytest.raises(ValueError, match="O valor total do pedido deve ser maior que zero."):
        calcular_desconto_pedido(0.0, None, False, date(2023, 5, 15))

    with pytest.raises(ValueError, match="O valor total do pedido deve ser maior que zero."):
        calcular_desconto_pedido(-10.0, None, True, date(2023, 5, 15))


def test_pedido_sem_desconto():
    resultado = calcular_desconto_pedido(100.0, None, False, date(2023, 5, 15))
    assert resultado == 100.0


def test_cliente_vip_sem_cupom():
    # 10% de desconto
    resultado = calcular_desconto_pedido(200.0, None, True, date(2023, 5, 15))
    assert resultado == 180.0


def test_cupom_bemvindo15_valido():
    # VIP (10%) + BEMVINDO15 (15%) = 25% de desconto
    resultado = calcular_desconto_pedido(200.0, "bemvindo15", True, date(2023, 5, 15))
    assert resultado == 150.0


def test_cupom_bemvindo15_valor_insuficiente():
    with pytest.raises(ValueError, match="Cupom BEMVINDO15 exige pedido mínimo de R$ 100,00."):
        calcular_desconto_pedido(99.99, "BEMVINDO15", False, date(2023, 5, 15))


def test_cupom_blackfriday_valido_novembro():
    # BLACKFRIDAY (25%)
    resultado = calcular_desconto_pedido(100.0, "BLACKFRIDAY", False, date(2023, 11, 25))
    assert resultado == 75.0


def test_cupom_blackfriday_mes_invalido():
    with pytest.raises(ValueError, match="Cupom BLACKFRIDAY válido apenas em novembro."):
        calcular_desconto_pedido(100.0, "BLACKFRIDAY", False, date(2023, 10, 31))


def test_cupom_invalido():
    with pytest.raises(ValueError, match="Cupom inválido."):
        calcular_desconto_pedido(100.0, "CUPOM_FALSO", False, date(2023, 5, 15))


def test_teto_maximo_desconto():
    # VIP (10%) + BLACKFRIDAY (25%) = 35%, mas o teto é 30%
    resultado = calcular_desconto_pedido(100.0, "BLACKFRIDAY", True, date(2023, 11, 10))
    assert resultado == 70.0