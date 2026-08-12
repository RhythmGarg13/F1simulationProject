/**
 * WeatherToggle.jsx
 * Weather selection panel. Sends immediate API update on change.
 */
import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const WEATHER_OPTIONS = [
  {
    id: 'DRY',
    icon: '☀️',
    label: 'Dry',
    desc: 'Hot tarmac, dry conditions',
    airTemp: 26,
    trackTemp: 42,
    rainIntensity: 0.0,
    windSpeed: 8,
    color: '#F59E0B',
  },
  {
    id: 'LIGHT_RAIN',
    icon: '🌦',
    label: 'Light Rain',
    desc: 'Damp track, Inter recommended',
    airTemp: 18,
    trackTemp: 22,
    rainIntensity: 0.35,
    windSpeed: 18,
    color: '#3B82F6',
  },
  {
    id: 'HEAVY_RAIN',
    icon: '🌧',
    label: 'Heavy Rain',
    desc: 'Standing water, Wet mandatory',
    airTemp: 14,
    trackTemp: 16,
    rainIntensity: 0.85,
    windSpeed: 30,
    color: '#1D4ED8',
  },
]

export default function WeatherToggle({ currentWeather, onWeatherChange, isLoading }) {
  return (
    <div className="card" style={{ padding: '0' }}>
      <div className="card-header">
        <div className="card-header__icon">🌡️</div>
        <div>
          <div className="card-header__title">Dynamic Weather</div>
          <div style={{ fontSize: '0.72rem', color: 'var(--f1-navy-light)', marginTop: 2 }}>
            Changing weather triggers full re-optimization
          </div>
        </div>
        {isLoading && (
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
            <div className="spinner" style={{ width: 20, height: 20, borderWidth: 2 }} />
            <span style={{ fontSize: '0.75rem', color: 'var(--f1-red)', fontWeight: 600 }}>
              Recalculating...
            </span>
          </div>
        )}
      </div>

      <div style={{ padding: '16px 20px 20px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {WEATHER_OPTIONS.map((option) => {
          const isActive = currentWeather === option.id
          return (
            <motion.button
              key={option.id}
              id={`weather-btn-${option.id.toLowerCase()}`}
              onClick={() => !isLoading && onWeatherChange(option)}
              whileHover={{ scale: isActive ? 1 : 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '12px 14px',
                borderRadius: 'var(--radius-md)',
                border: isActive
                  ? `2px solid ${option.color}`
                  : '2px solid transparent',
                background: isActive
                  ? `${option.color}15`
                  : 'rgba(26,31,58,0.04)',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                textAlign: 'left',
                width: '100%',
                opacity: isLoading && !isActive ? 0.5 : 1,
              }}
            >
              <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>{option.icon}</span>
              <div style={{ flex: 1 }}>
                <div style={{
                  fontWeight: 700,
                  fontSize: '0.875rem',
                  color: isActive ? option.color : 'var(--f1-navy)',
                }}>
                  {option.label}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--f1-navy-light)', marginTop: 1 }}>
                  {option.desc}
                </div>
              </div>
              {isActive && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    background: option.color,
                    flexShrink: 0,
                    boxShadow: `0 0 8px ${option.color}`,
                  }}
                />
              )}
            </motion.button>
          )
        })}
      </div>

      {/* Weather parameters display */}
      <AnimatePresence mode="wait">
        {WEATHER_OPTIONS.filter(o => o.id === currentWeather).map(opt => (
          <motion.div
            key={opt.id}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            style={{
              borderTop: '1px solid rgba(26,31,58,0.08)',
              padding: '12px 20px',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: 10,
            }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <div style={{ fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--f1-navy-light)', fontWeight: 600 }}>Air Temp</div>
              <div className="mono" style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--f1-navy)' }}>{opt.airTemp}°C</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <div style={{ fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--f1-navy-light)', fontWeight: 600 }}>Track Temp</div>
              <div className="mono" style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--f1-navy)' }}>{opt.trackTemp}°C</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <div style={{ fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--f1-navy-light)', fontWeight: 600 }}>Rain</div>
              <div className="mono" style={{ fontSize: '1rem', fontWeight: 700, color: opt.color }}>{(opt.rainIntensity * 100).toFixed(0)}%</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <div style={{ fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--f1-navy-light)', fontWeight: 600 }}>Wind</div>
              <div className="mono" style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--f1-navy)' }}>{opt.windSpeed} km/h</div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
