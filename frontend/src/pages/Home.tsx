import React from 'react'
import { useNavigate } from 'react-router-dom'

const Home: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Navigation */}
      <nav className="border-b border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">SEO/GEO AI Dashboard</h1>
          <div className="space-x-4">
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium"
            >
              Login
            </button>
            <button
              onClick={() => navigate('/login')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              Sign Up
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-24">
        <div className="text-center space-y-6 mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900">
            Optimize Your Website for <span className="text-blue-600">AI & Search Engines</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Get AI-powered SEO & GEO (Generative Engine Optimization) scoring, actionable recommendations, and a one-click AI agent to generate optimized content.
          </p>
          <button
            onClick={() => navigate('/login')}
            className="inline-block px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold text-lg"
          >
            Get Started Free
          </button>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition">
            <div className="text-3xl mb-4">📊</div>
            <h3 className="text-lg font-semibold mb-2 text-gray-900">SEO Scoring</h3>
            <p className="text-gray-600">
              Analyze title, meta descriptions, headers, word count, images, load time, and more to get a comprehensive SEO score.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition">
            <div className="text-3xl mb-4">🤖</div>
            <h3 className="text-lg font-semibold mb-2 text-gray-900">GEO Scoring</h3>
            <p className="text-gray-600">
              See how well your page is structured for AI answer engines like ChatGPT and Perplexity. Optimize for the future of search.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition">
            <div className="text-3xl mb-4">✨</div>
            <h3 className="text-lg font-semibold mb-2 text-gray-900">AI Agent</h3>
            <p className="text-gray-600">
              One-click AI optimization: get a full plan + rewritten content to hit your target score automatically.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
            <div className="text-3xl mb-4">📈</div>
            <h3 className="text-lg font-semibold mb-2 text-gray-900">Keyword Tracking</h3>
            <p className="text-gray-600">
              Track your keywords over time. Monitor rankings, search volume, and trends to stay ahead of the competition.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
            <div className="text-3xl mb-4">💡</div>
            <h3 className="text-lg font-semibold mb-2 text-gray-900">Smart Recommendations</h3>
            <p className="text-gray-600">
              Get AI-powered suggestions tailored to your content. Fix issues, improve structure, and boost visibility instantly.
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl p-12 text-center text-white">
          <h3 className="text-2xl font-bold mb-4">Ready to optimize your website?</h3>
          <p className="mb-6 text-blue-100">
            Sign up now and run your first SEO/GEO audit in seconds. No credit card required.
          </p>
          <button
            onClick={() => navigate('/login')}
            className="px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-50 font-semibold"
          >
            Start Free Trial
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-gray-50 mt-24">
        <div className="max-w-7xl mx-auto px-6 py-8 text-center text-gray-600 text-sm">
          <p>© 2026 SEO/GEO AI Dashboard. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

export default Home
