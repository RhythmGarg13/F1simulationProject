/**
 * PitStrategy.jsx
 * Pitstop strategy timeline card.
 */
import React from 'react'
import { motion } from 'framer-motion'
import { TIRE_COLORS } from '../data/trackPaths'

const TIRE_LABEL = {
  SOFT: 'S', MEDIUM: 'M', HARD: 'H', INTERMEDIATE: 'I', WET: 'W',
}

function TireCircle({ compound, size = 28 }) {
  const color = TIRE_COLORS[compound] || '#888'
  return (
    <div style={{
      width: size, height: size,
      borderRadius: '50%',
      background: color,
      border: '2px solid #fff',
      boxShadow: `0 2px 8px ${color}50`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: compound === 'HARD' ? '#333' : '#fff',
      fontSize: size * 0.38,
      fontWeight: 800,
      fontFamily: 'JetBrains Mono, monospace',
      flexShrink: 0,
    }}>
      {TIRE_LABEL[compound] || '?'}
    </div>
  )
}

export default function PitStrategy({ stints = [], pitStops = [], totalLaps = 0 }) {
  if (!stints.length) return (
    <div style={{ padding: '20px', textAlign: 'center', color: 'var(--f1-navy-light)' }}>
      No strategy data available
    </div>
  )

  return (
    <div style={{ padding: '0 20px 20px', display: 'flex', flexDirection: 'column', gap: 14 }}>

      {/* Visual pit timeline */}
      <div style={{ position: 'relative', paddingTop: 8 }}>
        <div style={{
          height: 8, borderRadius: 4,
          background: 'rgba(26,31,58,0.06)',
          position: 'relative', overflow: 'visible',
        }}>
          {stints.map((stint, i) => {
            const left = ((stint.start_lap - 1) / totalLaps) * 100
            const width = (stint.laps_on_tire / totalLaps) * 100
            const color = TIRE_COLORS[stint.compound] || '#888'
            return (
              <motion.div
                key={i}
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ delay: i * 0.1, duration: 0.5, ease: 'easeOut' }}
                style={{
                  position: 'absolute',
                  left: `${left}%`,
                  width: `${width}%`,
                  height: '100%',
                  background: `linear-gradient(90deg, ${color}dd, ${color}bb)`,
                  borderRadius: 4,
                  transformOrigin: 'left center',
                }}
              />
            )
          })}
        </div>

        {/* Pit stop markers */}
        {pitStops.map((pit, i) => {
          const left = ((pit.pit_lap - 1) / totalLaps) * 100
          return (
            <div key={i} style={{
              position: 'absolute',
              left: `${left}%`,
              top: -8,
              transform: 'translateX(-50%)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}>
              <div style={{
                width: 2, height: 22,
                background: 'var(--f1-navy)',
                borderRadius: 2,
              }} />
              <div style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.6rem',
                fontWeight: 700,
                color: 'var(--f1-navy)',
                marginTop: 2,
                whiteSpace: 'nowrap',
              }}>L{pit.pit_lap}</div>
            </div>
          )
        })}

        {/* Lap range labels */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 20,
          fontFamily: 'JetBrains Mono, monospace', fontSize: '0.68rem', color: 'var(--f1-navy-light)' }}>
          <span>L1</span>
          <span>L{Math.round(totalLaps / 2)}</span>
          <span>L{totalLaps}</span>
        </div>
      </div>

      <div className="divider" />

      {/* Stint breakdown */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {stints.map((stint, i) => {
          const pit = pitStops[i - 1]
          const color = TIRE_COLORS[stint.compound] || '#888'
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '10px 12px',
                borderRadius: 'var(--radius-md)',
                background: `${color}10`,
                border: `1px solid ${color}25`,
              }}
            >
              <TireCircle compound={stint.compound} size={32} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontWeight: 700, fontSize: '0.8rem', color: 'var(--f1-navy)',
                  display: 'flex', alignItems: 'center', gap: 6,
                }}>
                  Stint {stint.stint_number}
                  <span style={{
                    fontFamily: 'JetBrains Mono, monospace',
                    fontSize: '0.68rem',
                    fontWeight: 600,
                    padding: '1px 6px',
                    borderRadius: 4,
                    background: `${color}20`,
                    color,
                  }}>
                    {stint.compound}
                  </span>
                </div>
                <div style={{
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '0.72rem',
                  color: 'var(--f1-navy-light)',
                  marginTop: 2,
                }}>
                  L{stint.start_lap}–L{stint.end_lap} · {stint.laps_on_tire} laps
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: 'var(--f1-navy)',
                }}>
                  {(stint.avg_lap_time_s / 1).toFixed(3)}s
                </div>
                <div style={{ fontSize: '0.68rem', color: 'var(--f1-navy-light)', fontFamily: 'JetBrains Mono, monospace' }}>
                  avg lap
                </div>
              </div>
              {pit && (
                <div style={{
                  textAlign: 'right',
                  borderLeft: '1px solid rgba(26,31,58,0.08)',
                  paddingLeft: 10,
                }}>
                  <div style={{
                    fontFamily: 'JetBrains Mono, monospace',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    color: 'var(--f1-red)',
                  }}>
                    +{pit.time_loss_s.toFixed(1)}s
                  </div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--f1-navy-light)', fontFamily: 'JetBrains Mono, monospace' }}>
                    pit loss
                  </div>
                </div>
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Pit stop reasons */}
      {pitStops.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div className="section-label">Pit Stop Analysis</div>
          {pitStops.map((pit, i) => (
            <div key={i} style={{
              padding: '8px 12px',
              borderRadius: 8,
              background: 'rgba(26,31,58,0.04)',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 8,
            }}>
              <div style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontWeight: 700,
                fontSize: '0.75rem',
                color: 'var(--f1-red)',
                flexShrink: 0,
                minWidth: 24,
              }}>
                P{i + 1}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--f1-navy-light)', lineHeight: 1.5 }}>
                <span style={{ fontWeight: 600, color: 'var(--f1-navy)', fontFamily: 'JetBrains Mono, monospace' }}>
                  Lap {pit.pit_lap}:
                </span>{' '}
                {pit.strategic_reason}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
