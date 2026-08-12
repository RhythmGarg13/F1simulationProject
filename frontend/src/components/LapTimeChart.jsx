/**
 * LapTimeChart.jsx
 * Recharts line chart showing per-lap times colored by tire compound.
 */
import React, { useMemo } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Legend,
} from 'recharts'
import { TIRE_COLORS } from '../data/trackPaths'

const COMPOUND_ORDER = ['SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET']

function formatLapTime(secs) {
  const m = Math.floor(secs / 60)
  const s = (secs % 60).toFixed(3).padStart(6, '0')
  return `${m}:${s}`
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(26,31,58,0.1)',
      borderRadius: 10,
      padding: '10px 14px',
      boxShadow: '0 8px 24px rgba(26,31,58,0.12)',
      fontFamily: 'JetBrains Mono, monospace',
    }}>
      <div style={{ fontWeight: 700, fontSize: '0.8rem', color: '#1a1f3a', marginBottom: 6 }}>
        Lap {label}
      </div>
      {payload.map((p, i) => (
        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', gap: 16, fontSize: '0.72rem' }}>
          <span style={{ color: p.color, fontWeight: 600 }}>{p.name}</span>
          <span style={{ color: '#1a1f3a', fontWeight: 700 }}>
            {formatLapTime(p.value)}
          </span>
        </div>
      ))}
      {d && (
        <>
          <div style={{ borderTop: '1px solid rgba(26,31,58,0.08)', marginTop: 6, paddingTop: 6, fontSize: '0.68rem', color: '#6b7280' }}>
            Compound: {d.tire_compound} | Age: {d.tire_age}L | Wear: {d.tire_wear_pct?.toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.68rem', color: '#6b7280', marginTop: 2 }}>
            Fuel: {d.fuel_load_kg?.toFixed(1)}kg
          </div>
        </>
      )}
    </div>
  )
}

export default function LapTimeChart({ lapData, pitStops }) {
  if (!lapData?.length) return (
    <div style={{ height: 240, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ color: 'var(--f1-navy-light)', fontSize: '0.875rem' }}>No lap data available</div>
    </div>
  )

  const compounds = [...new Set(lapData.map(d => d.tire_compound))]

  // Build one series per compound with nulls for other laps
  const chartData = lapData.map(d => {
    const row = { lap: d.lap, ...d }
    compounds.forEach(c => {
      row[c] = d.tire_compound === c ? d.lap_time_s : null
    })
    return row
  })

  const yMin = Math.min(...lapData.map(d => d.lap_time_s)) - 1
  const yMax = Math.max(...lapData.map(d => d.lap_time_s)) + 2

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(26,31,58,0.06)" />
        <XAxis
          dataKey="lap"
          tick={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, fill: '#4a5568' }}
          tickLine={false}
          axisLine={{ stroke: 'rgba(26,31,58,0.1)' }}
          label={{ value: 'Lap', position: 'insideBottom', offset: -2, fontSize: 10, fill: '#4a5568' }}
        />
        <YAxis
          domain={[yMin, yMax]}
          tickFormatter={formatLapTime}
          tick={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, fill: '#4a5568' }}
          tickLine={false}
          axisLine={false}
          width={52}
        />
        <Tooltip content={<CustomTooltip />} />

        {/* Pit stop reference lines */}
        {pitStops?.map((pit, i) => (
          <ReferenceLine
            key={i}
            x={pit.pit_lap}
            stroke="rgba(26,31,58,0.4)"
            strokeDasharray="4 3"
            label={{ value: `PIT`, position: 'top', fontSize: 9, fill: '#1a1f3a', fontFamily: 'JetBrains Mono, monospace' }}
          />
        ))}

        {/* One line per compound */}
        {compounds.map(compound => (
          <Line
            key={compound}
            type="monotone"
            dataKey={compound}
            stroke={TIRE_COLORS[compound] || '#888'}
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 5, strokeWidth: 2, stroke: '#fff' }}
            name={compound}
            connectNulls={false}
          />
        ))}
        <Legend
          iconType="circle"
          iconSize={8}
          wrapperStyle={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '0.72rem', paddingTop: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
