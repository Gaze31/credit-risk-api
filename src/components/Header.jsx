import { Shield, Circle } from 'lucide-react'

export default function Header({ health }) {
  const isHealthy = health?.status === 'healthy'
  const statusColor = isHealthy ? 'text-emerald-400' : health ? 'text-red-400' : 'text-gray-500'
  const statusText = isHealthy ? 'Online' : health ? 'Offline' : 'Checking...'

  return (
    <header className="bg-gray-900 border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500/10 rounded-lg">
              <Shield className="text-emerald-400" size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Credit Risk Scorer</h1>
              <p className="text-sm text-gray-500">ML-powered loan default prediction</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Circle size={8} className={`fill-current ${statusColor}`} />
            <span className={statusColor}>{statusText}</span>
          </div>
        </div>
      </div>
    </header>
  )
}
