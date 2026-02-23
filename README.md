# Football Game Analysis - FastAPI

## 📌 Descrição

Este repositório contém o serviço **FastAPI** que atua como **orquestrador de análises com LLMs** para jogos de futebol.
Ele expõe endpoints públicos que permitem consultar análises avançadas, enquanto a lógica principal de orquestração (`llm-orchestrator`) permanece em um pacote privado.

---

## 🗂️ Estrutura

- `main.py` → ponto de entrada da aplicação FastAPI.
- `requirements.txt` → dependências de topo (produção e testes).
- `requirements.lock` → lockfile gerado com `pip freeze` para instalações reprodutíveis.
- `.env.example` → exemplo de variáveis de ambiente (sem chaves reais).
- `tests/` → testes automatizados com pytest.

---

## 🔗 Integração

- **Collector (NestJS + Redis + BullMQ)** → coleta dados de APIs e sites.
- **Backend (NestJS)** → expõe APIs para frontend e outros serviços.
- **Frontend (NextJS)** → interface web para usuários.
- **FastAPI (este repo)** → recebe requisições e usa o pacote privado `llm-orchestrator` para análises avançadas.
- **AI** → experimentos adicionais de inteligência artificial.

---

## 🚀 Como rodar

```bash
# instalar dependências (reprodutível)
pip install -r requirements.lock

# rodar servidor
uvicorn main:app --reload
```

## 🧪 Como testar

```bash
pytest -q
```

## ⚙️ Configuração

Configuração via `.env` (copie de `.env.example`):

```env
OPENAI_API_KEY=your_key_here
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT_SECONDS=20
PORT=8000
```

---

## 📜 Licença

Defina aqui a licença (ex: MIT, Apache 2.0).

---
