import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MainLayout } from './components/layout/MainLayout'
import { DashboardPage } from './pages/DashboardPage'
import { LandingPage } from './pages/LandingPage'
import { TasksPage } from './pages/TasksPage'
import { TaskDetailPage } from './pages/TaskDetailPage'
import { AgentsPage } from './pages/AgentsPage'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import { SplashScreen } from './components/common/SplashScreen'
import { useWebSocket } from './hooks/useWebSocket'
import { useStore } from './store'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      gcTime: 10 * 60_000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function WebSocketProvider({ children }: { children: React.ReactNode }) {
  useWebSocket()
  return <>{children}</>
}

export default function App() {
  const theme = useStore((s) => s.theme)
  const setTheme = useStore((s) => s.setTheme)

  useEffect(() => {
    const apply = () => setTheme(theme)
    if (theme !== 'system') return
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    mq.addEventListener('change', apply)
    return () => mq.removeEventListener('change', apply)
  }, [theme, setTheme])

  return (
    <ErrorBoundary>
      <SplashScreen />
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <WebSocketProvider>
            <Routes>
              {/* Landing page — standalone, no layout */}
              <Route path="/" element={<LandingPage />} />

              {/* App routes — wrapped in MainLayout */}
              <Route element={<MainLayout />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/tasks" element={<TasksPage />} />
                <Route path="/tasks/:id" element={<TaskDetailPage />} />
                <Route path="/agents" element={<AgentsPage />} />
              </Route>
            </Routes>
          </WebSocketProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}
