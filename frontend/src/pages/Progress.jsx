import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../App'

const TABS = ['Reading','Listening','Writing','Mock']

export default function Progress() {
  const { API } = useApp()
  const nav = useNavigate()
  const token = localStorage.getItem('token')
  const [tab,     setTab]     = useState('Reading')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/history/`, { headers:{ Authorization:`Bearer ${token}` } })
      .then(r => r.json())
      .then(d => { if(Array.isArray(d)) setHistory(d) })
      .finally(() => setLoading(false))
  }, [])

  const filtered = history.filter(s => {
    if (tab==='Reading')   return s.exam_type?.includes('reading')
    if (tab==='Listening') return s.exam_type?.includes('listening')
    if (tab==='Writing')   return s.exam_type?.includes('writing')
    return true
  })

  return (
    <div style={{ padding:'32px 40px' }}>
      <h1 className="fade-up" style={{ fontSize:26, fontWeight:800, marginBottom:24 }}>
        📊 Progress
      </h1>

      {/* Tabs */}
      <div className="fade-up" style={{ display:'flex', gap:4, borderBottom:'1px solid #E8E6E1',
        marginBottom:28 }}>
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            padding:'10px 20px', fontSize:14, fontWeight:500,
            background:'transparent', border:'none', cursor:'pointer',
            color: tab===t ? '#E63329':'#8A8680',
            borderBottom: tab===t ? '2px solid #E63329' : '2px solid transparent',
            transition:'all .15s',
          }}>{t}</button>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign:'center', padding:60, color:'#8A8680' }}>Yuklanmoqda...</div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign:'center', padding:80 }}>
          <div style={{ fontSize:40, marginBottom:16 }}>📭</div>
          <p style={{ color:'#8A8680', marginBottom:20 }}>
            Hali {tab.toLowerCase()} testlari topshirilmagan
          </p>
          <button onClick={() => nav('/tests')} style={{
            padding:'12px 28px', background:'#E63329', border:'none',
            borderRadius:12, color:'#fff', fontSize:14, fontWeight:600, cursor:'pointer'
          }}>Testlarga o'tish →</button>
        </div>
      ) : (
        <div className="fade-up">
          <p style={{ color:'#8A8680', marginBottom:20, fontSize:14 }}>
            Jami: <b>{filtered.length}</b> ta urinish
          </p>
          <div style={{ display:'grid', gap:12 }}>
            {filtered.map(s => {
              const g = s.grade || {}
              return (
                <div key={s.id}
                  onClick={() => nav(`/results/${s.id}`)}
                  style={{
                    background:'#fff', border:'1px solid #E8E6E1', borderRadius:16,
                    padding:'20px 24px', cursor:'pointer', transition:'all .2s',
                    display:'flex', justifyContent:'space-between', alignItems:'center',
                  }}
                  onMouseEnter={e => e.currentTarget.style.borderColor='#E63329'}
                  onMouseLeave={e => e.currentTarget.style.borderColor='#E8E6E1'}
                >
                  <div style={{ display:'flex', alignItems:'center', gap:16 }}>
                    <div style={{ fontSize:28 }}>{g.emoji}</div>
                    <div>
                      <div style={{ fontWeight:600 }}>{s.exam_name}</div>
                      <div style={{ fontSize:13, color:'#8A8680' }}>{s.date}</div>
                    </div>
                  </div>
                  <div style={{ textAlign:'right' }}>
                    <div style={{ fontSize:22, fontWeight:800, color:g.color }}>
                      {s.score_label}
                    </div>
                    <div style={{ fontSize:13, color:'#8A8680' }}>
                      {s.correct}/{s.total} ({s.percent}%)
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}