/**
 * TireStrategy.jsx
 * Tire compound usage visualization — donut chart + breakdown table.
 */
import React from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { motion } from 'framer-motion'
import { TIRE_COLORS } from '../data/trackPaths'

const TIRE_LABEL_FULL = {
  SOFT: 'Soft (S)', MEDIUM: 'Medium (M)', HARD: 'Hard (H)',
  INTERMEDIATE: 'Inter (I)', WET: 'Wet (W)',
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]
  return (
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(26,31,58,0.1)',
      borderRadius: 8,
      padding: '8px 12px',
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: '0.75rem',
      boxShadow: '0 4px 16px rgba(26,31,58,0.1)',
    }}>
      <div style={{ fontWeight: 700, color: d.payload.color }}>{d.name}</div>
      <div style={{ color: '#1a1f3a', marginTop: 2 }}>
        {d.value} laps ({((d.payload.value / d.payload.total) * 100).toFixed(0)}%)
      </div>
    </div>
  )
}

export default function TireStrategy({ stints = [], totalLaps = 0 }) {
  if (!stints.length) return (
    <div style={{ padding: 20, textAlign: 'center', color: 'var(--f1-navy-light)' }}>
      No tire data available
    </div>
  )

  // Aggregate laps per compound
  const compoundMap = {}
  stints.forEach(s => {
    if (!compoundMap[s.compound]) compoundMap[s.compound] = 0
    compoundMap[s.compound] += s.laps_on_tire
  })

  const pieData = Object.entries(compoundMap).map(([compound, laps]) => ({
    name: TIRE_LABEL_FULL[compound] || compound,
    value: laps,
    total: totalLaps,
    compound,
    color: TIRE_COLORS[compound] || '#888',
  }))

  return (
    <div style={{ padding: '0 20px 20px', display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* Donut Chart */}
      <div style={{ height: 200 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={3}
              dataKey="value"
            >
              {pieData.map((entry, i) => (
                <Cell key={i} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              iconType="circle"
              iconSize={8}
              wrapperStyle={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.68rem',
                lineHeight: '1.8',
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Total laps center label */}
      <div style={{
        display: 'flex', justifyContent: 'center',
        marginTop: -100, marginBottom: 80, pointerEvents: 'none',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div className="mono" style={{ fontWeight: 800, fontSize: '1.4rem', color: 'var(--f1-navy)', lineHeight: 1 }}>
            {totalLaps}
          </div>
          <div style={{ fontSize: '0.65rem', color: 'var(--f1-navy-light)', fontWeight: 600,
            textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            total laps
          </div>
        </div>
      </div>

      <div className="divider" />

      {/* Compound breakdown */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div className="section-label">Compound Usage</div>
        {pieData.map((entry, i) => {
          const pct = (entry.value / totalLaps) * 100
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.06 }}
              style={{ display: 'flex', flexDirection: 'column', gap: 5 }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{
                    width: 10, height: 10, borderRadius: '50%',
                    background: entry.color, flexShrink: 0,
                    boxShadow: `0 0 6px ${entry.color}50`,
                  }} />
                  <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--f1-navy)' }}>
                    {entry.name}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                  <span className="mono" style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--f1-navy)' }}>
                    {entry.value}L
                  </span>
                  <span className="mono" style={{ fontSize: '0.7rem', color: 'var(--f1-navy-light)' }}>
                    {pct.toFixed(0)}%
                  </span>
                </div>
              </div>
              {/* Progress bar */}
              <div style={{
                height: 4, borderRadius: 4,
                background: 'rgba(26,31,58,0.06)',
                overflow: 'hidden',
              }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${pct}%` }}
                  transition={{ delay: i * 0.06 + 0.1, duration: 0.6, ease: 'easeOut' }}
                  style={{
                    height: '100%',
                    background: `linear-gradient(90deg, ${entry.color}, ${entry.color}bb)`,
                    borderRadius: 4,
                  }}
                />
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Degradation summary */}
      {stints.length > 0 && (
        <>
          <div className="divider" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div className="section-label">Degradation Summary</div>
            {stints.map((stint, i) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '6px 10px',
                borderRadius: 8,
                background: `${TIRE_COLORS[stint.compound] || '#888'}0d`,
                border: `1px solid ${TIRE_COLORS[stint.compound] || '#888'}20`,
              }}>
                <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--f1-navy)' }}>
                  Stint {stint.stint_number} — {stint.compound}
                </span>
                <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--f1-navy-light)', fontWeight: 600 }}>
                  +{stint.total_degradation_s.toFixed(2)}s total deg
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
