import { useState } from 'react'
import { Send, RotateCcw, Loader2 } from 'lucide-react'

const FIELD_CONFIG = [
  { key: 'loan_amnt', label: 'Loan Amount ($)', min: 500, max: 40000, step: 500, default: 15000, description: 'Requested loan amount' },
  { key: 'int_rate', label: 'Interest Rate (%)', min: 5, max: 31, step: 0.25, default: 12.5, description: 'Assigned interest rate' },
  { key: 'annual_inc', label: 'Annual Income ($)', min: 10000, max: 500000, step: 1000, default: 60000, description: 'Borrower annual income' },
  { key: 'dti', label: 'DTI Ratio', min: 0, max: 50, step: 0.5, default: 18.5, description: 'Debt-to-income ratio' },
  { key: 'delinq_2yrs', label: 'Delinquencies (2yr)', min: 0, max: 10, step: 1, default: 0, description: 'Delinquencies in past 2 years' },
  { key: 'inq_last_6mths', label: 'Recent Inquiries', min: 0, max: 8, step: 1, default: 1, description: 'Credit inquiries in 6 months' },
  { key: 'open_acc', label: 'Open Accounts', min: 1, max: 50, step: 1, default: 8, description: 'Number of open credit lines' },
  { key: 'revol_util', label: 'Revolving Util (%)', min: 0, max: 100, step: 1, default: 45, description: 'Credit utilization rate' },
  { key: 'total_acc', label: 'Total Accounts', min: 2, max: 80, step: 1, default: 15, description: 'Total credit lines ever' },
  { key: 'emp_length', label: 'Employment (years)', min: 0, max: 10, step: 1, default: 3, description: 'Years at current employer' },
]

const PRESETS = {
  low: { loan_amnt: 10000, int_rate: 7.5, annual_inc: 95000, dti: 8, delinq_2yrs: 0, inq_last_6mths: 0, open_acc: 12, revol_util: 18, total_acc: 25, emp_length: 8 },
  moderate: { loan_amnt: 20000, int_rate: 15, annual_inc: 55000, dti: 22, delinq_2yrs: 1, inq_last_6mths: 2, open_acc: 8, revol_util: 55, total_acc: 15, emp_length: 3 },
  high: { loan_amnt: 35000, int_rate: 26, annual_inc: 30000, dti: 38, delinq_2yrs: 3, inq_last_6mths: 5, open_acc: 15, revol_util: 88, total_acc: 8, emp_length: 0 },
}

const getDefaults = () => Object.fromEntries(FIELD_CONFIG.map(f => [f.key, f.default]))

export default function LoanForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState(getDefaults())

  const handleChange = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: Number(value) }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleReset = () => setFormData(getDefaults())
  const handlePreset = (preset) => setFormData(PRESETS[preset])

  return (
    <form onSubmit={handleSubmit} className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-white">Loan Application</h2>
        <div className="flex gap-2">
          {Object.keys(PRESETS).map(p => (
            <button
              key={p}
              type="button"
              onClick={() => handlePreset(p)}
              className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                p === 'low' ? 'border-emerald-700 text-emerald-400 hover:bg-emerald-900/30' :
                p === 'moderate' ? 'border-amber-700 text-amber-400 hover:bg-amber-900/30' :
                'border-red-700 text-red-400 hover:bg-red-900/30'
              }`}
            >
              {p} risk
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {FIELD_CONFIG.map(field => (
          <div key={field.key}>
            <label className="block text-xs font-medium text-gray-400 mb-1">
              {field.label}
            </label>
            <input
              type="number"
              min={field.min}
              max={field.max}
              step={field.step}
              value={formData[field.key]}
              onChange={e => handleChange(field.key, e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
            />
            <p className="text-xs text-gray-600 mt-0.5">{field.description}</p>
          </div>
        ))}
      </div>

      <div className="flex gap-3 mt-6">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-800 disabled:cursor-not-allowed text-white font-medium py-2.5 px-4 rounded-lg transition-colors"
        >
          {loading ? (
            <><Loader2 size={16} className="animate-spin" /> Analyzing...</>
          ) : (
            <><Send size={16} /> Assess Risk</>
          )}
        </button>
        <button
          type="button"
          onClick={handleReset}
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-300 py-2.5 px-4 rounded-lg transition-colors"
        >
          <RotateCcw size={16} /> Reset
        </button>
      </div>
    </form>
  )
}
