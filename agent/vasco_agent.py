import json
import httpx
from strands import Agent, tool

KNOWLEDGE_URL = "https://kiro-demo-vasco-results.s3.amazonaws.com/knowledge/vasco-knowledge-base.json"

SYSTEM_PROMPT = """
Você é o Agente Vasco, um especialista apaixonado pelo Club de Regatas Vasco da Gama.
Você tem acesso a uma base de conhecimento com resultados recentes, artilheiros e análises do time.

Regras:
1. Sempre use a tool consultar_base_vasco para buscar dados atualizados antes de responder
2. Se a informação NÃO estiver na base local (ex: data não encontrada), use a tool buscar_ge_globo para procurar no site ge.globo.com
3. Quando usar a busca web, avise o usuário: "Não encontrei na base local, busquei no ge.globo.com:"
4. Responda em português brasileiro, com entusiasmo mas de forma informativa
5. Quando perguntarem sobre gols, cite o jogador e o minuto
6. Quando perguntarem sobre desempenho, dê estatísticas concretas
7. Seja conciso e direto nas respostas
"""


@tool
def buscar_ge_globo(consulta: str) -> str:
    """Busca informações sobre o Vasco da Gama no ge.globo.com quando a base de conhecimento local não tem a resposta.
    Use quando a pergunta é sobre um jogo ou data que não está na base local."""
    try:
        url = f"https://ge.globo.com/futebol/times/vasco/"
        resp = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15, follow_redirects=True)
        resp.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        textos = []
        for el in soup.find_all(["h2", "a", "p"]):
            t = el.get_text(strip=True)
            if len(t) > 20 and "vasco" in t.lower():
                textos.append(t)
        if textos:
            return "DADOS DO GE.GLOBO.COM (busca ao vivo):\n" + "\n".join(textos[:10])
        return "Não encontrei informações relevantes no ge.globo.com no momento."
    except Exception as e:
        return f"Erro ao buscar no ge.globo.com: {e}"


@tool
def consultar_base_vasco(pergunta: str) -> str:
    """Consulta a base de conhecimento do Vasco da Gama com resultados, gols, artilheiros e análises.
    Use sempre que precisar de dados sobre jogos, gols, desempenho ou jogadores do Vasco."""
    try:
        resp = httpx.get(KNOWLEDGE_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        pergunta_lower = pergunta.lower()

        # Artilheiros
        if any(w in pergunta_lower for w in ["artilheiro", "goleador", "quem mais fez"]):
            arts = data["artilheiros"]
            return "ARTILHEIROS:\n" + "\n".join(
                f"- {a['jogador']}: {a['gols']} gols, {a['assistencias']} assist." for a in arts
            )

        # Gols de um jogo específico
        if any(w in pergunta_lower for w in ["gol", "quem fez", "quem marcou"]):
            resultado = []
            for r in data["resultados"]:
                if r["gols_vasco"]:
                    resultado.append(f"{r['data']} - {r['mandante']} {r['gols_mandante']}x{r['gols_visitante']} {r['visitante']}: {', '.join(r['gols_vasco'])}")
            return "GOLS DO VASCO:\n" + "\n".join(resultado)

        # Desempenho
        if any(w in pergunta_lower for w in ["desempenho", "fase", "momento", "como está"]):
            d = data["desempenho"]
            a = data["analise"]
            return (
                f"DESEMPENHO RECENTE:\n"
                f"- Últimos 10 jogos: {d['ultimos_10_jogos']['vitorias']}V {d['ultimos_10_jogos']['empates']}E {d['ultimos_10_jogos']['derrotas']}D\n"
                f"- Aproveitamento: {d['aproveitamento']}\n"
                f"- Gols: {d['gols_marcados']} marcados, {d['gols_sofridos']} sofridos\n"
                f"- Sequência: {d['sequencia_atual']}\n\n"
                f"PONTOS FORTES: {', '.join(a['pontos_fortes'])}\n"
                f"PONTOS FRACOS: {', '.join(a['pontos_fracos'])}\n"
                f"PROJEÇÃO: {a['projecao']}"
            )

        # Último jogo
        if any(w in pergunta_lower for w in ["último jogo", "ultima partida", "ontem", "hoje"]):
            r = data["resultados"][0]
            return (
                f"ÚLTIMO JOGO ({r['data']}):\n"
                f"{r['mandante']} {r['gols_mandante']}x{r['gols_visitante']} {r['visitante']}\n"
                f"Competição: {r['competicao']}\n"
                f"Gols Vasco: {', '.join(r['gols_vasco']) if r['gols_vasco'] else 'Nenhum'}\n"
                f"Destaque: {r['destaque']}"
            )

        # Fallback: retorna tudo resumido
        return json.dumps({
            "resumo": data["resumo"],
            "desempenho": data["desempenho"],
            "artilheiros": data["artilheiros"][:3],
            "ultimo_jogo": data["resultados"][0],
        }, ensure_ascii=False)

    except Exception as e:
        return f"Erro ao consultar base: {e}"


def create_agent():
    return Agent(
        system_prompt=SYSTEM_PROMPT,
        tools=[consultar_base_vasco, buscar_ge_globo],
    )


if __name__ == "__main__":
    agent = create_agent()
    result = agent("Como está o desempenho do Vasco nos últimos meses?")
    print(result)
