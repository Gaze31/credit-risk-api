import { useState, useEffect } from 'react'
import { Activity, Shield, BarChart3, Info, Cpu, Database, GitBranch } from 'lucide-react'
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

const HIGHLIGHTS = [
  { icon: Cpu, title: 'Gradient Boosting', text: 'Ensemble model with 5-fold cross-validation for stable, reliable predictions.' },
  { icon: Database, title: 'Real Lending Data', text: 'Trained on Lending Club loan records with real-world default outcomes.' },
  { icon: GitBranch, title: 'Production API', text: 'FastAPI backend with health checks, Swagger docs, and full test coverage.' },
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
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header health={apiHealth} />

      {/* Hero */}
      {activeTab === 'predict' && !result && (
        <section className="bg-gradient-to-b from-emerald-50/70 to-slate-50 border-b border-slate-200">
          <div className="max-w-screen-2xl mx-auto px-4 sm:px-8 py-10 lg:py-14">
            <div className="max-w-3xl">
              <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 tracking-tight leading-tight">
                Instant loan default risk assessment,{' '}
                <span className="text-emerald-600">powered by machine learning</span>
              </h2>
              <p className="mt-4 text-lg text-slate-600">
                Enter a borrower profile and get a default probability, credit score estimate,
                risk tier, and the exact factors driving the decision — in under a second.
              </p>
            </div>
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6">
              {HIGHLIGHTS.map(({ icon: Icon, title, text }) => (
                <div key={title} className="flex items-start gap-3 bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                  <div className="p-2 bg-emerald-50 rounded-lg shrink-0">
                    <Icon size={18} className="text-emerald-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900 text-sm">{title}</p>
                    <p className="text-sm text-slate-500 mt-0.5">{text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Tab Navigation */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-8">
          <div className="flex gap-1 overflow-x-auto">
            {TABS.map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-emerald-600 text-emerald-700'
                      : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'
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
      <main className="max-w-screen-2xl mx-auto px-4 sm:px-8 py-8 w-full flex-1">
        {activeTab === 'predict' && (
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
            <div className="lg:col-span-2">
              <LoanForm onSubmit={handlePredict} loading={loading} />
            </div>
            <div className="lg:col-span-3">
              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                  {error}
                </div>
              )}
              {result && <RiskResult data={result} />}
              {!result && !error && (
                <div className="flex items-center justify-center h-full min-h-[400px] bg-white border border-dashed border-slate-300 rounded-2xl text-slate-400">
                  <div className="text-center px-6">
                    <Shield size={48} className="mx-auto mb-4 opacity-40" />
                    <p className="text-lg font-medium text-slate-500">Your risk assessment will appear here</p>
                    <p className="text-sm mt-1">Fill in the loan application or try one of the presets, then hit "Assess Risk"</p>
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
          <div className="max-w-4xl">
            <h2 className="text-2xl font-bold text-slate-900 mb-2">API Documentation</h2>
            <p className="text-slate-500 mb-6">RESTful endpoints served by FastAPI. All responses are JSON.</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h3 className="font-mono text-sm mb-1"><span className="text-white bg-emerald-600 rounded px-1.5 py-0.5 text-xs font-bold mr-2">POST</span><span className="text-slate-800">/api/predict</span></h3>
                <p className="text-slate-500 text-sm mt-2">Submit loan application for risk scoring. Returns default probability, risk tier, credit score, and feature importances.</p>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h3 className="font-mono text-sm mb-1"><span className="text-white bg-sky-600 rounded px-1.5 py-0.5 text-xs font-bold mr-2">GET</span><span className="text-slate-800">/api/health</span></h3>
                <p className="text-slate-500 text-sm mt-2">Health check endpoint. Returns model status and version.</p>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h3 className="font-mono text-sm mb-1"><span className="text-white bg-sky-600 rounded px-1.5 py-0.5 text-xs font-bold mr-2">GET</span><span className="text-slate-800">/api/model-info</span></h3>
                <p className="text-slate-500 text-sm mt-2">Model metadata, training metrics, feature importances, and confusion matrix.</p>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h3 className="font-mono text-sm mb-1"><span className="text-white bg-sky-600 rounded px-1.5 py-0.5 text-xs font-bold mr-2">GET</span><span className="text-slate-800">/api/sample</span></h3>
                <p className="text-slate-500 text-sm mt-2">Sample loan applications (low, moderate, high risk) for testing.</p>
              </div>
            </div>
            <div className="mt-6 p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
              <p className="text-slate-600 text-sm">
                Full interactive docs available at{' '}
                <a href="/api/docs" className="text-emerald-700 hover:text-emerald-800 font-medium underline">/api/docs</a>{' '}
                (Swagger UI)
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 mt-12">
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-8 text-center text-slate-500 text-sm">
          Credit Risk Scoring API v2.0 — Gradient Boosting on Lending Club data
          <br />
          Built by Sumedha Hundekar |{' '}
          <a href="https://github.com/Gaze31/credit-risk-api" className="text-slate-500 hover:text-slate-800 underline">
            GitHub
          </a>
        </div>
      </footer>
    </div>
  )
}
