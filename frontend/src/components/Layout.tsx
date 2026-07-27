import React from 'react'
import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Search, Tags, Sparkles, LogOut } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/audits', label: 'Audits', icon: Search },
  { to: '/keywords', label: 'Keywords', icon: Tags },
  { to: '/agent', label: 'AI Agent', icon: Sparkles },
]

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <a href="/" className="text-xl font-bold border-b border-slate-800 block p-6 hover:opacity-80">
          SEO/GEO AI
        </a>
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/dashboard'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition ${
                  isActive ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-800">
          <div className="text-xs text-slate-400 mb-2 truncate">{user?.email}</div>
          <button
            onClick={logout}
            className="flex items-center gap-2 text-sm text-slate-300 hover:text-white"
          >
            <LogOut size={16} /> Log out
          </button>
        </div>
      </aside>
      <main className="flex-1 bg-gray-100 overflow-y-auto">{children}</main>
    </div>
  )
}

export default Layout
