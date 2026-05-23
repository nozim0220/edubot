import React, { useState, useEffect, createContext, useContext } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Login     from './pages/Login'
import Home      from './pages/Home'
import Tests     from './pages/Tests'
import ExamPage  from './pages/ExamPage'
import Results   from './pages/Results'
import Progress  from './pages/Progress'
import Sidebar   from './components/Sidebar'

export const AppCtx = createContext(null)
export const useApp = () => useContext(AppCtx)

const API = import.meta.env.VITE_API_URL || '/mock-api'

function Layout({ children }) {
  return (
    <div style={{ display:'flex', minHeight:'100vh' }}>
      <Sidebar />
      <main style={{ flex:1, marginLeft:248, minHeight:'100vh' }}>
        {children}
      </main>
    </div>
  )
}

export default function App() {
  const [user,    setUser]    = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const t = localStorage.getItem('token')
    if (!t) { setLoading(false); return }
    fetch(`${API}/auth/me/`, { headers:{ Authorization:`Bearer ${t}` } })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setUser(d) })
      .finally(() => setLoading(false))
  }, [])

  const login  = (u, t) => { localStorage.setItem('token', t); setUser(u) }
  const logout = ()     => { localStorage.removeItem('token'); setUser(null) }

  if (loading) return (
    <div style={{ display:'flex', alignItems:'center', justifyContent:'center',
      height:'100vh', background:'#F8F7F4', gap:12, flexDirection:'column' }}>
      <div style={{ width:36, height:36, border:'3px solid #E8E6E1',
        borderTop:'3px solid #E63329', borderRadius:'50%' }} className="spin"/>
      <span style={{ color:'#8A8680', fontSize:13 }}>Yuklanmoqda...</span>
    </div>
  )

  return (
    <AppCtx.Provider value={{ user, login, logout, API }}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={!user ? <Login/> : <Navigate to="/"/>}/>
          <Route path="/" element={user ? <Layout><Home/></Layout> : <Navigate to="/login"/>}/>
          <Route path="/tests" element={user ? <Layout><Tests/></Layout> : <Navigate to="/login"/>}/>
          <Route path="/tests/:cat" element={user ? <Layout><Tests/></Layout> : <Navigate to="/login"/>}/>
          <Route path="/exam/:type" element={user ? <ExamPage/> : <Navigate to="/login"/>}/>
          <Route path="/results/:id" element={user ? <Layout><Results/></Layout> : <Navigate to="/login"/>}/>
          <Route path="/progress" element={user ? <Layout><Progress/></Layout> : <Navigate to="/login"/>}/>
        </Routes>
      </BrowserRouter>
    </AppCtx.Provider>
  )
}