import { useState, useMemo } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, ListTodo, Bot, Settings, Sparkles, Play, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '../../utils'
import { Logo } from '../common/Logo'
import { SettingsModal } from '../settings/SettingsModal'
import { useStore } from '../../store'
import { launchScout } from '../../api/client'

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/tasks', label: 'Tasks', icon: ListTodo },
  { to: '/agents', label: 'Agents', icon: Bot },
]

export function Sidebar() {
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [scoutOpen, setScoutOpen] = useState(false)
  const [numTasks, setNumTasks] = useState(5)
  const [maxDepth, setMaxDepth] = useState(2)
  const [scoutAgentId, setScoutAgentId] = useState('')
  const [launching, setLaunching] = useState(false)
  const wsConnected = useStore((s) => s.wsConnected)
  const agents = useStore((s) => s.agents)
  const navigate = useNavigate()

  const workerAgents = useMemo(
    () => Object.values(agents).filter((a) => a.role === 'worker'),
    [agents]
  )

  async function handleLaunchScout() {
    setLaunching(true)
    try {
      const result = await launchScout({
        num_tasks: numTasks,
        max_depth: maxDepth,
        agent_id: scoutAgentId || undefined,
      })
      setScoutOpen(false)
      navigate(`/tasks/${result.task_id}`)
    } catch (e) {
      console.error('Scout launch failed:', e)
    } finally {
      setLaunching(false)
    }
  }

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

        {/* Self-Improve Button */}
        <div className="pt-4">
          <p className="px-3 pb-1.5 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Automation</p>
          <button
            onClick={() => setScoutOpen(!scoutOpen)}
            className={cn(
              'group flex items-center gap-3 px-3 py-2.5 w-full rounded-md text-sm font-medium transition-all duration-200',
              scoutOpen
                ? 'text-primary bg-primary/10'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            )}
          >
            <Sparkles className="size-4 transition-transform group-hover:scale-110" />
            Self-Improve
          </button>

          <AnimatePresence>
            {scoutOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="mx-2 mt-2 p-3 bg-muted/50 border rounded-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Configure Scout</span>
                    <button onClick={() => setScoutOpen(false)} className="text-muted-foreground hover:text-foreground">
                      <X className="size-3" />
                    </button>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Tasks: {numTasks}
                    </label>
                    <input
                      type="range"
                      min={1}
                      max={10}
                      value={numTasks}
                      onChange={(e) => setNumTasks(Number(e.target.value))}
                      className="w-full h-1 bg-muted rounded-full appearance-none cursor-pointer accent-primary"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                      Max Depth: {maxDepth}
                    </label>
                    <div className="flex gap-1">
                      {[1, 2, 3].map((d) => (
                        <button
                          key={d}
                          onClick={() => setMaxDepth(d)}
                          className={cn(
                            'flex-1 py-1 text-xs font-bold rounded transition-colors',
                            maxDepth === d
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-muted text-muted-foreground hover:bg-muted/80'
                          )}
                        >
                          {d}
                        </button>
                      ))}
                    </div>
                  </div>

                  {workerAgents.length > 0 && (
                    <div className="space-y-1">
                      <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                        Agent
                      </label>
                      <select
                        value={scoutAgentId}
                        onChange={(e) => setScoutAgentId(e.target.value)}
                        className="w-full text-xs bg-background border rounded px-2 py-1.5 text-foreground"
                      >
                        <option value="">Auto (first available)</option>
                        {workerAgents.map((a) => (
                          <option key={a.id} value={a.id}>
                            {a.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  <button
                    onClick={handleLaunchScout}
                    disabled={launching}
                    className="w-full flex items-center justify-center gap-2 py-2 text-xs font-bold uppercase tracking-wider bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
                  >
                    <Play className="size-3" />
                    {launching ? 'Launching...' : 'Launch'}
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
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
