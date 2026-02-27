import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { LayoutDashboard, ListTodo, Bot, Settings } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '../../utils'
import { Logo } from '../common/Logo'
import { SettingsModal } from '../settings/SettingsModal'
import { useStore } from '../../store'

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/tasks', label: 'Tasks', icon: ListTodo },
  { to: '/agents', label: 'Agents', icon: Bot },
]

export function Sidebar() {
  const [settingsOpen, setSettingsOpen] = useState(false)
  const wsConnected = useStore((s) => s.wsConnected)

  return (
    <aside className="w-64 bg-card border-r flex flex-col h-full">
      <div className="p-6 flex items-center gap-3">
        <div className="size-8 flex items-center justify-center">
          <Logo size={32} />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight">Saladin</h1>
          <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Orchestration</p>
        </div>
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200 relative',
                isActive
                  ? 'text-primary bg-primary/10'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              )
            }
          >
            {({ isActive }) => (
              <>
                <link.icon className={cn('size-4 transition-transform group-hover:scale-110', isActive && 'text-primary')} />
                {link.label}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute left-0 w-1 h-5 bg-primary rounded-r-full"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 mt-auto space-y-2">
        <div className="flex items-center gap-2 px-3 py-1.5 text-xs text-muted-foreground">
          <span className={cn(
            'size-2 rounded-full',
            wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
          )} />
          {wsConnected ? 'Connected' : 'Disconnected'}
        </div>
        <button
          onClick={() => setSettingsOpen(true)}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-all duration-200"
        >
          <Settings className="size-4" />
          Settings
        </button>
      </div>

      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </aside>
  )
}
