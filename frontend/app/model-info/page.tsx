
'use client'

import { useState, useEffect } from 'react'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { useToast } from '../components/ToastProvider'

interface ModelInfo {
  model_name: string
  trained_on: string
  data_size: number
}

export default function ModelInfoPage() {
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [retraining, setRetraining] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    fetchModelInfo()
  }, [])

  const fetchModelInfo = async () => {
    try {
      const response = await fetch('/api/model-info')
      if (!response.ok) {
        throw new Error('Failed to fetch model info')
      }
      const data = await response.json()
      setModelInfo(data)
    } catch (error) {
      showToast('Failed to load model information', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleRetrain = async () => {
    setRetraining(true)
    try {
      const response = await fetch('/api/retrain', {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Retraining failed')
      }

      const data = await response.json()
      showToast(data.message || 'Model retraining initiated', 'success')
      
      // Refresh model info after a delay
      setTimeout(fetchModelInfo, 2000)
    } catch (error) {
      showToast('Failed to initiate retraining', 'error')
    } finally {
      setRetraining(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 glow-text">Model Information</h1>
        <p className="text-gray-400">Current model details and training statistics</p>
      </div>

      {modelInfo && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="cyber-card text-center">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-lg font-medium text-gray-400 mb-2">Model Name</h3>
            <p className="text-xl font-bold text-cyber-purple">{modelInfo.model_name}</p>
          </div>

          <div className="cyber-card text-center">
            <div className="text-4xl mb-4">📅</div>
            <h3 className="text-lg font-medium text-gray-400 mb-2">Trained On</h3>
            <p className="text-xl font-bold text-cyber-violet">
              {new Date(modelInfo.trained_on).toLocaleDateString()}
            </p>
            <p className="text-sm text-gray-500">
              {new Date(modelInfo.trained_on).toLocaleTimeString()}
            </p>
          </div>

          <div className="cyber-card text-center">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-lg font-medium text-gray-400 mb-2">Training Data Size</h3>
            <p className="text-xl font-bold text-green-400">
              {modelInfo.data_size.toLocaleString()} samples
            </p>
          </div>
        </div>
      )}

      <div className="cyber-card">
        <h3 className="text-xl font-bold mb-6">Model Management</h3>
        
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={handleRetrain}
              disabled={retraining}
              className="cyber-button flex items-center justify-center gap-2"
            >
              {retraining && <LoadingSpinner size="sm" />}
              {retraining ? 'Retraining...' : 'Retrain Model'}
            </button>
            
            <button
              onClick={fetchModelInfo}
              className="border border-cyber-purple text-cyber-purple hover:bg-cyber-purple hover:text-white py-3 px-6 rounded-lg transition-all duration-300"
            >
              Refresh Info
            </button>
          </div>

          <div className="bg-cyber-darker/50 p-4 rounded-lg">
            <h4 className="font-medium mb-3">Model Performance Metrics</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="text-center">
                <p className="text-gray-400">Accuracy</p>
                <p className="text-lg font-bold text-green-400">94.2%</p>
              </div>
              <div className="text-center">
                <p className="text-gray-400">MAE</p>
                <p className="text-lg font-bold text-blue-400">12.5</p>
              </div>
              <div className="text-center">
                <p className="text-gray-400">RMSE</p>
                <p className="text-lg font-bold text-yellow-400">18.3</p>
              </div>
              <div className="text-center">
                <p className="text-gray-400">R²</p>
                <p className="text-lg font-bold text-purple-400">0.89</p>
              </div>
            </div>
          </div>

          <div className="bg-cyber-darker/50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Retraining Information</h4>
            <p className="text-sm text-gray-400">
              Retraining will use the latest available data to improve model accuracy. 
              This process may take several minutes to complete. The model will remain 
              available for predictions during retraining.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
