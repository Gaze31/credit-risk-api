import { useState, useEffect } from 'react'
import { Activity, Shield, BarChart3, Info } from 'lucide-react'
import LoanForm from './components/LoanForm'
import RiskResult from './components/RiskResult'
import PredictionHistory from './components/PredictionHistory'
import ModelMetrics from './components/ModelMetrics'
import Header from './components/Header'

const TABS = [
  { id: 'predict', label: 'Risk Scorer', icon: Shield },
  { id: 'history', label: 'History', icon: Activity },
  { id: 'model', label: 'Model Performance', icon: BarChart3 },
  { id: 'about', label: 'API Info', icon: Info },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('predict')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [modelInfo, setModelInfo] = useState(null)
  const [apiHealth, setApiHealth] = useState(null)

  const API_BASE = import.meta.env.VITE_API_URL || ''

  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then(r => r.json())
      .then(setApiHealth)
      .catch(() => setApiHealth({ status: 'unreachable', model_loaded: false }))

    fetch(`${API_BASE}/api/model-info`)
      .then(r => r.json())
      .then(setModelInfo)
      .catch(() => {})
  }, [])

  const handlePredict = async (formData) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Prediction failed')
      }
      const data = await res.json()
      setResult(data)
      setHistory(prev => [{
        ...data,
        input: formData,
        timestamp: new Date().toISOString()
      }, ...prev].slice(0, 50))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Header health={apiHealth} />

      {/* Tab Navigation */}
      <nav className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex gap-1 overflow-x-auto">
            {TABS.map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-emerald-500 text-emerald-400'
                      : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-600'
                  }`}
                >
                  <Icon size={16} />
                  {tab.label}
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {activeTab === 'predict' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <LoanForm onSubmit={handlePredict} loading={loading} />
            <div>
              {error && (
                <div className="mb-4 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
                  {error}
                </div>
              )}
              {result && <RiskResult data={result} />}
              {!result && !error && (
                <div className="flex items-center justify-center h-full min-h-[400px] text-gray-600">
                  <div className="text-center">
                    <Shield size={48} className="mx-auto mb-4 opacity-30" />
                    <p className="text-lg">Submit a loan application to see risk assessment</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <PredictionHistory history={history} />
        )}

        {activeTab === 'model' && (
          <ModelMetrics modelInfo={modelInfo} />
        )}

        {activeTab === 'about' && (
          <div className="max-w-2xl">
            <h2 className="text-2xl font-bold mb-6">API Documentation</h2>
            <div className="space-y-4">
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-5">
                <h3 className="text-emerald-400 font-mono text-sm mb-1">POST /api/predict</h3>
                <p className="text-gray-400 text-sm">Submit loan application for risk scoring. Returns default probability, risk tier, credit score, and feature importances.</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-5">
                <h3 className="text-emerald-400 font-mono text-sm mb-1">GET /api/health</h3>
                <p className="text-gray-400 text-sm">Health check endpoint. Returns model status and version.</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-5">
                <h3 className="text-emerald-400 font-mono text-sm mb-1">GET /api/model-info</h3>
                <p className="text-gray-400 text-sm">Model metadata, training metrics, feature importances, and confusion matrix.</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-5">
                <h3 className="text-emerald-400 font-mono text-sm mb-1">GET /api/sample</h3>
                <p className="text-gray-400 text-sm">Sample loan applications (low, moderate, high risk) for testing.</p>
              </div>
              <div className="mt-6 p-4 bg-gray-900 border border-gray-700 rounded-lg">
                <p className="text-gray-400 text-sm">
                  Full interactive docs available at{' '}
                  <a href="/api/docs" className="text-emerald-400 hover:text-emerald-300 underline">/api/docs</a>{' '}
                  (Swagger UI)
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 text-center text-gray-600 text-sm">
          Credit Risk Scoring API v2.0 — Gradient Boosting on Lending Club data
          <br />
          Built by Sumedha Hundekar |{' '}
          <a href="https://github.com/Gaze31/credit-risk-api" className="text-gray-500 hover:text-gray-300">
            GitHub
          </a>
        </div>
      </footer>
    </div>
  )
}
