import { Clock } from 'lucide-react'

const TIER_COLORS = {
  LOW: 'text-emerald-600 bg-emerald-50 border-emerald-200',
  MODERATE: 'text-amber-600 bg-amber-50 border-amber-200',
  HIGH: 'text-red-600 bg-red-50 border-red-200',
  'VERY HIGH': 'text-red-700 bg-red-50 border-red-300',
  CRITICAL: 'text-red-800 bg-red-100 border-red-300',
}

export default function PredictionHistory({ history }) {
  if (history.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-white border border-dashed border-slate-300 rounded-2xl text-slate-400">
        <div className="text-center">
          <Clock size={40} className="mx-auto mb-3 opacity-40" />
          <p className="font-medium text-slate-500">No predictions yet</p>
          <p className="text-sm mt-1">Submit a loan application to start building history</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-slate-900">Prediction History</h2>
        <span className="text-sm text-slate-500">{history.length} prediction{history.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="overflow-x-auto bg-white border border-slate-200 rounded-2xl shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Time</th>
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Loan</th>
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Rate</th>
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Income</th>
              <th className="text-left py-3 px-4 text-slate-500 font-medium">DTI</th>
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Default Prob</th>
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Score</th>
              <th className="text-left py-3 px-4 text-slate-500 font-medium">Tier</th>
            </tr>
          </thead>
          <tbody>
            {history.map((entry, i) => (
              <tr key={i} className="border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-colors">
                <td className="py-3 px-4 text-slate-500 font-mono text-xs">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </td>
                <td className="py-3 px-4 text-slate-700">
                  ${entry.input?.loan_amnt?.toLocaleString() ?? '-'}
                </td>
                <td className="py-3 px-4 text-slate-700">
                  {entry.input?.int_rate ?? '-'}%
                </td>
                <td className="py-3 px-4 text-slate-700">
                  ${entry.input?.annual_inc?.toLocaleString() ?? '-'}
                </td>
                <td className="py-3 px-4 text-slate-700">
                  {entry.input?.dti ?? '-'}
                </td>
                <td className="py-3 px-4 font-mono text-slate-800">
                  {(entry.default_probability * 100).toFixed(1)}%
                </td>
                <td className="py-3 px-4 font-bold text-slate-900">
                  {entry.risk_score}
                </td>
                <td className="py-3 px-4">
                  <span className={`inline-block px-2.5 py-0.5 rounded-full border text-xs font-semibold ${TIER_COLORS[entry.risk_tier] || 'text-slate-500 bg-slate-50 border-slate-200'}`}>
                    {entry.risk_tier}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
