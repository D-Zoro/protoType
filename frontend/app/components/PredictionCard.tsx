interface PredictionData {
  pm2_5: number
  pm10: number
  no2: number
  o3: number
  aqi: number
}

interface PredictionCardProps {
  data: PredictionData
}

export function PredictionCard({ data }: PredictionCardProps) {
  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return 'text-green-400'
    if (aqi <= 100) return 'text-yellow-400'
    if (aqi <= 150) return 'text-orange-400'
    if (aqi <= 200) return 'text-red-400'
    if (aqi <= 300) return 'text-purple-400'
    return 'text-red-600'
  }

  const getAQILevel = (aqi: number) => {
    if (aqi <= 50) return 'Good'
    if (aqi <= 100) return 'Moderate'
    if (aqi <= 150) return 'Unhealthy for Sensitive Groups'
    if (aqi <= 200) return 'Unhealthy'
    if (aqi <= 300) return 'Very Unhealthy'
    return 'Hazardous'
  }

  return (
    <div className="cyber-card">
      <div className="text-center mb-6">
        <h3 className="text-3xl font-bold mb-2">Air Quality Index</h3>
        <div className={`text-6xl font-bold ${getAQIColor(data.aqi)} animate-pulse-slow`}>
          {Math.round(data.aqi)}
        </div>
        <p className={`text-lg font-medium ${getAQIColor(data.aqi)}`}>
          {getAQILevel(data.aqi)}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-cyber-darker/50 rounded-lg">
          <p className="text-gray-400 text-sm">PM2.5</p>
          <p className="text-2xl font-bold text-cyber-purple">{Math.round(data.pm2_5)}</p>
          <p className="text-xs text-gray-500">μg/m³</p>
        </div>
        
        <div className="text-center p-4 bg-cyber-darker/50 rounded-lg">
          <p className="text-gray-400 text-sm">PM10</p>
          <p className="text-2xl font-bold text-cyber-violet">{Math.round(data.pm10)}</p>
          <p className="text-xs text-gray-500">μg/m³</p>
        </div>
        
        <div className="text-center p-4 bg-cyber-darker/50 rounded-lg">
          <p className="text-gray-400 text-sm">NO2</p>
          <p className="text-2xl font-bold text-blue-400">{Math.round(data.no2)}</p>
          <p className="text-xs text-gray-500">μg/m³</p>
        </div>
        
        <div className="text-center p-4 bg-cyber-darker/50 rounded-lg">
          <p className="text-gray-400 text-sm">O3</p>
          <p className="text-2xl font-bold text-green-400">{Math.round(data.o3)}</p>
          <p className="text-xs text-gray-500">μg/m³</p>
        </div>
      </div>
    </div>
  )
}
