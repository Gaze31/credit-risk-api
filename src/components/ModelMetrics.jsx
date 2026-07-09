import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Brain, Target, TrendingUp } from 'lucide-react'

export default function ModelMetrics({ modelInfo }) {
  if (!modelInfo) {
    return (
      <div className="flex items-center justify-center h-64 bg-white border border-dashed border-slate-300 rounded-2xl text-slate-400">
        <div className="text-center">
          <Brain size={40} className="mx-auto mb-3 opacity-40" />
          <p className="font-medium text-slate-500">Loading model information...</p>
          <p className="text-sm mt-1">Make sure the API is running</p>
        </div>
      </div>
    )
  }

  const { metrics, training_info, model_type, features } = modelInfo

  // Feature importance chart
  const featureData = training_info?.feature_importances
    ? Object.entries(training_info.feature_importances)
        .map(([name, value]) => ({
          name: name.replace(/_/g, ' '),
          importance: parseFloat((value * 100).toFixed(1))
        }))
        .sort((a, b) => b.importance - a.importance)
    : []

  // Confusion matrix
  const cm = training_info?.confusion_matrix

  // Metric cards
  const metricCards = [
    { label: 'AUC-ROC', value: metrics?.auc_roc, icon: Target, color: 'text-emerald-600', desc: 'Area under ROC curve' },
    { label: 'Precision', value: metrics?.precision, icon: Target, color: 'text-sky-600', desc: 'Positive predictive value' },
    { label: 'Recall', value: metrics?.recall, icon: TrendingUp, color: 'text-violet-600', desc: 'Sensitivity / true positive rate' },
    { label: 'F1 Score', value: metrics?.f1_score, icon: Brain, color: 'text-amber-600', desc: 'Harmonic mean of precision & recall' },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Model Performance</h2>
        <p className="text-slate-500">{model_type} — {training_info?.train_size?.toLocaleString()} training samples, {training_info?.test_size?.toLocaleString()} test samples</p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {metricCards.map(card => {
          const Icon = card.icon
          return (
            <div key={card.label} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-3">
                <Icon size={16} className={card.color} />
                <span className="text-xs text-slate-500 uppercase tracking-wider font-medium">{card.label}</span>
              </div>
              <p className={`text-3xl font-bold ${card.color}`}>
                {card.value != null ? card.value.toFixed(3) : '—'}
              </p>
              <p className="text-xs text-slate-400 mt-1">{card.desc}</p>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div className="space-y-8">
          {/* Cross-Validation */}
          {metrics?.cv_auc_mean && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-700 mb-3">5-Fold Cross-Validation</h3>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-emerald-600">{metrics.cv_auc_mean.toFixed(4)}</span>
                <span className="text-slate-400">±</span>
                <span className="text-lg text-slate-600">{metrics.cv_auc_std.toFixed(4)}</span>
                <span className="text-xs text-slate-400 ml-2">AUC-ROC (mean ± std)</span>
              </div>
              <p className="text-xs text-slate-500 mt-2">
                Low variance across folds indicates stable generalization. The model is not overfitting to a specific train/test split.
              </p>
            </div>
          )}

          {/* Confusion Matrix */}
          {cm && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-700 mb-4">Confusion Matrix</h3>
              <div className="grid grid-cols-2 gap-2 max-w-xs">
                <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-center">
                  <p className="text-xs text-slate-500">True Negatives</p>
                  <p className="text-2xl font-bold text-emerald-600">{cm.tn?.toLocaleString()}</p>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                  <p className="text-xs text-slate-500">False Positives</p>
                  <p className="text-2xl font-bold text-red-600">{cm.fp?.toLocaleString()}</p>
                </div>
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-center">
                  <p className="text-xs text-slate-500">False Negatives</p>
                  <p className="text-2xl font-bold text-amber-600">{cm.fn?.toLocaleString()}</p>
                </div>
                <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-center">
                  <p className="text-xs text-slate-500">True Positives</p>
                  <p className="text-2xl font-bold text-emerald-600">{cm.tp?.toLocaleString()}</p>
                </div>
              </div>
              <div className="flex gap-4 mt-3 text-xs text-slate-500">
                <span>Accuracy: {((cm.tn + cm.tp) / (cm.tn + cm.fp + cm.fn + cm.tp) * 100).toFixed(1)}%</span>
                <span>Specificity: {(cm.tn / (cm.tn + cm.fp) * 100).toFixed(1)}%</span>
              </div>
            </div>
          )}

          {/* Dataset Info */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Dataset</h3>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-slate-500">Default Rate</p>
                <p className="text-slate-900 font-bold">{training_info?.default_rate ? (training_info.default_rate * 100).toFixed(1) + '%' : '—'}</p>
              </div>
              <div>
                <p className="text-slate-500">Training Set</p>
                <p className="text-slate-900 font-bold">{training_info?.train_size?.toLocaleString() ?? '—'}</p>
              </div>
              <div>
                <p className="text-slate-500">Test Set</p>
                <p className="text-slate-900 font-bold">{training_info?.test_size?.toLocaleString() ?? '—'}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {/* Feature Importance */}
          {featureData.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-700 mb-4">Feature Importances (Gini)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={featureData} layout="vertical" margin={{ left: 90, right: 20 }}>
                  <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={v => `${v}%`} />
                  <YAxis type="category" dataKey="name" tick={{ fill: '#475569', fontSize: 12 }} width={85} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
                    labelStyle={{ color: '#0f172a' }}
                    formatter={v => [`${v}%`, 'Importance']}
                  />
                  <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                    {featureData.map((_, i) => (
                      <Cell key={i} fill={i < 3 ? '#059669' : '#cbd5e1'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Features List */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Input Features ({features?.length})</h3>
            <div className="flex flex-wrap gap-2">
              {features?.map(f => (
                <span key={f} className="px-3 py-1 bg-slate-100 border border-slate-200 rounded-full text-xs text-slate-600 font-mono">
                  {f}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
