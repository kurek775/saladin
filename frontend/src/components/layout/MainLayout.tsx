import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

export function MainLayout() {
  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-primary/20">
      {/* Subtle background glow */}
      <div className="fixed inset-0 pointer-events-none opacity-20 pointer-events-none select-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-green-600 blur-[100px] rounded-full" />
      </div>

      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 relative z-10 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth scrollbar-thin">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
