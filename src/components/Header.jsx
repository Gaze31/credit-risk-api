import { Shield, Circle, Github } from 'lucide-react'

export default function Header({ health }) {
  const isHealthy = health?.status === 'healthy'
  const statusColor = isHealthy ? 'text-emerald-600' : health ? 'text-red-500' : 'text-slate-400'
  const statusBg = isHealthy ? 'bg-emerald-50 border-emerald-200' : health ? 'bg-red-50 border-red-200' : 'bg-slate-50 border-slate-200'
  const statusText = isHealthy ? 'API Online' : health ? 'API Offline' : 'Checking...'

  return (
    <header className="bg-white border-b border-slate-200">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-8 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-600 rounded-xl shadow-sm">
              <Shield className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Credit Risk Scorer</h1>
              <p className="text-sm text-slate-500">ML-powered loan default prediction</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <a
              href="https://github.com/Gaze31/credit-risk-api"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900 border border-slate-200 hover:border-slate-300 rounded-lg px-3 py-1.5 transition-colors"
            >
              <Github size={16} /> Source
            </a>
            <div className={`flex items-center gap-2 text-sm border rounded-full px-3 py-1.5 ${statusBg}`}>
              <Circle size={8} className={`fill-current ${statusColor}`} />
              <span className={`font-medium ${statusColor}`}>{statusText}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
