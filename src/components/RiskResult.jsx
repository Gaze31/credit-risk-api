import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { AlertTriangle, CheckCircle, XCircle, AlertCircle, ShieldAlert } from 'lucide-react'

const TIER_CONFIG = {
  LOW: { color: '#059669', bg: 'bg-emerald-50', border: 'border-emerald-200', icon: CheckCircle },
  MODERATE: { color: '#d97706', bg: 'bg-amber-50', border: 'border-amber-200', icon: AlertCircle },
  HIGH: { color: '#dc2626', bg: 'bg-red-50', border: 'border-red-200', icon: AlertTriangle },
  'VERY HIGH': { color: '#b91c1c', bg: 'bg-red-50', border: 'border-red-300', icon: XCircle },
  CRITICAL: { color: '#991b1b', bg: 'bg-red-100', border: 'border-red-300', icon: ShieldAlert },
}

export default function RiskResult({ data }) {
  const tier = TIER_CONFIG[data.risk_tier] || TIER_CONFIG.MODERATE
  const TierIcon = tier.icon

  // Feature importance chart data
  const chartData = Object.entries(data.feature_importance).map(([name, value]) => ({
    name: name.replace(/_/g, ' '),
    importance: parseFloat((value * 100).toFixed(1))
  }))

  // Risk score gauge percentage (300-850 scale)
  const scorePercent = ((data.risk_score - 300) / 550) * 100

  return (
    <div className="space-y-4">
      {/* Risk Tier Banner */}
      <div className={`${tier.bg} border ${tier.border} rounded-2xl p-5 shadow-sm`}>
        <div className="flex items-start gap-4">
          <TierIcon size={32} style={{ color: tier.color }} className="mt-1 flex-shrink-0" />
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <span className="text-2xl font-bold" style={{ color: tier.color }}>
                {data.risk_tier}
              </span>
              <span className="text-sm text-slate-500">risk</span>
            </div>
            <p className="text-slate-700 text-sm">{data.recommendation}</p>
            <p className="text-slate-500 text-xs mt-1">Confidence: {data.confidence}</p>
          </div>
        </div>
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-white border border-slate-200 rounded-xl p-4 text-center shadow-sm">
          <p className="text-xs text-slate-500 mb-1">Default Probability</p>
          <p className="text-2xl font-bold" style={{ color: tier.color }}>
            {(data.default_probability * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 text-center shadow-sm">
          <p className="text-xs text-slate-500 mb-1">Credit Score</p>
          <p className="text-2xl font-bold text-slate-900">{data.risk_score}</p>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2">
            <div
              className="h-1.5 rounded-full transition-all duration-500"
              style={{
                width: `${scorePercent}%`,
                backgroundColor: tier.color
              }}
            />
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 text-center shadow-sm">
          <p className="text-xs text-slate-500 mb-1">Risk Tier</p>
          <p className="text-2xl font-bold" style={{ color: tier.color }}>
            {data.risk_tier.charAt(0)}
          </p>
        </div>
      </div>

      {/* Feature Importance Chart */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-700 mb-4">Top Risk Drivers</h3>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 80, right: 20 }}>
            <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={v => `${v}%`} />
            <YAxis type="category" dataKey="name" tick={{ fill: '#475569', fontSize: 12 }} width={75} />
            <Tooltip
              contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
              labelStyle={{ color: '#0f172a' }}
              formatter={v => [`${v}%`, 'Importance']}
            />
            <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={i === 0 ? tier.color : '#cbd5e1'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Input Summary */}
      {data.input_summary && (
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <h3 className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">Input Summary</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(data.input_summary).map(([key, val]) => (
              <div key={key} className="flex justify-between">
                <span className="text-slate-500">{key.replace(/_/g, ' ')}</span>
                <span className="text-slate-800 font-mono">
                  {typeof val === 'number' && key.includes('income') ? `$${val.toLocaleString()}` :
                   typeof val === 'number' && key.includes('amount') ? `$${val.toLocaleString()}` :
                   typeof val === 'number' && key.includes('rate') ? `${val}%` :
                   val}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
