/**
 * CircuitMap.jsx
 * D3.js SVG circuit visualization with data-mapped key points
 * and animated F1 car that follows the track path.
 */
import React, { useEffect, useRef, useState, useCallback } from 'react'
import * as d3 from 'd3'
import { TRACK_PATHS, EVENT_COLORS, EVENT_ICONS, TIRE_COLORS } from '../data/trackPaths'

const COMPOUND_LABEL = {
  SOFT: 'S', MEDIUM: 'M', HARD: 'H', INTERMEDIATE: 'I', WET: 'W',
}

export default function CircuitMap({ trackId, keyPoints = [], currentStint, isAnimating }) {
  const svgRef      = useRef(null)
  const pathRef     = useRef(null)
  const carRef      = useRef(null)
  const animFrameRef = useRef(null)
  const progressRef  = useRef(0)

  const [tooltip, setTooltip] = useState(null)

  const trackDef = TRACK_PATHS[trackId] || TRACK_PATHS['suzuka']
  const compound = currentStint?.compound || 'MEDIUM'
  const carColor = TIRE_COLORS[compound] || TIRE_COLORS.MEDIUM

  // ── Draw track + key point markers ──────────────────────────────────────
  useEffect(() => {
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const [vx, vy, vw, vh] = trackDef.viewBox.split(' ').map(Number)

    svg.attr('viewBox', trackDef.viewBox)
       .attr('preserveAspectRatio', 'xMidYMid meet')

    // Background
    svg.append('rect')
      .attr('x', vx).attr('y', vy)
      .attr('width', vw).attr('height', vh)
      .attr('fill', '#f0f4ff')
      .attr('rx', 12)

    // Grid lines (subtle)
    const gridG = svg.append('g').attr('class', 'grid')
    for (let x = vx + 40; x < vw; x += 40) {
      gridG.append('line').attr('x1', x).attr('y1', vy).attr('x2', x).attr('y2', vh)
        .attr('stroke', 'rgba(26,31,58,0.04)').attr('stroke-width', 1)
    }
    for (let y = vy + 30; y < vh; y += 30) {
      gridG.append('line').attr('x1', vx).attr('y1', y).attr('x2', vw).attr('y2', y)
        .attr('stroke', 'rgba(26,31,58,0.04)').attr('stroke-width', 1)
    }

    // Track outline (outer glow)
    svg.append('path')
      .attr('d', trackDef.path)
      .attr('fill', 'none')
      .attr('stroke', 'rgba(26,31,58,0.12)')
      .attr('stroke-width', 22)
      .attr('stroke-linecap', 'round')
      .attr('stroke-linejoin', 'round')
      .attr('filter', 'url(#trackGlow)')

    // Glow filter
    const defs = svg.append('defs')
    const filter = defs.append('filter').attr('id', 'trackGlow')
    filter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'blur')
    const merge = filter.append('feMerge')
    merge.append('feMergeNode').attr('in', 'blur')
    merge.append('feMergeNode').attr('in', 'SourceGraphic')

    // Track road surface
    const trackPath = svg.append('path')
      .attr('d', trackDef.path)
      .attr('fill', 'none')
      .attr('stroke', '#cdd5f0')
      .attr('stroke-width', 16)
      .attr('stroke-linecap', 'round')
      .attr('stroke-linejoin', 'round')

    // Track center line
    svg.append('path')
      .attr('d', trackDef.path)
      .attr('fill', 'none')
      .attr('stroke', 'rgba(26,31,58,0.15)')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '6,6')
      .attr('stroke-linecap', 'round')

    pathRef.current = trackPath.node()

    // ── Key point markers ─────────────────────────────────────────────────
    const [, , w, h] = [vx, vy, vw, vh]
    keyPoints.forEach((kp, i) => {
      const x = kp.svg_x_pct * vw
      const y = kp.svg_y_pct * vh
      const color = EVENT_COLORS[kp.event_type] || '#888'
      const icon  = EVENT_ICONS[kp.event_type] || '?'

      const g = svg.append('g')
        .attr('transform', `translate(${x},${y})`)
        .style('cursor', 'pointer')

      // Pulse ring
      g.append('circle')
        .attr('r', 14)
        .attr('fill', `${color}20`)
        .attr('stroke', `${color}40`)
        .attr('stroke-width', 1.5)

      // Marker circle
      g.append('circle')
        .attr('r', 9)
        .attr('fill', color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)

      // Icon text
      g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('fill', '#fff')
        .attr('font-size', '7px')
        .attr('font-weight', '700')
        .attr('font-family', 'JetBrains Mono, monospace')
        .text(icon)

      // Tooltip on hover
      g.on('mouseenter', (event) => {
        const rect = svgRef.current.getBoundingClientRect()
        setTooltip({
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
          name: kp.name,
          desc: kp.description,
          type: kp.event_type,
          data: kp.simulation_data,
          color,
        })
      })
      .on('mouseleave', () => setTooltip(null))

      // Pit window annotation
      if (kp.event_type === 'PIT_WINDOW' && kp.simulation_data?.pit_window) {
        svg.append('text')
          .attr('x', x + 14)
          .attr('y', y + 3)
          .attr('fill', color)
          .attr('font-size', '7px')
          .attr('font-weight', '600')
          .attr('font-family', 'JetBrains Mono, monospace')
          .text(`PIT ${kp.simulation_data.pit_window}`)
      }
    })

    // ── Car element ───────────────────────────────────────────────────────
    const car = svg.append('g').attr('class', 'f1-car')
    
    // Car body (simplified F1 silhouette)
    car.append('ellipse')
      .attr('rx', 10).attr('ry', 4.5)
      .attr('fill', carColor)
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
    
    // Cockpit
    car.append('ellipse')
      .attr('cx', 2).attr('cy', 0)
      .attr('rx', 4).attr('ry', 3)
      .attr('fill', '#1a1f3a')
    
    // Front wing
    car.append('rect')
      .attr('x', 7).attr('y', -6)
      .attr('width', 2).attr('height', 12)
      .attr('fill', '#fff')
      .attr('rx', 1)
    
    // Rear wing
    car.append('rect')
      .attr('x', -10).attr('y', -7)
      .attr('width', 2.5).attr('height', 14)
      .attr('fill', carColor)
      .attr('rx', 1)

    // Exhaust glow
    car.append('ellipse')
      .attr('cx', -12).attr('cy', 0)
      .attr('rx', 3).attr('ry', 2.5)
      .attr('fill', '#FF6B35')
      .attr('opacity', 0.7)

    carRef.current = car

    // Position car at start
    if (pathRef.current) {
      const pathEl = pathRef.current
      const totalLen = pathEl.getTotalLength()
      const pt = pathEl.getPointAtLength(0)
      const ptNext = pathEl.getPointAtLength(5)
      const angle = Math.atan2(ptNext.y - pt.y, ptNext.x - pt.x) * 180 / Math.PI
      car.attr('transform', `translate(${pt.x},${pt.y}) rotate(${angle})`)
    }

  }, [trackId, keyPoints])

  // ── Animate car on track ───────────────────────────────────────────────
  useEffect(() => {
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
    if (!isAnimating || !pathRef.current || !carRef.current) return

    const pathEl = pathRef.current
    const totalLen = pathEl.getTotalLength()
    const speed = 0.0008  // fraction of path per frame

    const animate = () => {
      progressRef.current = (progressRef.current + speed) % 1
      const t = progressRef.current * totalLen
      const pt     = pathEl.getPointAtLength(t)
      const ptNext = pathEl.getPointAtLength((t + 8) % totalLen)
      const angle  = Math.atan2(ptNext.y - pt.y, ptNext.x - pt.x) * 180 / Math.PI

      carRef.current.attr('transform', `translate(${pt.x},${pt.y}) rotate(${angle})`)
      animFrameRef.current = requestAnimationFrame(animate)
    }

    animFrameRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animFrameRef.current)
  }, [isAnimating, trackId])

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      {/* Track label */}
      <div style={{
        position: 'absolute', top: 10, left: 14, zIndex: 2,
        display: 'flex', alignItems: 'center', gap: 6,
      }}>
        <span style={{ fontSize: '1.2rem' }}>{trackDef.country}</span>
        <span style={{
          fontWeight: 700, fontSize: '0.75rem', color: 'var(--f1-navy)',
          background: 'rgba(255,255,255,0.85)',
          padding: '3px 8px', borderRadius: '6px',
          backdropFilter: 'blur(8px)',
          border: '1px solid rgba(26,31,58,0.1)',
        }}>{trackDef.label}</span>
      </div>

      <svg
        ref={svgRef}
        style={{ width: '100%', height: '100%', minHeight: 260 }}
      />

      {/* Compound indicator */}
      <div style={{
        position: 'absolute', bottom: 10, right: 14, zIndex: 2,
        display: 'flex', alignItems: 'center', gap: 6,
        background: 'rgba(255,255,255,0.85)',
        padding: '4px 10px', borderRadius: '8px',
        backdropFilter: 'blur(8px)',
        border: '1px solid rgba(26,31,58,0.1)',
      }}>
        <div style={{
          width: 18, height: 18, borderRadius: '50%',
          background: carColor, border: '2px solid #fff',
          boxShadow: `0 0 8px ${carColor}60`,
          display: 'grid', placeItems: 'center',
          fontSize: '8px', fontWeight: 700, color: '#fff',
          fontFamily: 'JetBrains Mono, monospace',
        }}>
          {COMPOUND_LABEL[compound]}
        </div>
        <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--f1-navy)' }}>
          {compound}
        </span>
      </div>

      {/* Tooltip overlay */}
      {tooltip && (
        <div style={{
          position: 'absolute',
          left: tooltip.x + 12,
          top: tooltip.y - 10,
          zIndex: 100,
          background: 'var(--f1-navy)',
          color: '#fff',
          borderRadius: 8,
          padding: '8px 12px',
          maxWidth: 220,
          boxShadow: '0 8px 24px rgba(0,0,0,0.3)',
          pointerEvents: 'none',
          fontSize: '0.75rem',
          fontFamily: 'JetBrains Mono, monospace',
        }}>
          <div style={{ fontWeight: 700, color: tooltip.color, marginBottom: 3 }}>
            {tooltip.name}
          </div>
          <div style={{ color: '#cbd5e1', lineHeight: 1.5 }}>{tooltip.desc}</div>
          {tooltip.data?.pit_window && (
            <div style={{ marginTop: 4, color: '#10B981', fontWeight: 600 }}>
              Window: {tooltip.data.pit_window}
            </div>
          )}
          {tooltip.data?.avg_wear_pct != null && (
            <div style={{ marginTop: 4, color: '#F59E0B' }}>
              Wear: {tooltip.data.avg_wear_pct.toFixed(1)}%
            </div>
          )}
        </div>
      )}
    </div>
  )
}
