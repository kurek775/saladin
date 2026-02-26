import { Activity, Bot, CircleDot, Sun, Moon, Monitor } from 'lucide-react'
import { useStore } from '../../store'
import type { Theme } from '../../store/themeSlice'
import { cn } from '../../utils'

const themeOrder: Theme[] = ['light', 'dark', 'system']
const themeIcon = { light: Sun, dark: Moon, system: Monitor } as const
const themeLabel = { light: 'Light', dark: 'Dark', system: 'System' } as const

export function Header() {
  const theme = useStore((s) => s.theme)
  const setTheme = useStore((s) => s.setTheme)
  const agentCount = useStore((s) => Object.keys(s.agents).length)
  const activeTaskCount = useStore((s) => {
    let count = 0
    for (const t of Object.values(s.tasks)) {
      if (t.status === 'running' || t.status === 'under_review' || t.status === 'revision') {
        count++
      }
    }
    return count
  })

  return (
    <header className="h-16 bg-card/50 backdrop-blur-md border-b flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex items-center gap-2">
        <Activity className="size-4 text-primary animate-pulse" />
        <span className="text-sm font-medium">System Status: <span className="text-green-500">Operational</span></span>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Bot className="size-4" />
          <span className="font-semibold text-foreground">{agentCount}</span>
          <span>agent{agentCount !== 1 ? 's' : ''}</span>
        </div>
        
        <div className="h-4 w-px bg-border" />
        
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <CircleDot className={cn("size-4", activeTaskCount > 0 ? "text-primary fill-primary/20" : "")} />
          <span className="font-semibold text-foreground">{activeTaskCount}</span>
          <span>active task{activeTaskCount !== 1 ? 's' : ''}</span>
        </div>

        <div className="h-4 w-px bg-border" />

        {(() => {
          const Icon = themeIcon[theme]
          return (
            <button
              type="button"
              onClick={() => {
                const idx = (themeOrder.indexOf(theme) + 1) % themeOrder.length
                setTheme(themeOrder[idx] ?? 'dark')
              }}
              className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
              title={`Theme: ${themeLabel[theme]}`}
            >
              <Icon className="size-4" />
              <span className="hidden sm:inline">{themeLabel[theme]}</span>
            </button>
          )
        })()}
      </div>
    </header>
  )
}
