'use client'

import { useState } from 'react'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { useToast } from '../components/ToastProvider'

interface BatchLocation {
  latitude: number
  longitude: number
}

interface BatchResult {
  location: {
    latitude: number
    longitude: number
  }
  predictions: {
    pm2_5: number
    pm10: number
    no2: number
    o3: number
    aqi: number
  }
}

export default function BatchPage() {
  const [locations, setLocations] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<BatchResult[]>([])
  const { showToast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!locations.trim()) {
      showToast('Please enter at least one location', 'error')
      return
    }

    try {
      const lines = locations.trim().split('\n')
      const batchData: BatchLocation[] = []

      for (const line of lines) {
        const [lat, lng] = line.split(',').map(s => parseFloat(s.trim()))
        if (isNaN(lat) || isNaN(lng)) {
          showToast('Invalid coordinate format. Use: latitude, longitude', 'error')
          return
        }
        batchData.push({ latitude: lat, longitude: lng })
      }

      setLoading(true)

      const response = await fetch('/api/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(batchData),
      })

      if (!response.ok) {
        throw new Error('Batch prediction failed')
      }

      const data = await response.json()
      setResults(data)
      showToast(`Successfully processed ${data.length} locations`, 'success')
    } catch (error) {
      showToast('Failed to process batch predictions', 'error')
    } finally {
      setLoading(false)
    }
  }

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return 'text-green-400'
    if (aqi <= 100) return 'text-yellow-400'
    if (aqi <= 150) return 'text-orange-400'
    if (aqi <= 200) return 'text-red-400'
    return 'text-purple-400'
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 glow-text">Batch Predictions</h1>
        <p className="text-gray-400">Process multiple locations at once for air quality predictions</p>
      </div>

      <div className="cyber-card">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">
              Locations (one per line: latitude, longitude)
            </label>
            <textarea
              value={locations}
              onChange={(e) => setLocations(e.target.value)}
              placeholder="28.6139, 77.2090&#10;19.0760, 72.8777&#10;12.9716, 77.5946"
              className="cyber-input w-full h-32 resize-none"
              required
            />
            <p className="text-xs text-gray-500 mt-2">
              Example: 28.6139, 77.2090 (Delhi) or 19.0760, 72.8777 (Mumbai)
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="cyber-button flex items-center justify-center gap-2"
          >
            {loading && <LoadingSpinner size="sm" />}
            {loading ? 'Processing...' : 'Process Batch'}
          </button>
        </form>
      </div>

      {results.length > 0 && (
        <div className="cyber-card">
          <h3 className="text-xl font-bold mb-6">Batch Results</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-cyber-purple/20">
                  <th className="text-left py-3 px-2">Location</th>
                  <th className="text-center py-3 px-2">AQI</th>
                  <th className="text-center py-3 px-2">PM2.5</th>
                  <th className="text-center py-3 px-2">PM10</th>
                  <th className="text-center py-3 px-2">NO2</th>
                  <th className="text-center py-3 px-2">O3</th>
                </tr>
              </thead>
              <tbody>
                {results.map((result, index) => (
                  <tr key={index} className="border-b border-cyber-gray hover:bg-cyber-gray/30 transition-colors">
                    <td className="py-3 px-2">
                      {result.location.latitude.toFixed(4)}, {result.location.longitude.toFixed(4)}
                    </td>
                    <td className={`text-center py-3 px-2 font-bold ${getAQIColor(result.predictions.aqi)}`}>
                      {Math.round(result.predictions.aqi)}
                    </td>
                    <td className="text-center py-3 px-2">{Math.round(result.predictions.pm2_5)}</td>
                    <td className="text-center py-3 px-2">{Math.round(result.predictions.pm10)}</td>
                    <td className="text-center py-3 px-2">{Math.round(result.predictions.no2)}</td>
                    <td className="text-center py-3 px-2">{Math.round(result.predictions.o3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
