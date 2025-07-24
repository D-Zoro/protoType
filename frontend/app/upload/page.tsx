'use client'

import { useState } from 'react'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { useToast } from '../components/ToastProvider'

export default function UploadPage() {
  const [dragActive, setDragActive] = useState(false)
  const [loading, setLoading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const { showToast } = useToast()

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const files = e.dataTransfer.files
    if (files && files[0]) {
      if (files[0].type === 'text/csv' || files[0].name.endsWith('.csv')) {
        setFile(files[0])
      } else {
        showToast('Please upload a CSV file', 'error')
      }
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files[0]) {
      if (files[0].type === 'text/csv' || files[0].name.endsWith('.csv')) {
        setFile(files[0])
      } else {
        showToast('Please upload a CSV file', 'error')
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!file) {
      showToast('Please select a CSV file', 'error')
      return
    }

    setLoading(true)
    
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/train', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Training failed')
      }

      const data = await response.json()
      showToast(data.message || 'Model trained successfully', 'success')
      setFile(null)
    } catch (error) {
      showToast('Failed to train model', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 glow-text">Train Model</h1>
        <p className="text-gray-400">Upload a CSV file to train the air pollution prediction model</p>
      </div>

      <div className="cyber-card">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
              dragActive
                ? 'border-cyber-purple bg-cyber-purple/10'
                : 'border-cyber-purple/30 hover:border-cyber-purple/50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".csv"
              onChange={handleChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            
            <div className="space-y-4">
              <div className="text-6xl">📊</div>
              
              {file ? (
                <div>
                  <p className="text-lg font-medium text-cyber-purple">{file.name}</p>
                  <p className="text-sm text-gray-400">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-lg font-medium">
                    Drag and drop your CSV file here, or click to browse
                  </p>
                  <p className="text-sm text-gray-400">
                    Supports CSV files up to 50MB
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-cyber-darker/50 p-4 rounded-lg">
            <h3 className="font-medium mb-2">CSV Format Requirements:</h3>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Include columns: latitude, longitude, pm2_5, pm10, no2, o3, aqi</li>
              <li>• First row should contain column headers</li>
              <li>• Use comma-separated values</li>
              <li>• Ensure numeric values for all pollutant measurements</li>
            </ul>
          </div>

          <button
            type="submit"
            disabled={loading || !file}
            className="cyber-button flex items-center justify-center gap-2 w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading && <LoadingSpinner size="sm" />}
            {loading ? 'Training Model...' : 'Train Model'}
          </button>
        </form>
      </div>

      <div className="cyber-card">
        <h3 className="text-xl font-bold mb-4">Training Tips</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-cyber-purple mb-2">Data Quality</h4>
            <p className="text-sm text-gray-400">
              Ensure your data is clean, complete, and represents diverse geographical locations and weather conditions.
            </p>
          </div>
          <div>
            <h4 className="font-medium text-cyber-purple mb-2">Sample Size</h4>
            <p className="text-sm text-gray-400">
              Larger datasets (1000+ rows) typically produce more accurate models. Include seasonal variations if possible.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
