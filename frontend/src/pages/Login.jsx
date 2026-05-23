import React, { useState } from 'react'
import { useApp } from '../App'

export default function Login() {
  const { login, API } = useApp()
  const [loading, setLoading] = useState(false)
  const [tgId, setTgId] = useState('')

  // Bot orqali kelgan foydalanuvchi ID bilan kirish
  const handleLogin = async (userData) => {
    setLoading(true)
    try {
      const res  = await fetch(`${API}/auth/telegram/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      })
      const data = await res.json()
      if (data.access) {
        login(data.user, data.access)
      } else {
        alert("Xatolik: " + JSON.stringify(data))
      }
    } catch(e) {
      alert("Server bilan bog'lanib bo'lmadi. Django ishga tushganmi?")
    }
    setLoading(false)
  }

  // Telegram ID bilan kirish (botdan olish mumkin)
  const handleTgIdLogin = () => {
    if (!tgId || isNaN(tgId)) {
      alert("To'g'ri Telegram ID kiriting!")
      return
    }
    handleLogin({
      id: parseInt(tgId),
      first_name: 'Foydalanuvchi',
      auth_date: Math.floor(Date.now() / 1000),
      hash: 'dev',
    })
  }

  // O'zingizning ID bilan tez kirish
  const quickLogin = () => {
    handleLogin({
      id: 8012147189, // Sizning Telegram ID
      first_name: 'Abdumannonov',
      auth_date: Math.floor(Date.now() / 1000),
      hash: 'dev',
    })
  }

  return (
    <div style={{ minHeight:'100vh', display:'flex', background:'#F8F7F4' }}>
      {/* Chap panel */}
      <div style={{
        width:'50%', background:'#E63329',
        display:'flex', flexDirection:'column',
        justifyContent:'center', padding:'60px',
        position:'relative', overflow:'hidden',
      }}>
        {[200,300,400].map((s,i) => (
          <div key={i} style={{
            position:'absolute', width:s, height:s,
            border:'1px solid rgba(255,255,255,0.15)',
            borderRadius:'50%', top:'50%', left:'50%',
            transform:`translate(-${20+i*10}%,-50%)`,
          }}/>
        ))}
        <div style={{ position:'relative' }}>
          <div style={{ fontWeight:800, fontSize:32, color:'#fff',
            letterSpacing:'-1px', marginBottom:40 }}>
            ABT<span style={{ opacity:.6 }}> PREP</span>
          </div>
          <h1 style={{ fontSize:44, fontWeight:800, color:'#fff',
            lineHeight:1.1, letterSpacing:'-1.5px', marginBottom:20 }}>
            IELTS, SAT,<br/>DTM — barchasi<br/>bir joyda.
          </h1>
          <p style={{ fontSize:17, color:'rgba(255,255,255,0.8)',
            lineHeight:1.6, maxWidth:380 }}>
            O'zbekistondagi birinchi to'liq mock platform.
            Real imtihon formatida, AI tahlili bilan.
          </p>
          <div style={{ display:'flex', gap:16, marginTop:40 }}>
            {[
              {n:'IELTS', d:'Reading, Listening, Writing'},
              {n:'SAT',   d:'Math, Reading & Writing'},
              {n:'DTM',   d:'6 ta fan, rasmiy format'},
            ].map(({n,d}) => (
              <div key={n} style={{
                background:'rgba(255,255,255,0.12)',
                borderRadius:12, padding:'14px 16px',
              }}>
                <div style={{ fontWeight:800, fontSize:18, color:'#fff' }}>{n}</div>
                <div style={{ fontSize:12, color:'rgba(255,255,255,0.7)', marginTop:2 }}>{d}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* O'ng panel */}
      <div style={{ flex:1, display:'flex', alignItems:'center',
        justifyContent:'center', padding:40 }}>
        <div className="scale-in" style={{ maxWidth:400, width:'100%' }}>
          <h2 style={{ fontSize:28, fontWeight:800, marginBottom:8,
            letterSpacing:'-0.5px' }}>Xush kelibsiz</h2>
          <p style={{ color:'#8A8680', fontSize:15, marginBottom:36 }}>
            Telegram orqali kiring
          </p>

          {/* Tez kirish — o'z ID bilan */}
          <div style={{
            background:'#fff', border:'2px solid #E63329',
            borderRadius:16, padding:'24px', marginBottom:16,
          }}>
            <div style={{ fontWeight:700, marginBottom:8, color:'#E63329' }}>
              🚀 Tez kirish
            </div>
            <p style={{ fontSize:13, color:'#8A8680', marginBottom:16 }}>
              Botda /start bosib, profilingiz bilan kiring
            </p>
            <button
              onClick={quickLogin}
              disabled={loading}
              style={{
                width:'100%', padding:'14px', borderRadius:12,
                background:'#E63329', border:'none', color:'#fff',
                fontSize:15, fontWeight:700, cursor:'pointer',
              }}>
              {loading ? 'Kirilmoqda...' : '▶️ Kirish'}
            </button>
          </div>

          {/* Telegram ID bilan kirish */}
          <div style={{
            background:'#fff', border:'1px solid #E8E6E1',
            borderRadius:16, padding:'24px',
          }}>
            <div style={{ fontWeight:700, marginBottom:8 }}>
              🆔 Telegram ID bilan kirish
            </div>
            <p style={{ fontSize:13, color:'#8A8680', marginBottom:12 }}>
              Telegram ID ni @userinfobot dan bilib oling
            </p>
            <input
              type="number"
              placeholder="Masalan: 123456789"
              value={tgId}
              onChange={e => setTgId(e.target.value)}
              style={{
                width:'100%', padding:'12px 16px', borderRadius:10,
                border:'1px solid #E8E6E1', fontSize:15,
                fontFamily:'inherit', outline:'none', marginBottom:12,
                color:'#1A1916',
              }}
            />
            <button
              onClick={handleTgIdLogin}
              disabled={loading}
              style={{
                width:'100%', padding:'12px', borderRadius:10,
                background:'#1A1916', border:'none', color:'#fff',
                fontSize:14, fontWeight:600, cursor:'pointer',
              }}>
              {loading ? 'Kirilmoqda...' : 'Kirish →'}
            </button>
          </div>

          <p style={{ textAlign:'center', fontSize:12,
            color:'#C0BDB8', marginTop:20 }}>
            ID topish: Telegramda @userinfobot ga /start yuboring
          </p>
        </div>
      </div>
    </div>
  )
}