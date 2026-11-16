import os
import re
import sys
import subprocess
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Troque pelo nome que aparecer na lista do Passo 1 (sem o prefixo 'models/')
MODELO = "gemini-3.5-flash-lite"

def limpar_markdown(texto: str) -> str:
    padrao = r"```(?:python)?\n(.*?)```"
    match = re.search(padrao, texto, re.DOTALL)
    return match.group(1).strip() if match else texto.strip()

def chamar_llm(prompt: str) -> tuple[str, int]:
    """Usa streaming para evitar erro 504 DEADLINE_EXCEEDED e mostrar progresso."""
    partes = []
    tokens = 0
    print("Gerando resposta", end="", flush=True)
    for chunk in client.models.generate_content_stream(model=MODELO, contents=prompt):
        if chunk.text:
            partes.append(chunk.text)
            print(".", end="", flush=True)
        if chunk.usage_metadata and chunk.usage_metadata.total_token_count:
            tokens = chunk.usage_metadata.total_token_count
    print(" concluído!")
    return "".join(partes), tokens

def rodar_pytest_e_cobertura(arquivo_teste: str) -> tuple[bool, str]:
    cmd = [
        sys.executable, "-m", "pytest",
        arquivo_teste,
        "--cov=codigo_alvo",
        "--cov-report=term-missing",
        "-q"
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    sucesso = resultado.returncode == 0
    saida_completa = resultado.stdout + "\n" + resultado.stderr
    return sucesso, saida_completa

def rodada_a_baseline(codigo_fonte: str):
    print("\n=== INICIANDO RODADA A (BASELINE ZERO-SHOT) ===")
    prompt = f"""
    Gere testes unitários usando pytest para o seguinte código Python.
    Importe as funções de 'codigo_alvo'. Retorne APENAS o código Python válido.

    Código:
    {codigo_fonte}
    """
    texto_bruto, tokens = chamar_llm(prompt)
    codigo_teste = limpar_markdown(texto_bruto)

    with open("test_baseline.py", "w", encoding="utf-8") as f:
        f.write(codigo_teste)

    sucesso, log = rodar_pytest_e_cobertura("test_baseline.py")
    print(f"Sucesso na execução: {sucesso} | Tokens totais: {tokens}")
    print(log)

def rodada_b_self_correction(codigo_fonte: str, max_tentativas: int = 3):
    print("\n=== INICIANDO RODADA B (FEW-SHOT + SELF-CORRECTION LOOP) ===")
    exemplo_few_shot = """
    Exemplo de padrão esperado:
    import pytest
    from codigo_alvo import funcao_exemplo

    def test_cenario_sucesso():
        assert funcao_exemplo(10) == 20

    def test_cenario_excecao():
        with pytest.raises(ValueError, match="mensagem esperada"):
            funcao_exemplo(-1)
    """

    prompt_inicial = f"""
    Você é um engenheiro de QA especialista em Python.
    Gere uma suíte de testes unitários em pytest com 100% de cobertura de linhas e branches para o código abaixo.
    Importe de 'codigo_alvo'. Retorne APENAS código Python puro, sem explicações.

    {exemplo_few_shot}

    Código-alvo:
    {codigo_fonte}
    """

    tokens_acumulados = 0
    prompt_atual = prompt_inicial

    for tentativa in range(1, max_tentativas + 1):
        print(f"-> Tentativa {tentativa}/{max_tentativas}: ", end="")
        texto_bruto, tokens = chamar_llm(prompt_atual)
        tokens_acumulados += tokens
        codigo_teste = limpar_markdown(texto_bruto)

        with open("test_agente.py", "w", encoding="utf-8") as f:
            f.write(codigo_teste)

        sucesso, log = rodar_pytest_e_cobertura("test_agente.py")

        if sucesso and "100%" in log:
            print(f"Sucesso total atingido na tentativa {tentativa}! | Tokens totais: {tokens_acumulados}")
            print(log)
            return

        prompt_atual = f"""
        Os testes gerados anteriormente falharam ou não atingiram 100% de cobertura.
        Analise o log do pytest abaixo, corrija os asserts, imports ou adicione testes para as linhas faltantes (Missing).
        Retorne APENAS o código Python completo e corrigido.

        Código-alvo original:
        {codigo_fonte}

        Código de teste anterior:
        {codigo_teste}

        Saída do pytest / cobertura:
        {log}
        """

    print(f"Limite de tentativas atingido. | Tokens totais: {tokens_acumulados}")
    print(log)

if __name__ == "__main__":
    with open("codigo_alvo.py", "r", encoding="utf-8") as f:
        codigo = f.read()

    rodada_a_baseline(codigo)
    rodada_b_self_correction(codigo)