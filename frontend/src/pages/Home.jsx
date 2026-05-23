import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../App'

const DAYS = ['DU','SE','CH','PA','JU','SH','YA']

export default function Home() {
  const { user, API } = useApp()
  const nav = useNavigate()
  const token = localStorage.getItem('token')
  const [history, setHistory] = useState([])
  const [exams,   setExams]   = useState([])

  useEffect(() => {
    fetch(`${API}/history/`, { headers:{ Authorization:`Bearer ${token}` } })
      .then(r => r.json()).then(d => Array.isArray(d) && setHistory(d)).catch(()=>{})
    fetch(`${API}/exams/`)
      .then(r => r.json()).then(setExams).catch(()=>{})
  }, [])

  const best = history.length ? history.reduce((a,b) => a.percent>b.percent?a:b) : null
  const last = history[0]

  const todayRoute = [
    { n:'IELTS Reading', sub:'Real imtihon matni bilan', type:'ielts_reading', emoji:'📖' },
    { n:'IELTS Listening', sub:'4 section, audio transkripsiya', type:'ielts_listening', emoji:'🎧' },
  ]

  return (
    <div style={{ padding:'32px 40px', maxWidth:1100 }}>
      {/* Header */}
      <div className="fade-up" style={{
        display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:32
      }}>
        <div>
          <div style={{ fontSize:12, fontWeight:600, color:'#E63329', letterSpacing:'0.8px',
            textTransform:'uppercase', marginBottom:6 }}>BUGUNGI YO'NALISH</div>
          <h1 style={{ fontSize:30, fontWeight:800, letterSpacing:'-0.5px' }}>
            {user?.name}, bugungi yo'nalishingiz.
          </h1>
          <p style={{ color:'#8A8680', marginTop:4, fontSize:14 }}>
            Maqsad: Band 7.0 · IELTS sana belgilanmagan
          </p>
        </div>
        <div style={{ display:'flex', gap:16, alignItems:'center' }}>
          <div style={{ textAlign:'center' }}>
            <div style={{ fontSize:24 }}>🔥</div>
            <div style={{ fontWeight:800, fontSize:20 }}>0</div>
            <div style={{ fontSize:11, color:'#8A8680' }}>Streak</div>
          </div>
          <div style={{ textAlign:'center' }}>
            <div style={{ fontSize:24 }}>⭐</div>
            <div style={{ fontWeight:800, fontSize:20 }}>{user?.xp || 0}</div>
            <div style={{ fontSize:11, color:'#8A8680' }}>XP</div>
          </div>
        </div>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 380px', gap:24 }}>
        {/* Left */}
        <div>
          {/* Band history */}
          <div className="fade-up" style={{
            background:'#fff', border:'1px solid #E8E6E1', borderRadius:20,
            padding:'28px', marginBottom:20
          }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:20 }}>
              <div>
                <div style={{ fontSize:11, fontWeight:600, color:'#8A8680', textTransform:'uppercase', letterSpacing:'0.8px', marginBottom:6 }}>
                  BAND TARIXI
                </div>
                <div style={{ fontSize:40, fontWeight:800, letterSpacing:'-1px' }}>
                  {best ? best.score_label : '0.0'}
                </div>
                <div style={{ fontSize:13, color:'#8A8680', marginTop:4 }}>
                  Maqsad: 7.0 · {best ? `${(7-parseFloat(best.score_raw||0)).toFixed(1)} band qoldi` : '7.0 band masofada'}
                </div>
              </div>
              <div style={{ fontSize:24 }}>🎯</div>
            </div>

            {history.length === 0 ? (
              <div style={{
                background:'#FEF2F1', borderRadius:12, padding:'16px 20px',
                textAlign:'center', color:'#8A8680', fontSize:14
              }}>
                To'liq mock topshiring — band tarixi shu yerda ko'rinadi
              </div>
            ) : (
              <div style={{ display:'flex', gap:12, overflowX:'auto' }}>
                {history.slice(0,6).map((s,i) => (
                  <div key={i} style={{
                    minWidth:80, background:'#F8F7F4', borderRadius:12,
                    padding:'12px', textAlign:'center', flexShrink:0
                  }}>
                    <div style={{ fontSize:18, fontWeight:800, color:'#E63329' }}>
                      {s.score_label}
                    </div>
                    <div style={{ fontSize:11, color:'#8A8680', marginTop:2 }}>
                      {s.exam_type?.replace('_',' ').toUpperCase()}
                    </div>
                    <div style={{ fontSize:11, color:'#C0BDB8' }}>{s.date}</div>
                  </div>
                ))}
              </div>
            )}

            <div style={{ display:'flex', gap:12, marginTop:16 }}>
              <div style={{ flex:1, background:'#F8F7F4', borderRadius:10, padding:'12px 16px' }}>
                <div style={{ fontSize:11, color:'#8A8680', marginBottom:4 }}>SO'NGGI</div>
                <div style={{ fontWeight:700 }}>{last?.score_label || '—'}</div>
              </div>
              <div style={{ flex:1, background:'#F8F7F4', borderRadius:10, padding:'12px 16px' }}>
                <div style={{ fontSize:11, color:'#8A8680', marginBottom:4 }}>ENG YAXSHI</div>
                <div style={{ fontWeight:700 }}>{best?.score_label || '—'}</div>
              </div>
              <div style={{ flex:1, background:'#FEF2F1', borderRadius:10, padding:'12px 16px' }}>
                <div style={{ fontSize:11, color:'#E63329', marginBottom:4 }}>MAQSAD</div>
                <div style={{ fontWeight:700, color:'#E63329' }}>7.0</div>
              </div>
            </div>
          </div>

          {/* Today route */}
          <div className="fade-up" style={{ background:'#fff', border:'1px solid #E8E6E1', borderRadius:20, padding:'28px' }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20 }}>
              <div>
                <div style={{ fontSize:11, fontWeight:600, color:'#E63329', letterSpacing:'0.8px', textTransform:'uppercase', marginBottom:4 }}>
                  BUGUNGI YO'NALISH
                </div>
                <div style={{ fontSize:18, fontWeight:700 }}>Birinchi mashqingizni boshlang</div>
              </div>
            </div>
            <div style={{ display:'grid', gap:12 }}>
              {todayRoute.map((r, i) => (
                <div key={i} onClick={() => nav(`/exam/${r.type}`)} style={{
                  display:'flex', alignItems:'center', justifyContent:'space-between',
                  padding:'16px 20px', borderRadius:14,
                  border:'1px solid #E8E6E1', cursor:'pointer',
                  transition:'all .2s',
                  background:'#FAFAF9',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor='#E63329'; e.currentTarget.style.background='#FEF2F1' }}
                onMouseLeave={e => { e.currentTarget.style.borderColor='#E8E6E1'; e.currentTarget.style.background='#FAFAF9' }}
                >
                  <div style={{ display:'flex', alignItems:'center', gap:14 }}>
                    <div style={{
                      width:36, height:36, background:'#F2F1EE', borderRadius:10,
                      display:'flex', alignItems:'center', justifyContent:'center',
                      fontSize:12, fontWeight:700, color:'#8A8680'
                    }}>{String(i+1).padStart(2,'0')}</div>
                    <div>
                      <div style={{ fontWeight:600, fontSize:15 }}>{r.n}</div>
                      <div style={{ fontSize:13, color:'#8A8680' }}>{r.sub}</div>
                    </div>
                  </div>
                  <span style={{ fontSize:18, color:'#C0BDB8' }}>→</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right */}
        <div>
          {/* Streak */}
          <div className="fade-up" style={{
            background:'#fff', border:'1px solid #E8E6E1', borderRadius:20, padding:'24px', marginBottom:16
          }}>
            <div style={{ display:'flex', gap:8, marginBottom:12 }}>
              {DAYS.map((d,i) => (
                <div key={i} style={{
                  flex:1, textAlign:'center',
                  opacity: i === new Date().getDay() ? 1 : 0.35
                }}>
                  <div style={{ fontSize:18, marginBottom:4 }}>🔥</div>
                  <div style={{ fontSize:10, color:'#8A8680' }}>{d}</div>
                </div>
              ))}
            </div>
            <div style={{ display:'flex', alignItems:'center', gap:12 }}>
              <div style={{ fontSize:32, fontWeight:800 }}>0</div>
              <div style={{ color:'#8A8680', fontSize:13 }}>kunlik streak</div>
            </div>
          </div>

          {/* Quick stats */}
          <div className="fade-up" style={{
            background:'#fff', border:'1px solid #E8E6E1', borderRadius:20, padding:'24px', marginBottom:16
          }}>
            <div style={{ fontWeight:700, marginBottom:16 }}>Tezkor statistika</div>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
              {[
                { label:"Topshirilgan", v:history.length, emoji:'📝' },
                { label:"Eng yaxshi %", v: best?`${best.percent}%`:'—', emoji:'🏆' },
                { label:"Jami XP", v:user?.xp||0, emoji:'⭐' },
                { label:"Daraja", v:`Lv.${user?.level||1}`, emoji:'🎓' },
              ].map(({ label, v, emoji }) => (
                <div key={label} style={{ background:'#F8F7F4', borderRadius:12, padding:'14px' }}>
                  <div style={{ fontSize:20, marginBottom:4 }}>{emoji}</div>
                  <div style={{ fontWeight:700, fontSize:18 }}>{v}</div>
                  <div style={{ fontSize:11, color:'#8A8680' }}>{label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Exam countdown */}
          <div className="fade-up" style={{
            background:'#fff', border:'1px solid #E8E6E1', borderRadius:20, padding:'24px'
          }}>
            <div style={{ display:'flex', gap:10, alignItems:'center', marginBottom:12 }}>
              <span style={{ fontSize:20 }}>📅</span>
              <div style={{ fontSize:11, fontWeight:600, color:'#8A8680', textTransform:'uppercase', letterSpacing:'0.8px' }}>
                IMTIHON SANA
              </div>
            </div>
            <div style={{ fontWeight:700, fontSize:16, marginBottom:12 }}>Sana belgilanmagan</div>
            <button style={{
              width:'100%', padding:'12px', borderRadius:10,
              background:'#E63329', border:'none', color:'#fff',
              fontSize:14, fontWeight:600, cursor:'pointer'
            }}>
              Sana qo'yish
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}