/**
 * Dashboard.jsx
 * Main multi-card layout — assembles all components into the cockpit UI.
 */
import React, { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { calculateStrategy, fetchTracks, updateWeather } from '../api/strategyApi'
import { TRACK_PATHS } from '../data/trackPaths'

import CircuitMap    from './CircuitMap'
import LapTimeChart  from './LapTimeChart'
import PitStrategy   from './PitStrategy'
import TireStrategy  from './TireStrategy'
import TelemetryCard from './TelemetryCard'
import WeatherToggle from './WeatherToggle'

const CARD_VARIANTS = {
  hidden: { opacity: 0, y: 20 },
  visible: (i) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.08, duration: 0.4, ease: 'easeOut' },
  }),
}

function CardShell({ title, icon, badge, children, style, idx = 0 }) {
  return (
    <motion.div
      className="card"
      variants={CARD_VARIANTS}
      custom={idx}
      initial="hidden"
      animate="visible"
      style={style}
    >
      <div className="card-header">
        <div className="card-header__icon">{icon}</div>
        <div>
          <div className="card-header__title">{title}</div>
        </div>
        {badge && <div className="card-header__badge">{badge}</div>}
      </div>
      {children}
    </motion.div>
  )
}

function LoadingOverlay() {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', gap: 16, padding: '60px 20px',
    }}>
      <div style={{ position: 'relative' }}>
        <div className="spinner" style={{ width: 48, height: 48 }} />
        <div style={{
          position: 'absolute', inset: 0, display: 'flex',
          alignItems: 'center', justifyContent: 'center',
          fontSize: '1.2rem',
        }}>🏎️</div>
      </div>
      <div style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--f1-navy)' }}>
        Running Monte Carlo Simulation...
      </div>
      <div style={{
        fontFamily: 'JetBrains Mono, monospace',
        fontSize: '0.72rem',
        color: 'var(--f1-navy-light)',
        textAlign: 'center',
        lineHeight: 1.8,
      }}>
        SLSQP optimization with g(x) constraints<br />
        Processing 5,000 race simulations<br />
        Evaluating ||∇g(x)||₂ convergence...
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [tracks, setTracks]         = useState([])
  const [trackId, setTrackId]       = useState('suzuka')
  const [strategy, setStrategy]     = useState(null)
  const [isLoading, setIsLoading]   = useState(false)
  const [isWeatherLoading, setIsWeatherLoading] = useState(false)
  const [error, setError]           = useState(null)
  const [weather, setWeather]       = useState({
    type: 'DRY', airTemp: 26, trackTemp: 42, rainIntensity: 0, windSpeed: 8,
  })
  const [isAnimating, setIsAnimating] = useState(true)
  const [activeTab, setActiveTab]     = useState('lap_times')
  const prevWeatherRef = useRef('DRY')

  // Fetch tracks list on mount
  useEffect(() => {
    fetchTracks()
      .then(t => setTracks(t))
      .catch(() => {
        // Fallback track list from local data
        setTracks(Object.entries(TRACK_PATHS).map(([id, t]) => ({
          track_id: id,
          name: t.label,
          country: t.country,
        })))
      })
  }, [])

  // Initial strategy calculation
  useEffect(() => {
    runCalculation()
  }, [trackId])

  const runCalculation = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await calculateStrategy({
        trackId,
        weather,
        nSimulations: 3000,
      })
      setStrategy(result)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Backend connection failed. Make sure the FastAPI server is running on port 8000.')
    } finally {
      setIsLoading(false)
    }
  }, [trackId, weather])

  const handleWeatherChange = useCallback(async (option) => {
    const newWeather = {
      type: option.id,
      airTemp: option.airTemp,
      trackTemp: option.trackTemp,
      rainIntensity: option.rainIntensity,
      windSpeed: option.windSpeed,
    }
    setWeather(newWeather)
    setIsWeatherLoading(true)
    setError(null)

    try {
      const result = await updateWeather({
        trackId,
        driverName: strategy?.driver_name || 'VER',
        teamName: strategy?.team_name || 'Red Bull Racing',
        prevWeatherType: prevWeatherRef.current,
        weather: newWeather,
      })
      prevWeatherRef.current = option.id
      setStrategy(result)
    } catch (err) {
      // Fallback: full recalculation
      try {
        const result = await calculateStrategy({ trackId, weather: newWeather, nSimulations: 2000 })
        setStrategy(result)
        prevWeatherRef.current = option.id
      } catch (err2) {
        setError(err2.message)
      }
    } finally {
      setIsWeatherLoading(false)
    }
  }, [trackId, strategy])

  const currentStint = strategy?.stints?.[0] || null

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-gradient)',
      backgroundAttachment: 'fixed',
    }}>
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <header style={{
        background: 'rgba(255,255,255,0.7)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(26,31,58,0.08)',
        position: 'sticky', top: 0, zIndex: 200,
        padding: '0 32px',
      }}>
        <div style={{
          maxWidth: 1400,
          margin: '0 auto',
          height: 64,
          display: 'flex',
          alignItems: 'center',
          gap: 20,
        }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
            <div style={{
              width: 38, height: 38,
              borderRadius: 10,
              background: 'linear-gradient(135deg, var(--f1-red), #ff4d4d)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '1.1rem',
              boxShadow: '0 4px 12px rgba(225,6,0,0.3)',
              animation: 'pulse-glow 3s ease-in-out infinite',
            }}>🏎️</div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.9rem', color: 'var(--f1-navy)', lineHeight: 1.1 }}>
                F1 Strategy Engine
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--f1-red)', fontWeight: 600,
                textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Monte Carlo · Telemetry · 2026 Season
              </div>
            </div>
          </div>

          {/* Track selector */}
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--f1-navy-light)', whiteSpace: 'nowrap' }}>
                Circuit
              </span>
              <select
                id="track-selector"
                value={trackId}
                onChange={e => setTrackId(e.target.value)}
                style={{ minWidth: 220 }}
              >
                {tracks.length > 0
                  ? tracks.map(t => (
                      <option key={t.track_id} value={t.track_id}>
                        {t.country || ''} {t.name}
                      </option>
                    ))
                  : Object.entries(TRACK_PATHS).map(([id, t]) => (
                      <option key={id} value={id}>{t.country} {t.label}</option>
                    ))
                }
              </select>
            </div>
          </div>

          {/* Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
            <button
              id="toggle-animation"
              className="btn btn--ghost"
              onClick={() => setIsAnimating(a => !a)}
              style={{ padding: '8px 14px', fontSize: '0.78rem' }}
            >
              {isAnimating ? '⏸ Pause' : '▶ Animate'}
            </button>
            <button
              id="recalculate-btn"
              className="btn btn--primary"
              onClick={runCalculation}
              disabled={isLoading}
              style={{ padding: '8px 18px', fontSize: '0.78rem' }}
            >
              {isLoading ? '⟳ Computing...' : '⚡ Recalculate'}
            </button>
          </div>
        </div>
      </header>

      {/* ── Main Content ─────────────────────────────────────────────────── */}
      <main style={{ maxWidth: 1400, margin: '0 auto', padding: '28px 32px 60px' }}>

        {/* Error banner */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              style={{
                padding: '14px 18px',
                borderRadius: 12,
                background: 'rgba(239,68,68,0.08)',
                border: '1px solid rgba(239,68,68,0.25)',
                color: '#991b1b',
                fontSize: '0.875rem',
                fontWeight: 500,
                marginBottom: 20,
                display: 'flex',
                alignItems: 'flex-start',
                gap: 10,
              }}
            >
              <span style={{ fontSize: '1rem', flexShrink: 0 }}>⚠️</span>
              <div>
                <strong>Backend Error:</strong> {error}
                <br />
                <span style={{ fontSize: '0.78rem', opacity: 0.8 }}>
                  Start the backend: <code style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '0.75rem' }}>cd backend && uvicorn main:app --reload</code>
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Top row: Circuit map (large) + Weather + Telemetry ── */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 280px',
          gap: 20,
          marginBottom: 20,
        }}>
          {/* Circuit map card */}
          <CardShell title="Live Circuit Map" icon="🗺️" idx={0}
            badge={strategy?.track_name?.split(' ').slice(-2).join(' ') || trackId}
            style={{ overflow: 'hidden' }}
          >
            {isLoading ? (
              <LoadingOverlay />
            ) : (
              <>
                <div style={{ padding: '0 0 0 0', height: 320 }}>
                  <CircuitMap
                    trackId={trackId}
                    keyPoints={strategy?.track_key_points || []}
                    currentStint={currentStint}
                    isAnimating={isAnimating}
                  />
                </div>
                {/* Legend */}
                <div style={{
                  padding: '10px 20px',
                  borderTop: '1px solid rgba(26,31,58,0.06)',
                  display: 'flex',
                  gap: 16,
                  flexWrap: 'wrap',
                  fontSize: '0.68rem',
                }}>
                  {[
                    { color: '#8B5CF6', label: 'High-G Zone' },
                    { color: '#F59E0B', label: 'Tire Stress' },
                    { color: '#10B981', label: 'Pit Window' },
                    { color: '#3B82F6', label: 'Overtake' },
                    { color: '#06B6D4', label: 'DRS Zone' },
                    { color: '#EF4444', label: 'Braking' },
                  ].map(({ color, label }) => (
                    <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <div style={{ width: 8, height: 8, borderRadius: '50%', background: color, flexShrink: 0 }} />
                      <span style={{ color: 'var(--f1-navy-light)', fontWeight: 500 }}>{label}</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </CardShell>

          {/* Right column: Weather + Telemetry */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <WeatherToggle
              currentWeather={weather.type}
              onWeatherChange={handleWeatherChange}
              isLoading={isWeatherLoading}
            />
          </div>
        </div>

        {/* ── Race Overview stats row ── */}
        {strategy && !isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
              gap: 14,
              marginBottom: 20,
            }}
          >
            {[
              { label: 'Track',          value: strategy.track_name?.split('(')[0].trim().split(' ').slice(0, 2).join(' '), icon: '🏁' },
              { label: 'Optimal Time',   value: strategy.optimal_total_time_formatted, icon: '⏱', mono: true, highlight: true },
              { label: 'Pit Stops',      value: strategy.pit_stops?.length, icon: '🔧' },
              { label: 'Total Laps',     value: strategy.total_laps, icon: '🔄', mono: true },
              { label: 'Weather',        value: strategy.weather_type, icon: '🌡️' },
              { label: 'MC Probability', value: `${((strategy.monte_carlo_stats?.optimal_strategy_probability || 0) * 100).toFixed(0)}%`, icon: '📊', mono: true },
            ].map((item, i) => (
              <motion.div
                key={item.label}
                className="card card--flat"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                style={{
                  padding: '14px 16px',
                  background: item.highlight
                    ? 'linear-gradient(135deg, rgba(225,6,0,0.08), rgba(225,6,0,0.04))'
                    : undefined,
                  border: item.highlight ? '1px solid rgba(225,6,0,0.15)' : undefined,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                  <span style={{ fontSize: '0.9rem' }}>{item.icon}</span>
                  <span style={{
                    fontSize: '0.62rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    color: 'var(--f1-navy-light)',
                  }}>
                    {item.label}
                  </span>
                </div>
                <div className={item.mono ? 'mono' : ''} style={{
                  fontSize: item.highlight ? '1.2rem' : '1rem',
                  fontWeight: 800,
                  color: item.highlight ? 'var(--f1-red)' : 'var(--f1-navy)',
                  lineHeight: 1.1,
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}>
                  {item.value ?? '—'}
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* ── Main chart area + side panel ── */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 340px',
          gap: 20,
        }}>
          {/* Left: Tabbed charts */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

            {/* Tab card */}
            <CardShell title="Race Analysis" icon="📈" idx={1}
              badge={activeTab === 'lap_times' ? 'Lap Times' : activeTab === 'pit' ? 'Pit Strategy' : 'Tires'}
            >
              {/* Tab buttons */}
              <div style={{
                display: 'flex',
                gap: 4,
                padding: '0 20px 16px',
                borderBottom: '1px solid rgba(26,31,58,0.06)',
              }}>
                {[
                  { id: 'lap_times', label: '📊 Expected Lap Times' },
                  { id: 'pit', label: '🔧 Pitstop Strategy' },
                  { id: 'tires', label: '🏎️ Tire Compounds' },
                ].map(tab => (
                  <button
                    key={tab.id}
                    id={`tab-${tab.id}`}
                    onClick={() => setActiveTab(tab.id)}
                    style={{
                      padding: '7px 14px',
                      borderRadius: 8,
                      border: 'none',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      background: activeTab === tab.id
                        ? 'var(--f1-navy)' : 'rgba(26,31,58,0.06)',
                      color: activeTab === tab.id ? '#fff' : 'var(--f1-navy-light)',
                      fontFamily: 'Inter, sans-serif',
                    }}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              <div style={{ padding: '16px 20px 4px' }}>
                <AnimatePresence mode="wait">
                  {isLoading ? (
                    <LoadingOverlay />
                  ) : activeTab === 'lap_times' ? (
                    <motion.div key="laps" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <LapTimeChart
                        lapData={strategy?.lap_data}
                        pitStops={strategy?.pit_stops}
                      />
                    </motion.div>
                  ) : activeTab === 'pit' ? (
                    <motion.div key="pit" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <PitStrategy
                        stints={strategy?.stints}
                        pitStops={strategy?.pit_stops}
                        totalLaps={strategy?.total_laps}
                      />
                    </motion.div>
                  ) : (
                    <motion.div key="tires" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <TireStrategy
                        stints={strategy?.stints}
                        totalLaps={strategy?.total_laps}
                      />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </CardShell>

            {/* Seaborn visualizations */}
            {strategy?.visualizations && !isLoading && (
              <CardShell title="Comparative Analysis" icon="📉" idx={2} badge="Seaborn">
                <div style={{ padding: '0 16px 20px' }}>
                  <div style={{ marginBottom: 12 }}>
                    <div className="section-label" style={{ padding: '0 4px 6px' }}>
                      Tire Degradation Curves
                    </div>
                    <img
                      src={`data:image/png;base64,${strategy.visualizations.degradation_curves_b64}`}
                      alt="Tire degradation curves — all compounds"
                      style={{ width: '100%', borderRadius: 10, border: '1px solid rgba(26,31,58,0.08)' }}
                    />
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <div className="section-label" style={{ padding: '0 4px 6px' }}>
                      Monte Carlo Distribution
                    </div>
                    <img
                      src={`data:image/png;base64,${strategy.visualizations.lap_time_distribution_b64}`}
                      alt="Monte Carlo race time distribution"
                      style={{ width: '100%', borderRadius: 10, border: '1px solid rgba(26,31,58,0.08)' }}
                    />
                  </div>
                  <div>
                    <div className="section-label" style={{ padding: '0 4px 6px' }}>
                      Lap Time Strategy
                    </div>
                    <img
                      src={`data:image/png;base64,${strategy.visualizations.strategy_comparison_b64}`}
                      alt="Expected lap times by compound"
                      style={{ width: '100%', borderRadius: 10, border: '1px solid rgba(26,31,58,0.08)' }}
                    />
                  </div>
                </div>
              </CardShell>
            )}
          </div>

          {/* Right sidebar: Telemetry */}
          <CardShell title="Race Telemetry" icon="📡" idx={3} badge="LIVE">
            {isLoading ? (
              <div style={{ padding: '24px', display: 'flex', justifyContent: 'center' }}>
                <div className="spinner" />
              </div>
            ) : (
              <TelemetryCard
                strategy={strategy}
                mcStats={strategy?.monte_carlo_stats}
              />
            )}
          </CardShell>
        </div>
      </main>

      {/* ── Footer ── */}
      <footer style={{
        borderTop: '1px solid rgba(26,31,58,0.08)',
        padding: '20px 32px',
        background: 'rgba(255,255,255,0.5)',
        backdropFilter: 'blur(10px)',
      }}>
        <div style={{
          maxWidth: 1400,
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 10,
        }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--f1-navy-light)' }}>
            <strong style={{ color: 'var(--f1-navy)' }}>F1 Race Strategy & Telemetry Simulation Engine</strong>
            {' '}— November 2025 · Python · Pandas · Monte Carlo · Scikit-learn · Seaborn
          </div>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '0.68rem',
            color: 'var(--f1-navy-light)',
          }}>
            SLSQP Optimization · g(x) Constraints · ||∇g(x)||₂ Convergence · All 24 F1 2026 Tracks
          </div>
        </div>
      </footer>
    </div>
  )
}
