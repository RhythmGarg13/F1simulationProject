/**
 * TelemetryCard.jsx
 * Real-time telemetry numbers panel — Monte Carlo stats and race overview.
 */
import React from 'react'
import { motion } from 'framer-motion'

function StatItem({ label, value, unit, color, highlight }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 3,
        padding: '10px 12px',
        borderRadius: 10,
        background: highlight ? 'rgba(225,6,0,0.06)' : 'rgba(26,31,58,0.04)',
        border: highlight ? '1px solid rgba(225,6,0,0.15)' : '1px solid rgba(26,31,58,0.06)',
      }}
    >
      <div style={{
        fontSize: '0.65rem',
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        color: 'var(--f1-navy-light)',
      }}>
        {label}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
        <span className="mono" style={{
          fontSize: '1.125rem',
          fontWeight: 800,
          color: color || 'var(--f1-navy)',
          lineHeight: 1,
        }}>
          {value}
        </span>
        {unit && (
          <span style={{ fontSize: '0.68rem', color: 'var(--f1-navy-light)', fontFamily: 'JetBrains Mono, monospace' }}>
            {unit}
          </span>
        )}
      </div>
    </motion.div>
  )
}

function formatTime(secs) {
  if (!secs) return '—'
  const m = Math.floor(secs / 60)
  const s = (secs % 60).toFixed(3)
  return `${m}:${String(s).padStart(6, '0')}`
}

export default function TelemetryCard({ strategy, mcStats }) {
  if (!strategy) return null

  const ci_low  = mcStats?.confidence_interval_95_low
  const ci_high = mcStats?.confidence_interval_95_high
  const ciRange = ci_low && ci_high ? `±${((ci_high - ci_low) / 2).toFixed(1)}s` : '—'

  return (
    <div style={{ padding: '0 20px 20px', display: 'flex', flexDirection: 'column', gap: 10 }}>

      {/* Race time — highlight */}
      <div style={{
        padding: '14px 16px',
        borderRadius: 12,
        background: 'linear-gradient(135deg, rgba(225,6,0,0.08), rgba(225,6,0,0.04))',
        border: '1px solid rgba(225,6,0,0.15)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div>
          <div style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase',
            letterSpacing: '0.08em', color: 'var(--f1-red)', marginBottom: 3 }}>
            Optimal Race Time
          </div>
          <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--f1-navy)' }}>
            {strategy.optimal_total_time_formatted}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase',
            letterSpacing: '0.08em', color: 'var(--f1-navy-light)', marginBottom: 3 }}>
            Confidence
          </div>
          <div className="mono" style={{ fontSize: '1rem', fontWeight: 700, color: '#10B981' }}>
            {((mcStats?.optimal_strategy_probability || 0) * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        <StatItem
          label="Total Laps"
          value={strategy.total_laps}
          color="var(--f1-navy)"
        />
        <StatItem
          label="Pit Stops"
          value={strategy.pit_stops?.length || 0}
          color="var(--f1-red)"
          highlight
        />
        <StatItem
          label="MC Simulations"
          value={(mcStats?.n_simulations || 0).toLocaleString()}
          color="var(--f1-teal)"
        />
        <StatItem
          label="MC Std Dev"
          value={mcStats?.std_race_time_s ? `±${mcStats.std_race_time_s.toFixed(1)}` : '—'}
          unit="s"
          color="var(--f1-navy)"
        />
        <StatItem
          label="95% CI Range"
          value={ciRange}
          color="#8B5CF6"
        />
        <StatItem
          label="SLSQP Iters"
          value={strategy.optimizer_iterations || 0}
          color="var(--f1-navy)"
        />
        <StatItem
          label="||∇g(x)||₂"
          value={strategy.constraint_norm ? strategy.constraint_norm.toFixed(6) : '—'}
          color={strategy.optimizer_converged ? '#10B981' : '#F59E0B'}
          highlight={!strategy.optimizer_converged}
        />
        <StatItem
          label="Converged"
          value={strategy.optimizer_converged ? 'YES' : 'NO'}
          color={strategy.optimizer_converged ? '#10B981' : '#EF4444'}
        />
      </div>

      {/* Weather note */}
      {strategy.weather_note && (
        <div style={{
          padding: '10px 12px',
          borderRadius: 10,
          background: 'rgba(0,180,216,0.06)',
          border: '1px solid rgba(0,180,216,0.2)',
          fontSize: '0.72rem',
          color: 'var(--f1-navy-light)',
          lineHeight: 1.6,
        }}>
          {strategy.weather_note}
        </div>
      )}

      {/* Strategy delta */}
      {strategy.strategy_delta && (
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          style={{
            padding: '10px 12px',
            borderRadius: 10,
            background: 'rgba(245,158,11,0.08)',
            border: '1px solid rgba(245,158,11,0.25)',
            fontSize: '0.72rem',
            color: '#92400e',
            fontWeight: 600,
            lineHeight: 1.6,
            display: 'flex',
            gap: 8,
            alignItems: 'flex-start',
          }}
        >
          <span style={{ fontSize: '1rem', flexShrink: 0 }}>⚡</span>
          <span>{strategy.strategy_delta}</span>
        </motion.div>
      )}
    </div>
  )
}
