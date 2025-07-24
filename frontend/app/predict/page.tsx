
'use client'

import { useState } from 'react'
import { PredictionCard } from '../components/PredictionCard'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { useToast } from '../components/ToastProvider'

interface PredictionResponse {
  predictions: {
    pm2_5: number
    pm10: number
    no2: number
    o3: number
    aqi: number
  }
  location: {
    latitude: number
    longitude: number
  }
  timestamp: string
  data_sources: string[]
}

export default function PredictPage() {
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null)
  const { showToast } = useToast()

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude.toString())
          setLongitude(position.coords.longitude.toString())
          showToast('Location detected successfully', 'success')
        },
        () => {
          showToast('Unable to detect location', 'error')
        }
      )
    } else {
      showToast('Geolocation is not supported', 'error')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!latitude || !longitude) {
      showToast('Please enter both latitude and longitude', 'error')
      return
    }

    setLoading(true)
    
    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latitude: parseFloat(latitude),
          longitude: parseFloat(longitude),
        }),
      })

      if (!response.ok) {
        throw new Error('Prediction failed')
      }

      const data = await response.json()
      setPrediction(data)
      showToast('Prediction generated successfully', 'success')
    } catch (error) {
      showToast('Failed to get prediction', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 glow-text">Air Quality Prediction</h1>
        <p className="text-gray-400">Enter coordinates to get real-time air pollution predictions</p>
      </div>

      <div className="cyber-card">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Latitude</label>
              <input
                type="number"
                step="any"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                placeholder="e.g., 28.6139"
                className="cyber-input w-full"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Longitude</label>
              <input
                type="number"
                step="any"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                placeholder="e.g., 77.2090"
                className="cyber-input w-full"
                required
              />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <button
              type="submit"
              disabled={loading}
              className="cyber-button flex items-center justify-center gap-2"
            >
              {loading && <LoadingSpinner size="sm" />}
              {loading ? 'Predicting...' : 'Get Prediction'}
            </button>
            
            <button
              type="button"
              onClick={getCurrentLocation}
              className="border border-cyber-purple text-cyber-purple hover:bg-cyber-purple hover:text-white py-3 px-6 rounded-lg transition-all duration-300"
            >
              Use Current Location
            </button>
          </div>
        </form>
      </div>

      {prediction && (
        <div className="space-y-6">
          <PredictionCard data={prediction.predictions} />
          
          <div className="cyber-card">
            <h3 className="text-xl font-bold mb-4">Prediction Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-400">Location:</p>
                <p>{prediction.location.latitude}, {prediction.location.longitude}</p>
              </div>
              <div>
                <p className="text-gray-400">Timestamp:</p>
                <p>{new Date(prediction.timestamp).toLocaleString()}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-gray-400">Data Sources:</p>
                <p>{prediction.data_sources.join(', ')}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
