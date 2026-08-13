/**
 * Header.jsx — App header with logo, track selector, and control buttons.
 */
import React from 'react'
import { TRACK_PATHS } from '../data/trackPaths'

export default function Header({ tracks, trackId, onTrackChange, isLoading, isAnimating, onToggleAnimation, onRecalculate }) {
  return (
    <header className="app-header">
      <div className="app-header__inner">
        {/* Logo */}
        <div className="app-header__logo">
          <div className="app-header__logo-icon">🏎️</div>
          <div>
            <div className="app-header__logo-title">F1 Strategy Engine</div>
            <div className="app-header__logo-sub">Monte Carlo · Telemetry · 2026 Season</div>
          </div>
        </div>

        {/* Track selector */}
        <div className="app-header__track">
          <span className="app-header__track-label">Circuit</span>
          <select
            id="track-selector"
            value={trackId}
            onChange={e => onTrackChange(e.target.value)}
            className="app-header__track-select"
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

        {/* Controls */}
        <div className="app-header__controls">
          <button
            id="toggle-animation"
            className="btn btn--ghost"
            onClick={onToggleAnimation}
          >
            {isAnimating ? '⏸ Pause' : '▶ Animate'}
          </button>
          <button
            id="recalculate-btn"
            className="btn btn--primary"
            onClick={onRecalculate}
            disabled={isLoading}
          >
            {isLoading ? '⟳ Computing...' : '⚡ Recalculate'}
          </button>
        </div>
      </div>
    </header>
  )
}
