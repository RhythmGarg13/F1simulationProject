/**
 * Footer.jsx — App footer with tech stack info.
 */
import React from 'react'

export default function Footer() {
  return (
    <footer className="app-footer">
      <div className="app-footer__inner">
        <div className="app-footer__title">
          <strong>F1 Race Strategy &amp; Telemetry Simulation Engine</strong>
          {' '}— Python · Pandas · NumPy · Scipy SLSQP · Seaborn · React
        </div>
        <div className="app-footer__detail mono">
          SLSQP Optimisation · g(x) Constraints · Constraint Sensitivity Diagnostic · All 24 F1 2026 Tracks
        </div>
      </div>
    </footer>
  )
}
