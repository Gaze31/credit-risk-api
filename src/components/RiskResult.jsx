import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { AlertTriangle, CheckCircle, XCircle, AlertCircle, ShieldAlert } from 'lucide-react'

const TIER_CONFIG = {
  LOW: { color: '#10b981', bg: 'bg-emerald-900/20', border: 'border-emerald-700', icon: CheckCircle },
  MODERATE: { color: '#f59e0b', bg: 'bg-amber-900/20', border: 'border-amber-700', icon: AlertCircle },
  HIGH: { color: '#ef4444', bg: 'bg-red-900/20', border: 'border-red-700', icon: AlertTriangle },
  'VERY HIGH': { color: '#dc2626', bg: 'bg-red-900/30', border: 'border-red-600', icon: XCircle },
  CRITICAL: { color: '#7f1d1d', bg: 'bg-red-950/40', border: 'border-red-800', icon: ShieldAlert },
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
      <div className={`${tier.bg} border ${tier.border} rounded-xl p-5`}>
        <div className="flex items-start gap-4">
          <TierIcon size={32} style={{ color: tier.color }} className="mt-1 flex-shrink-0" />
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <span className="text-2xl font-bold" style={{ color: tier.color }}>
                {data.risk_tier}
              </span>
              <span className="text-sm text-gray-400">risk</span>
            </div>
            <p className="text-gray-300 text-sm">{data.recommendation}</p>
            <p className="text-gray-500 text-xs mt-1">Confidence: {data.confidence}</p>
          </div>
        </div>
      </div>

      {/* Score Cards */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center">
          <p className="text-xs text-gray-500 mb-1">Default Probability</p>
          <p className="text-2xl font-bold" style={{ color: tier.color }}>
            {(data.default_probability * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center">
          <p className="text-xs text-gray-500 mb-1">Credit Score</p>
          <p className="text-2xl font-bold text-white">{data.risk_score}</p>
          <div className="w-full bg-gray-800 rounded-full h-1.5 mt-2">
            <div
              className="h-1.5 rounded-full transition-all duration-500"
              style={{
                width: `${scorePercent}%`,
                backgroundColor: tier.color
              }}
            />
          </div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-center">
          <p className="text-xs text-gray-500 mb-1">Risk Tier</p>
          <p className="text-2xl font-bold" style={{ color: tier.color }}>
            {data.risk_tier.charAt(0)}
          </p>
        </div>
      </div>

      {/* Feature Importance Chart */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 className="text-sm font-medium text-gray-300 mb-4">Top Risk Drivers</h3>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 80, right: 20 }}>
            <XAxis type="number" tick={{ fill: '#6b7280', fontSize: 11 }} tickFormatter={v => `${v}%`} />
            <YAxis type="category" dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} width={75} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              labelStyle={{ color: '#e5e7eb' }}
              formatter={v => [`${v}%`, 'Importance']}
            />
            <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={i === 0 ? tier.color : '#4b5563'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Input Summary */}
      {data.input_summary && (
        <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
          <h3 className="text-xs font-medium text-gray-500 mb-2">Input Summary</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(data.input_summary).map(([key, val]) => (
              <div key={key} className="flex justify-between">
                <span className="text-gray-500">{key.replace(/_/g, ' ')}</span>
                <span className="text-gray-300 font-mono">
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
