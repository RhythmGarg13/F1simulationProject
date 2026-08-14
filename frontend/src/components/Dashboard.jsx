/**
 * Dashboard.jsx
 * Main multi-card layout — assembles all components into the cockpit UI.
 *
 * Split into sub-components:
 *   Header     — logo, track selector, control buttons
 *   ErrorBanner — animated error alert
 *   StatsRow   — race overview stats strip
 *   Footer     — tech stack info
 */
import React, { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { calculateStrategy, fetchTracks, updateWeather } from '../api/strategyApi'
import { TRACK_PATHS } from '../data/trackPaths'

import CircuitMap from './CircuitMap'
import LapTimeChart from './LapTimeChart'
import PitStrategy from './PitStrategy'
import TireStrategy from './TireStrategy'
import TelemetryCard from './TelemetryCard'
import WeatherToggle from './WeatherToggle'
import Header from './Header'
import ErrorBanner from './ErrorBanner'
import StatsRow from './StatsRow'
import Footer from './Footer'

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

function LoadingOverlay({ testId }) {
  return (
    <div className="loading-overlay" data-testid={testId}>
      <div className="loading-overlay__spinner-wrap">
        <div className="spinner loading-overlay__spinner" />
        <div className="loading-overlay__car">🏎️</div>
      </div>
      <div className="loading-overlay__title">Running Monte Carlo Simulation...</div>
      <div className="loading-overlay__detail mono">
        SLSQP optimization with g(x) constraints<br />
        Processing 5,000 race simulations<br />
        Evaluating ||∇g(x)||₂ constraint sensitivity...
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [tracks, setTracks] = useState([])
  const [trackId, setTrackId] = useState('suzuka')
  const [strategy, setStrategy] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isWeatherLoading, setIsWeatherLoading] = useState(false)
  const [error, setError] = useState(null)
  const [weather, setWeather] = useState({
    type: 'DRY', airTemp: 26, trackTemp: 42, rainIntensity: 0, windSpeed: 8,
  })
  const [isAnimating, setIsAnimating] = useState(true)
  const [activeTab, setActiveTab] = useState('lap_times')
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
      // err.message is already normalised by the axios interceptor in strategyApi.js
      setError(err.message || 'Backend connection failed. Make sure the FastAPI server is running on port 8000.')
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
    <div className="app-shell">
      <Header
        tracks={tracks}
        trackId={trackId}
        onTrackChange={setTrackId}
        isLoading={isLoading}
        isAnimating={isAnimating}
        onToggleAnimation={() => setIsAnimating(a => !a)}
        onRecalculate={runCalculation}
      />

      <main className="app-main">
        <ErrorBanner error={error} />

        {/* ── Top row: Circuit map (large) + Weather ── */}
        <div className="layout-top-row">
          {/* Circuit map card */}
          <CardShell title="Live Circuit Map" icon="🗺️" idx={0}
            badge={strategy?.track_name?.split(' ').slice(-2).join(' ') || trackId}
            style={{ overflow: 'hidden' }}
          >
            {isLoading ? (
              <LoadingOverlay testId="circuit-map-loading" />
            ) : (
              <>
                <div className="circuit-map-wrap">
                  <CircuitMap
                    trackId={trackId}
                    keyPoints={strategy?.track_key_points || []}
                    currentStint={currentStint}
                    isAnimating={isAnimating}
                  />
                </div>
                {/* Legend */}
                <div className="circuit-legend">
                  {[
                    { color: '#8B5CF6', label: 'High-G Zone' },
                    { color: '#F59E0B', label: 'Tire Stress' },
                    { color: '#10B981', label: 'Pit Window' },
                    { color: '#3B82F6', label: 'Overtake' },
                    { color: '#06B6D4', label: 'DRS Zone' },
                    { color: '#EF4444', label: 'Braking' },
                  ].map(({ color, label }) => (
                    <div key={label} className="circuit-legend__item">
                      <div className="circuit-legend__dot" style={{ background: color }} />
                      <span className="circuit-legend__label">{label}</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </CardShell>

          {/* Right column: Weather */}
          <div className="layout-right-col">
            <WeatherToggle
              currentWeather={weather.type}
              onWeatherChange={handleWeatherChange}
              isLoading={isWeatherLoading}
            />
          </div>
        </div>

        {/* ── Race Overview stats row ── */}
        {strategy && !isLoading && <StatsRow strategy={strategy} />}

        {/* ── Main chart area + side panel ── */}
        <div className="layout-charts-row">
          {/* Left: Tabbed charts */}
          <div className="layout-charts-left">
            {/* Tab card */}
            <CardShell title="Race Analysis" icon="📈" idx={1}
              badge={activeTab === 'lap_times' ? 'Lap Times' : activeTab === 'pit' ? 'Pit Strategy' : 'Tires'}
            >
              {/* Tab buttons */}
              <div className="tab-bar">
                {[
                  { id: 'lap_times', label: '📊 Expected Lap Times' },
                  { id: 'pit', label: '🔧 Pitstop Strategy' },
                  { id: 'tires', label: '🏎️ Tire Compounds' },
                ].map(tab => (
                  <button
                    key={tab.id}
                    id={`tab-${tab.id}`}
                    onClick={() => setActiveTab(tab.id)}
                    className={`tab-btn${activeTab === tab.id ? ' tab-btn--active' : ''}`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="tab-content">
                <AnimatePresence mode="wait">
                  {isLoading ? (
                    <LoadingOverlay testId="lap-chart-loading" />
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
                <div className="viz-grid">
                  <div>
                    <div className="section-label viz-label">Tire Degradation Curves</div>
                    <img
                      src={`data:image/png;base64,${strategy.visualizations.degradation_curves_b64}`}
                      alt="Tire degradation curves — all compounds"
                      className="viz-img"
                    />
                  </div>
                  <div>
                    <div className="section-label viz-label">Monte Carlo Distribution</div>
                    <img
                      src={`data:image/png;base64,${strategy.visualizations.lap_time_distribution_b64}`}
                      alt="Monte Carlo race time distribution"
                      className="viz-img"
                    />
                  </div>
                  <div>
                    <div className="section-label viz-label">Lap Time Strategy</div>
                    <img
                      src={`data:image/png;base64,${strategy.visualizations.strategy_comparison_b64}`}
                      alt="Expected lap times by compound"
                      className="viz-img"
                    />
                  </div>
                </div>
              </CardShell>
            )}
          </div>

          {/* Right sidebar: Telemetry */}
          <CardShell title="Race Telemetry" icon="📡" idx={3} badge="LIVE">
            {isLoading ? (
              <div className="telemetry-loading">
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

      <Footer />
    </div>
  )
}
