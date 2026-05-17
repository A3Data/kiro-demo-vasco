import { useState, useEffect, useRef } from 'react'

const S3_URL = 'https://kiro-demo-vasco-results.s3.amazonaws.com/knowledge/vasco-knowledge-base.json'
const API_URL = 'https://8igv937iqb.execute-api.us-east-1.amazonaws.com/chat'

function ResultBadge({ resultado }) {
  const colors = { V: '#2e7d32', D: '#c62828', E: '#f9a825' }
  return <span style={{ background: colors[resultado], color: '#fff', padding: '2px 8px', borderRadius: 4, fontSize: 12 }}>{resultado}</span>
}

function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  const send = async () => {
    if (!input.trim()) return
    const userMsg = { role: 'user', text: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'agent', text: data.response }])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'agent', text: `Erro: ${e.message}` }])
    }
    setLoading(false)
  }

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  return (
    <div style={{ border: '1px solid #333', borderRadius: 8, display: 'flex', flexDirection: 'column', height: 400 }}>
      <div style={{ background: '#222', color: '#fff', padding: '8px 16px', borderRadius: '8px 8px 0 0' }}>
        🤖 Agente Vasco — Pergunte sobre gols, artilheiros, desempenho (busca ao vivo no ge.globo.com se não encontrar na base)
      </div>
      <div style={{ flex: 1, overflow: 'auto', padding: 12 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 8, textAlign: m.role === 'user' ? 'right' : 'left' }}>
            <span style={{
              display: 'inline-block', maxWidth: '80%', padding: '8px 12px', borderRadius: 12,
              background: m.role === 'user' ? '#1976d2' : '#f5f5f5',
              color: m.role === 'user' ? '#fff' : '#000', whiteSpace: 'pre-wrap', textAlign: 'left'
            }}>{m.text}</span>
          </div>
        ))}
        {loading && <div style={{ color: '#999' }}>Pensando...</div>}
        <div ref={endRef} />
      </div>
      <div style={{ display: 'flex', borderTop: '1px solid #ddd' }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Pergunte sobre o Vasco..."
          style={{ flex: 1, padding: 12, border: 'none', outline: 'none', fontSize: 14 }}
        />
        <button onClick={send} disabled={loading} style={{ padding: '12px 20px', background: '#c62828', color: '#fff', border: 'none', cursor: 'pointer' }}>
          Enviar
        </button>
      </div>
    </div>
  )
}

export default function App() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch(S3_URL).then(r => r.json()).then(setData).catch(() => {})
  }, [])

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 20, fontFamily: 'system-ui' }}>
      <h1 style={{ borderBottom: '3px solid #c62828' }}>⚽ Vasco da Gama — Central do Torcedor</h1>

      {data && (
        <>
          <p style={{ color: '#666', fontSize: 14 }}>{data.resumo}</p>
          <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
            <div style={{ background: '#2e7d32', color: '#fff', padding: '10px 16px', borderRadius: 8, textAlign: 'center' }}>
              <div style={{ fontSize: 22, fontWeight: 'bold' }}>{data.desempenho.ultimos_10_jogos.vitorias}</div><div>Vitórias</div>
            </div>
            <div style={{ background: '#f9a825', padding: '10px 16px', borderRadius: 8, textAlign: 'center' }}>
              <div style={{ fontSize: 22, fontWeight: 'bold' }}>{data.desempenho.ultimos_10_jogos.empates}</div><div>Empates</div>
            </div>
            <div style={{ background: '#c62828', color: '#fff', padding: '10px 16px', borderRadius: 8, textAlign: 'center' }}>
              <div style={{ fontSize: 22, fontWeight: 'bold' }}>{data.desempenho.ultimos_10_jogos.derrotas}</div><div>Derrotas</div>
            </div>
            <div style={{ background: '#1565c0', color: '#fff', padding: '10px 16px', borderRadius: 8, textAlign: 'center' }}>
              <div style={{ fontSize: 22, fontWeight: 'bold' }}>{data.desempenho.aproveitamento}</div><div>Aprov.</div>
            </div>
          </div>

          <h2>Últimos Jogos</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: 24, fontSize: 14 }}>
            <thead><tr style={{ background: '#222', color: '#fff' }}>
              <th style={{ padding: 6 }}>Data</th><th>Jogo</th><th>Placar</th><th>Gols Vasco</th><th></th>
            </tr></thead>
            <tbody>
              {data.resultados.map((r, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: 6 }}>{r.data}</td>
                  <td style={{ textAlign: 'center' }}>{r.mandante} x {r.visitante}</td>
                  <td style={{ textAlign: 'center', fontWeight: 'bold' }}>{r.gols_mandante}x{r.gols_visitante}</td>
                  <td style={{ fontSize: 12 }}>{r.gols_vasco.join(', ') || '-'}</td>
                  <td><ResultBadge resultado={r.resultado} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <h2>💬 Chat com Agente Vasco</h2>
      <Chat />
    </div>
  )
}
