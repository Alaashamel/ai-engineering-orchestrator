import { NavLink, Outlet } from 'react-router-dom'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
    isActive
      ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
      : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800/50 border border-transparent'
  }`

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-950 text-gray-100 overflow-hidden">
      <aside className="w-60 border-r border-gray-800/60 flex flex-col shrink-0">
        <div className="p-5 border-b border-gray-800/40">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold">
              AS
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-tight leading-tight">
                AI Software Co.
              </h1>
              <p className="text-[10px] text-gray-500 mt-0.5">Control Center</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          <NavLink to="/" end className={linkClass}>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Dashboard
          </NavLink>
          <NavLink to="/projects" className={linkClass}>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            Projects
          </NavLink>
        </nav>
        <div className="p-4 border-t border-gray-800/40 text-[11px] text-gray-600">
          v0.1.0
        </div>
      </aside>
      <div className="flex-1 flex flex-col min-w-0">
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
        <footer className="border-t border-gray-800/40 px-6 py-3 text-center text-[11px] text-gray-600 shrink-0">
          v0.1.0 &middot; AI Software Engineering Co. &middot; Autonomous Agent System
        </footer>
      </div>
    </div>
  )
}
