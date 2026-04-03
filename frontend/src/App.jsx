import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const CATEGORIES = ['OVERALL', 'POLITICS', 'SPORTS', 'CRYPTO', 'CULTURE', 'ECONOMICS', 'TECH', 'FINANCE']

function App() {
  const [traders, setTraders] = useState([])
  const [category, setCategory] = useState('OVERALL')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [user, setUser] = useState(null)
  const [follows, setFollows] = useState([])
  const [showAuth, setShowAuth] = useState(false)
  const [username, setUsername] = useState('')

  // Load user from localStorage
  useEffect(() => {
    const savedToken = localStorage.getItem('polystart_token')
    if (savedToken) {
      fetchUser(savedToken)
    }
  }, [])

  // Fetch traders when category changes
  useEffect(() => {
    fetchTraders()
  }, [category])

  // Fetch follows when user changes
  useEffect(() => {
    if (user?.token) {
      fetchFollows()
    }
  }, [user])

  const fetchUser = async (token) => {
    try {
      const resp = await fetch(`${API_URL}/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (resp.ok) {
        const data = await resp.json()
        setUser({ ...data, token })
      } else {
        localStorage.removeItem('polystart_token')
      }
    } catch (e) {
      console.error(e)
    }
  }

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

  const fetchFollows = async () => {
    if (!user?.token) return
    try {
      const resp = await fetch(`${API_URL}/follows`, {
        headers: { 'Authorization': `Bearer ${user.token}` }
      })
      if (resp.ok) {
        const data = await resp.json()
        setFollows(data.map(f => f.address))
      }
    } catch (e) {
      console.error(e)
    }
  }

  const login = async () => {
    if (!username.trim()) return
    try {
      const resp = await fetch(`${API_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          telegram_id: `web_${Date.now()}`,
          username: username 
        })
      })
      const data = await resp.json()
      if (data.api_token) {
        localStorage.setItem('polystart_token', data.api_token)
        setUser({ ...data, token: data.api_token })
        setShowAuth(false)
      }
    } catch (e) {
      alert('Login failed')
    }
  }

  const logout = () => {
    localStorage.removeItem('polystart_token')
    setUser(null)
    setFollows([])
  }

  const toggleFollow = async (trader) => {
    if (!user) {
      setShowAuth(true)
      return
    }

    const isFollowing = follows.includes(trader.address)
    
    try {
      if (isFollowing) {
        await fetch(`${API_URL}/follow/${trader_address}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${user.token}` }
        })
        setFollows(follows.filter(f => f !== trader.address))
      } else {
        // Check limit
        if (user.tier === 'free' && follows.length >= 3) {
          alert('Free tier: max 3 follows. Upgrade to Pro!')
          return
        }
        
        await fetch(`${API_URL}/follow`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${user.token}` 
          },
          body: JSON.stringify({
            trader_address: trader.address,
            trader_name: trader.username
          })
        })
        setFollows([...follows, trader.address])
      }
    } catch (e) {
      alert('Error: ' + e.message)
    }
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
        
        {user && (
          <div className="user-info">
            <span>👤 {user.username} ({user.tier})</span>
            <button onClick={logout} className="logout-btn">Logout</button>
          </div>
        )}
        
        {!user && (
          <button onClick={() => setShowAuth(true)} className="login-btn">
            Sign In
          </button>
        )}
      </header>

      {showAuth && (
        <div className="auth-modal">
          <div className="auth-box">
            <h3>Sign In</h3>
            <input
              type="text"
              placeholder="Your name"
              value={username}
              onChange={e => setUsername(e.target.value)}
            />
            <button onClick={login}>Continue</button>
            <button onClick={() => setShowAuth(false)} className="cancel">
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="stats">
        <div className="stat-card">
          <div className="value">{traders.length}</div>
          <div className="label">Top Traders</div>
        </div>
        <div className="stat-card">
          <div className="value">{user ? follows.length : '-'}</div>
          <div className="label">Following</div>
        </div>
        <div className="stat-card">
          <div className="value">{user?.tier || 'Guest'}</div>
          <div className="label">Plan</div>
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
                <div className="address">{trader.address.slice(0, 14)}...</div>
              </div>
              <div className="trader-stats">
                <div className={`pnl ${trader.pnl >= 0 ? 'positive' : ''}`}>
                  {trader.pnl >= 0 ? '+' : ''}{formatNumber(trader.pnl)}
                </div>
                <div className="volume">Vol: {formatNumber(trader.vol)}</div>
              </div>
              <button 
                className={`follow-btn ${follows.includes(trader.address) ? 'following' : ''}`}
                onClick={() => toggleFollow(trader)}
              >
                {follows.includes(trader.address) ? 'Following' : 'Follow'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App