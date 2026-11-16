```markdown
# 🧪 Piloto TCC — Geração Automatizada de Testes Unitários com LLMs e Autocorreção

Este repositório contém o experimento piloto desenvolvido para validar a arquitetura e a viabilidade metodológica de um Trabalho de Conclusão de Curso (TCC) na área de **Automação de Engenharia de Software com Inteligência Artificial Generativa**.

O objetivo do piloto é comparar empiricamente duas abordagens de geração automatizada de suítes de testes unitários em Python (`pytest`) utilizando Grandes Modelos de Linguagem (LLMs):
1. **Rodada A (*Baseline Zero-Shot*):** Solicitação direta de geração de testes sem exemplos ou feedback de execução.
2. **Rodada B (*Few-Shot + Self-Correction Loop*):** Arquitetura agêntica que fornece exemplos estruturados de referência, executa os testes gerados em ambiente isolado e retroalimenta o modelo com os logs de falha e cobertura faltante até atingir 100% de cobertura ou o limite de iterações.

---

## 📂 Estrutura do Repositório

```text
piloto_tcc_llm/
├── codigo_alvo.py          # Módulo de regras de negócio utilizado como alvo dos testes
├── experimento_piloto.py   # Orquestrador do pipeline (chamada à LLM, execução pytest e coleta de métricas)
├── test_baseline.py        # Suíte de testes gerada automaticamente na Rodada A (Zero-Shot)
├── test_agente.py          # Suíte de testes gerada automaticamente na Rodada B (Agente)
└── README.md               # Documentação do experimento

```

---

## ⚙️ Pré-requisitos e Instalação

* **Python 3.10+** (testado em Python 3.14)
* Uma chave de API válida do **Google AI Studio (Gemini)**

### 1. Clonar o repositório

```bash
git clone [https://github.com/LuHenRe/piloto_tcc_llm.git](https://github.com/LuHenRe/piloto_tcc_llm.git)
cd piloto_tcc_llm

```

### 2. Instalar as dependências

```bash
python -m pip install google-genai pytest pytest-cov

```

### 3. Configurar a variável de ambiente da API

No **Windows (PowerShell)**:

```powershell
$env:GEMINI_API_KEY="sua_chave_de_api_aqui"

```

No **Linux / macOS (Bash/Zsh)**:

```bash
export GEMINI_API_KEY="sua_chave_de_api_aqui"

```

---

## 🚀 Como Executar o Experimento

Com a variável `GEMINI_API_KEY` configurada na sessão do terminal, execute o orquestrador:

```bash
python experimento_piloto.py

```

O script realizará automaticamente:

1. A leitura do código-fonte em `codigo_alvo.py`.
2. A geração da suíte `test_baseline.py` via *streaming* e a medição de execução/cobertura via `pytest-cov`.
3. A execução do laço iterativo da Rodada B (`test_agente.py`), verificando tanto o código de saída (`returncode == 0`) quanto o atingimento de `100%` de cobertura de instruções (`Stmts`).
4. A contabilização total de tokens consumidos em cada abordagem.

---

## 📊 Resultados Preliminares (Prova de Conceito)

Na execução piloto utilizando o modelo `gemini-3.8-flash` sobre o módulo `codigo_alvo.py` (20 instruções executáveis com múltiplas ramificações condicionais e exceções), obtiveram-se os seguintes resultados:

| Métrica / Critério Avaliado | Rodada A (*Zero-Shot*) | Rodada B (*Few-Shot* + Agente) |
| --- | --- | --- |
| **Status da Execução (`pytest`)** | ❌ Falhou (`1 failed, 8 passed`) | ✅ Passou (`9 passed, 1 warning`) |
| **Iterações Necessárias** | 1 (sem autocorreção) | 1 (sucesso antes de acionar o *retry*) |
| **Cobertura de Linhas (`Stmts`)** | 100% (20/20) | 100% (20/20) |
| **Custo Computacional** | 1.126 tokens | 1.119 tokens |
| **Tratamento de Regex (`R$`)** | Falhou (não escapou o caractere `$`) | Acertou (escapou `R\$`) |
| **Validação de Casos de Borda** | Parcial (não testou `.strip()`) | Completa (testou `"  bemvindo15  "`) |

### Principais Achados Técnicos

* **Cobertura isolada não garante validade:** Na Rodada A, o modelo alcançou 100% de cobertura de linhas, mas gerou um falso negativo ao passar `"R$"` sem escape dentro de `pytest.raises(..., match=...)`, onde `$` é interpretado como âncora de fim de linha em Regex.
* **Eficácia do enquadramento estruturado:** A Rodada B corrigiu a semântica de Regex e cobriu casos de sanitização de entrada com consumo equivalente de tokens.
* **Oportunidade de evolução (Análise Estática):** A geração da Rodada B emitiu um `SyntaxWarning` no Python 3.14 por utilizar `"\$"` em vez de uma *raw string* (`r"..."`), evidenciando a necessidade de incorporar *linters* (como `ruff`) ao critério de parada do agente nas próximas etapas da pesquisa.

---

## 🗺️ Próximos Passos (Escopo do TCC)

* [ ] Expandir o benchmark para módulos reais de projetos *open-source* com maior complexidade ciclomática e dependências externas (*mocking*).
* [ ] Adicionar análise estática (`ruff`) como critério obrigatório no loop de autocorreção para eliminar *warnings*.
* [ ] Incorporar **Teste de Mutação** (`mutmut`) para avaliar a capacidade real das suítes geradas em detectar defeitos injetados no código.
* [ ] Comparar o desempenho e o custo financeiro entre diferentes famílias e tamanhos de modelos (ex.: modelos *Flash*, *Pro* e LLMs locais via Ollama).

---

## 👤 Autor

**Luiz Henrique**

Estudante de Bacharelado em Sistemas de Informação — UFCI-MG (Campus Varginha)

```

```
