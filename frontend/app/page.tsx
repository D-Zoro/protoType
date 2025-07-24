export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-8 animate-float">
        <div className="relative">
          <h1 className="text-8xl md:text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyber-purple via-cyber-violet to-cyber-purple animate-glow">
            Airo
          </h1>
          <div className="absolute inset-0 text-8xl md:text-9xl font-bold text-cyber-purple/20 blur-sm">
            Airo
          </div>
        </div>
        
        <p className="text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto">
          Real-time air pollution prediction powered by advanced AI algorithms
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <a href="/predict" className="cyber-button">
            Start Prediction
          </a>
          <a href="/model-info" className="border border-cyber-purple text-cyber-purple hover:bg-cyber-purple hover:text-white py-3 px-6 rounded-lg transition-all duration-300">
            Model Info
          </a>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 max-w-6xl mx-auto">
          <div className="cyber-card text-center">
            <div className="text-4xl mb-4">🌍</div>
            <h3 className="text-xl font-bold mb-2">Global Coverage</h3>
            <p className="text-gray-400">Predict air quality anywhere in the world with precise coordinates</p>
          </div>
          
          <div className="cyber-card text-center">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold mb-2">Real-time Results</h3>
            <p className="text-gray-400">Get instant predictions powered by live satellite and weather data</p>
          </div>
          
          <div className="cyber-card text-center">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold mb-2">AI Powered</h3>
            <p className="text-gray-400">Advanced machine learning models for accurate pollution forecasting</p>
          </div>
        </div>
      </div>
    </div>
  )
}
