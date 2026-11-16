import pytest
from datetime import date
from codigo_alvo import calcular_desconto_pedido

def test_valor_total_invalido():
    with pytest.raises(ValueError, match="O valor total do pedido deve ser maior que zero."):
        calcular_desconto_pedido(0.0, None, False, date(2023, 5, 15))

def test_cliente_vip_sem_cupom():
    resultado = calcular_desconto_pedido(200.0, None, True, date(2023, 5, 15))
    assert resultado == 180.0

def test_cliente_nao_vip_sem_cupom():
    resultado = calcular_desconto_pedido(200.0, None, False, date(2023, 5, 15))
    assert resultado == 200.0

def test_cupom_bemvindo15_sucesso():
    resultado = calcular_desconto_pedido(100.0, "  bemvindo15  ", True, date(2023, 5, 15))
    assert resultado == 75.0

def test_cupom_bemvindo15_valor_minimo_invalido():
    with pytest.raises(ValueError, match="Cupom BEMVINDO15 exige pedido mínimo de R\$ 100,00."):
        calcular_desconto_pedido(99.9, "BEMVINDO15", False, date(2023, 5, 15))

def test_cupom_blackfriday_sucesso():
    resultado = calcular_desconto_pedido(200.0, "blackfriday", True, date(2023, 11, 20))
    assert resultado == 140.0

def test_cupom_blackfriday_mes_invalido():
    with pytest.raises(ValueError, match="Cupom BLACKFRIDAY válido apenas em novembro."):
        calcular_desconto_pedido(200.0, "BLACKFRIDAY", False, date(2023, 10, 20))

def test_cupom_invalido():
    with pytest.raises(ValueError, match="Cupom inválido."):
        calcular_desconto_pedido(200.0, "CUPOM_FALSO", False, date(2023, 5, 15))

def test_teto_maximo_desconto():
    resultado = calcular_desconto_pedido(200.0, "BLACKFRIDAY", True, date(2023, 11, 15))
    assert resultado == 140.0