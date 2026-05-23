import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useApp } from '../App'

const NAV = [
  { to:'/',         icon:'🏠', label:'Home' },
  { to:'/tests',    icon:'📋', label:'Tests' },
  { to:'/progress', icon:'📊', label:'Progress' },
]

export default function Sidebar() {
  const { user, logout } = useApp()
  const nav = useNavigate()

  return (
    <aside style={{
      width:248, height:'100vh', position:'fixed', left:0, top:0,
      background:'#FFFFFF', borderRight:'1px solid #E8E6E1',
      display:'flex', flexDirection:'column', zIndex:50,
    }}>
      {/* Logo */}
      <div style={{ padding:'24px 20px 20px', borderBottom:'1px solid #E8E6E1' }}>
        <div style={{ display:'flex', alignItems:'center', gap:10 }}>
          <div style={{
            width:36, height:36, background:'#E63329', borderRadius:10,
            display:'flex', alignItems:'center', justifyContent:'center',
            color:'#fff', fontWeight:800, fontSize:16,
          }}>A</div>
          <div>
            <div style={{ fontWeight:800, fontSize:15, letterSpacing:'-0.3px' }}>ABT</div>
            <div style={{ fontSize:11, color:'#8A8680', letterSpacing:'0.5px' }}>FULL PREP</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex:1, padding:'12px 12px' }}>
        {NAV.map(({ to, icon, label }) => (
          <NavLink key={to} to={to} end={to==='/'} style={({ isActive }) => ({
            display:'flex', alignItems:'center', gap:10,
            padding:'10px 12px', borderRadius:10, marginBottom:2,
            textDecoration:'none', fontSize:14, fontWeight:500,
            background: isActive ? '#FEF2F1' : 'transparent',
            color: isActive ? '#E63329' : '#4A4845',
            transition:'all .15s',
          })}>
            <span style={{ fontSize:17 }}>{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div style={{ padding:'16px 16px', borderTop:'1px solid #E8E6E1' }}>
        <div style={{
          display:'flex', alignItems:'center', gap:10,
          padding:'10px 12px', borderRadius:10,
          background:'#F8F7F4', marginBottom:8,
        }}>
          <div style={{
            width:32, height:32, borderRadius:'50%',
            background:'#E63329', display:'flex', alignItems:'center',
            justifyContent:'center', color:'#fff', fontWeight:700, fontSize:13,
          }}>
            {user?.name?.charAt(0) || 'U'}
          </div>
          <div style={{ flex:1, overflow:'hidden' }}>
            <div style={{ fontSize:13, fontWeight:600, overflow:'hidden',
              textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
              {user?.name || 'Foydalanuvchi'}
            </div>
            <div style={{ fontSize:11, color:'#8A8680' }}>
              XP: {user?.xp || 0}
            </div>
          </div>
        </div>
        <button onClick={logout} style={{
          width:'100%', padding:'8px', borderRadius:8, border:'1px solid #E8E6E1',
          background:'transparent', fontSize:13, color:'#8A8680', cursor:'pointer',
        }}>
          Chiqish
        </button>
      </div>
    </aside>
  )
}