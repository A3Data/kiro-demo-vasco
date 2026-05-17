# ⚽ Kiro Demo — Vasco da Gama Agent

Demo criada durante o workshop de introdução ao Kiro CLI, mostrando como criar um agente de IA especializado com deploy completo na AWS usando ferramentas modernas.

## 🎯 Visão de Negócio

### Problema
Torcedores e analistas precisam de acesso rápido e contextualizado a informações sobre resultados, gols e desempenho do time, sem navegar por múltiplos sites.

### Solução
Um agente de IA conversacional especializado no Vasco da Gama que:
- Responde perguntas sobre resultados, artilheiros e desempenho
- Busca informações ao vivo no ge.globo.com quando não encontra na base local
- Interface web responsiva com tabela de resultados e chat

### Valor Entregue
- **Acesso instantâneo** a dados estruturados do time
- **Análise inteligente** com contexto e estatísticas
- **Fallback automático** para busca web em dados não cadastrados
- **Deploy serverless** com custo próximo de zero

---

## 🏗️ Arquitetura

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   CloudFront    │────▶│    S3        │     │   S3 (Knowledge)│
│  (Frontend)     │     │  (Hosting)   │     │                 │
└─────────────────┘     └──────────────┘     └────────┬────────┘
                                                       │
┌─────────────────┐     ┌──────────────┐              │
│   React + Vite  │────▶│ API Gateway  │──────┐       │
│   (Chat UI)     │     │  (HTTP API)  │      │       │
└─────────────────┘     └──────────────┘      ▼       ▼
                                         ┌──────────────────┐
                                         │     Lambda       │
                                         │ (Agente Vasco)   │
                                         │  httpx + bs4     │
                                         └──────────────────┘
                                                │
                                                ▼
                                         ┌──────────────────┐
                                         │  ge.globo.com    │
                                         │  (Fallback Web)  │
                                         └──────────────────┘
```

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Frontend | React 19 + Vite | Velocidade de build, DX moderna |
| Backend | Python + FastAPI (local) / Lambda (prod) | Simplicidade, integração Strands |
| Agent | Strands Agents | Framework recomendado para AgentCore |
| Infra | CloudFront + S3 + API Gateway + Lambda | Serverless, custo zero em idle |
| CI/CD | GitHub Actions | Integração nativa com GitHub |
| MCP | awslabs.aws-api-mcp-server | Acesso AWS via Kiro CLI |

## 📁 Estrutura do Projeto

```
.
├── .kiro/
│   └── settings/mcp.json       # MCP AWS configurado (leitura + escrita)
├── .github/workflows/ci.yml    # CI/CD: testes + segurança
├── agent/
│   └── vasco_agent.py          # Agente Strands com tools
├── backend/
│   └── main.py                 # FastAPI (dev local)
├── crawler/
│   └── crawler.py              # Scraper ge.globo.com → S3
├── deploy/
│   └── lambda_function.py      # Lambda handler (produção)
├── frontend/
│   └── src/App.jsx             # React: resultados + chat
└── knowledge/
    └── vasco-knowledge-base.json  # Base de conhecimento (RAG simulado)
```

## 🚀 Como Rodar Localmente

```bash
# Backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

## 🌐 URLs em Produção

| Serviço | URL |
|---------|-----|
| Frontend | https://de2d2crx16eoa.cloudfront.net |
| API | https://8igv937iqb.execute-api.us-east-1.amazonaws.com/chat |
| Knowledge Base | https://kiro-demo-vasco-results.s3.amazonaws.com/knowledge/vasco-knowledge-base.json |

## 🔒 Segurança

- **CI/CD** roda Bandit (SAST), Safety (deps), Trivy (vulnerabilidades) e TruffleHog (secrets)
- **Lambda** com role mínima (apenas CloudWatch Logs)
- **S3** com bucket policy restrita
- **CORS** configurado no API Gateway

## 📊 Features do Agente

1. **consultar_base_vasco** — Busca dados na knowledge base do S3
2. **buscar_ge_globo** — Fallback web scraping quando dados não encontrados

### Exemplos de Perguntas
- "Quem é o artilheiro do Vasco?"
- "Quem fez gol contra o Bahia?"
- "Como está o desempenho do Vasco?"
- "O que aconteceu no jogo de ontem?"

## 🧰 Kiro CLI Features Demonstradas

- **MCP Server** — AWS API MCP para operações S3 via Kiro
- **Agentes customizados** — `.kiro/agents/` com specialist + review
- **Steerings** — Boas práticas AgentCore
- **Subagents** — Pipeline de criação + revisão
- **Knowledge Base** — JSON no S3 como RAG simulado

---

*Criado com ❤️ usando [Kiro CLI](https://kiro.dev) no workshop de introdução da A3Data.*
