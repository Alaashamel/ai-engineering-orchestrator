import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="text-6xl font-bold text-gray-600 mb-4">404</h1>
      <p className="text-gray-400 mb-6">Page not found</p>
      <Link to="/" className="text-blue-400 hover:text-blue-300">
        &larr; Back to Dashboard
      </Link>
    </div>
  )
}
