import json
import httpx

KNOWLEDGE_URL = "https://kiro-demo-vasco-results.s3.amazonaws.com/knowledge/vasco-knowledge-base.json"
GE_URL = "https://ge.globo.com/futebol/times/vasco/"


def consultar_base(pergunta):
    resp = httpx.get(KNOWLEDGE_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    p = pergunta.lower()

    if any(w in p for w in ["artilheiro", "goleador", "quem mais fez"]):
        arts = data["artilheiros"]
        return "ARTILHEIROS:\n" + "\n".join(f"- {a['jogador']}: {a['gols']} gols, {a['assistencias']} assist." for a in arts)

    if any(w in p for w in ["gol", "quem fez", "quem marcou"]):
        resultado = []
        for r in data["resultados"]:
            if r["gols_vasco"]:
                resultado.append(f"{r['data']} - {r['mandante']} {r['gols_mandante']}x{r['gols_visitante']} {r['visitante']}: {', '.join(r['gols_vasco'])}")
        return "GOLS DO VASCO:\n" + "\n".join(resultado)

    if any(w in p for w in ["desempenho", "fase", "momento", "como está"]):
        d = data["desempenho"]
        a = data["analise"]
        return (f"DESEMPENHO: {d['ultimos_10_jogos']['vitorias']}V {d['ultimos_10_jogos']['empates']}E {d['ultimos_10_jogos']['derrotas']}D\n"
                f"Aproveitamento: {d['aproveitamento']}\nGols: {d['gols_marcados']} pró, {d['gols_sofridos']} contra\n"
                f"Forças: {', '.join(a['pontos_fortes'])}\nFracos: {', '.join(a['pontos_fracos'])}\n{a['projecao']}")

    if any(w in p for w in ["último jogo", "ultima partida"]):
        r = data["resultados"][0]
        return f"ÚLTIMO JOGO ({r['data']}): {r['mandante']} {r['gols_mandante']}x{r['gols_visitante']} {r['visitante']}\nGols Vasco: {', '.join(r['gols_vasco']) or 'Nenhum'}\n{r['destaque']}"

    return json.dumps({"resumo": data["resumo"], "desempenho": data["desempenho"], "artilheiros": data["artilheiros"][:3]}, ensure_ascii=False)


def buscar_ge(consulta):
    try:
        resp = httpx.get(GE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10, follow_redirects=True)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        textos = [el.get_text(strip=True) for el in soup.find_all(["h2", "a"]) if len(el.get_text(strip=True)) > 20 and "vasco" in el.get_text(strip=True).lower()]
        return "Busca ao vivo no ge.globo.com:\n" + "\n".join(textos[:8]) if textos else "Sem dados no ge.globo.com."
    except Exception as e:
        return f"Erro: {e}"


def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        message = body.get("message", "")
        
        resposta = consultar_base(message)
        if "não" in resposta.lower() or len(resposta) < 30:
            resposta += "\n\n" + buscar_ge(message)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Allow-Methods": "POST,OPTIONS"},
            "body": json.dumps({"response": resposta}, ensure_ascii=False)
        }
    except Exception as e:
        return {"statusCode": 500, "headers": {"Access-Control-Allow-Origin": "*"}, "body": json.dumps({"error": str(e)})}
