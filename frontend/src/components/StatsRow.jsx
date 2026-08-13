/**
 * StatsRow.jsx — Race overview stats strip shown after strategy loads.
 */
import React from 'react'
import { motion } from 'framer-motion'

const STATS = (strategy) => [
  { label: 'Track',          value: strategy.track_name?.split('(')[0].trim().split(' ').slice(0, 2).join(' '), icon: '🏁' },
  { label: 'Optimal Time',   value: strategy.optimal_total_time_formatted, icon: '⏱', mono: true, highlight: true },
  { label: 'Pit Stops',      value: strategy.pit_stops?.length, icon: '🔧' },
  { label: 'Total Laps',     value: strategy.total_laps, icon: '🔄', mono: true },
  { label: 'Weather',        value: strategy.weather_type, icon: '🌡️' },
  { label: 'MC Probability', value: `${((strategy.monte_carlo_stats?.optimal_strategy_probability || 0) * 100).toFixed(0)}%`, icon: '📊', mono: true },
]

export default function StatsRow({ strategy }) {
  if (!strategy) return null

  return (
    <motion.div
      className="stats-row"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {STATS(strategy).map((item, i) => (
        <motion.div
          key={item.label}
          className={`stats-card card card--flat${item.highlight ? ' stats-card--highlight' : ''}`}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
        >
          <div className="stats-card__label-row">
            <span className="stats-card__icon">{item.icon}</span>
            <span className="stats-card__label">{item.label}</span>
          </div>
          <div className={`stats-card__value${item.mono ? ' mono' : ''}${item.highlight ? ' stats-card__value--highlight' : ''}`}>
            {item.value ?? '—'}
          </div>
        </motion.div>
      ))}
    </motion.div>
  )
}
