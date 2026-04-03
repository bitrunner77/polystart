import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const CATEGORIES = ['OVERALL', 'POLITICS', 'SPORTS', 'CRYPTO', 'CULTURE', 'ECONOMICS', 'TECH', 'FINANCE']

function App() {
  const [traders, setTraders] = useState([])
  const [category, setCategory] = useState('OVERALL')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchTraders()
  }, [category])

  const fetchTraders = async () => {
    setLoading(true)
    try {
      const resp = await fetch(`${API_URL}/traders/${category}`)
      const data = await resp.json()
      setTraders(data)
      setError(null)
    } catch (err) {
      setError('Failed to load traders')
    }
    setLoading(false)
  }

  const formatNumber = (num) => {
    if (num >= 1000000) return `$${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `$${(num / 1000).toFixed(0)}K`
    return `$${num.toFixed(0)}`
  }

  return (
    <div className="container">
      <header className="header">
        <h1>🏆 PolyStart</h1>
        <p>Follow the best Polymarket traders</p>
      </header>

      <div className="stats">
        <div className="stat-card">
          <div className="value">{traders.length}</div>
          <div className="label">Top Traders</div>
        </div>
        <div className="stat-card">
          <div className="value">{CATEGORIES.length}</div>
          <div className="label">Categories</div>
        </div>
        <div className="stat-card">
          <div className="value">Free</div>
          <div className="label">Basic Access</div>
        </div>
      </div>

      <div className="tabs">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            className={`tab ${category === cat ? 'active' : ''}`}
            onClick={() => setCategory(cat)}
          >
            {cat.charAt(0) + cat.slice(1).toLowerCase()}
          </button>
        ))}
      </div>

      {loading && <div className="loading">Loading traders...</div>}
      
      {error && <div className="error">{error}</div>}

      {!loading && !error && (
        <div className="trader-list">
          {traders.map(trader => (
            <div key={trader.address} className="trader-card">
              <div className="rank">#{trader.rank}</div>
              <div className="trader-info">
                <h3>
                  {trader.username}
                  {trader.verified && ' ✅'}
                </h3>
                <div className="address">{trader.address.slice(0, 10)}...</div>
              </div>
              <div className="trader-stats">
                <div className={`pnl ${trader.pnl >= 0 ? 'positive' : ''}`}>
                  {trader.pnl >= 0 ? '+' : ''}{formatNumber(trader.pnl)}
                </div>
                <div className="volume">Vol: {formatNumber(trader.vol)}</div>
              </div>
              <button className="follow-btn">Follow</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App