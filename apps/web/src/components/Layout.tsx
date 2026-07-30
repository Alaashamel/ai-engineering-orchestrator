import { NavLink, Outlet } from 'react-router-dom'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `block px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
    isActive
      ? 'bg-blue-600 text-white'
      : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
  }`

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      <aside className="w-64 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-lg font-bold tracking-tight">
            AI Software Engineering Co.
          </h1>
          <p className="text-xs text-gray-500 mt-1">Control Center</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          <NavLink to="/" end className={linkClass}>
            Dashboard
          </NavLink>
          <NavLink to="/projects" className={linkClass}>
            Projects
          </NavLink>
        </nav>
        <div className="p-4 border-t border-gray-800 text-xs text-gray-600">
          v0.1.0
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
