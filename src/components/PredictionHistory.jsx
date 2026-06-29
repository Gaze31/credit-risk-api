import { Clock, Trash2 } from 'lucide-react'

const TIER_COLORS = {
  LOW: 'text-emerald-400',
  MODERATE: 'text-amber-400',
  HIGH: 'text-red-400',
  'VERY HIGH': 'text-red-500',
  CRITICAL: 'text-red-700',
}

export default function PredictionHistory({ history }) {
  if (history.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-600">
        <div className="text-center">
          <Clock size={40} className="mx-auto mb-3 opacity-30" />
          <p>No predictions yet</p>
          <p className="text-sm mt-1">Submit a loan application to start building history</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">Prediction History</h2>
        <span className="text-sm text-gray-500">{history.length} prediction{history.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left py-3 px-4 text-gray-500 font-medium">Time</th>
              <th className="text-left py-3 px-4 text-gray-500 font-medium">Loan</th>
              <th className="text-left py-3 px-4 text-gray-500 font-medium">Rate</th>
              <th className="text-left py-3 px-4 text-gray-500 font-medium">Income</th>
              <th className="text-left py-3 px-4 text-gray-500 font-medium">DTI</th>
              <th className="text-left py-3 px-4 text-gray-500 font-medium">Default Prob</th>
              <th className="text-left py-3 px-4 text-gray-500 font-medium">Score</th>
              <th className="text-left py-3 px-4 text-gray-500 font-medium">Tier</th>
            </tr>
          </thead>
          <tbody>
            {history.map((entry, i) => (
              <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-900/50 transition-colors">
                <td className="py-3 px-4 text-gray-500 font-mono text-xs">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </td>
                <td className="py-3 px-4 text-gray-300">
                  ${entry.input?.loan_amnt?.toLocaleString() ?? '-'}
                </td>
                <td className="py-3 px-4 text-gray-300">
                  {entry.input?.int_rate ?? '-'}%
                </td>
                <td className="py-3 px-4 text-gray-300">
                  ${entry.input?.annual_inc?.toLocaleString() ?? '-'}
                </td>
                <td className="py-3 px-4 text-gray-300">
                  {entry.input?.dti ?? '-'}
                </td>
                <td className="py-3 px-4 font-mono">
                  {(entry.default_probability * 100).toFixed(1)}%
                </td>
                <td className="py-3 px-4 font-bold text-white">
                  {entry.risk_score}
                </td>
                <td className={`py-3 px-4 font-semibold ${TIER_COLORS[entry.risk_tier] || 'text-gray-400'}`}>
                  {entry.risk_tier}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
