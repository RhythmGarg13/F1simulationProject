/**
 * ErrorBanner.jsx — Animated error message banner.
 */
import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function ErrorBanner({ error }) {
  return (
    <AnimatePresence>
      {error && (
        <motion.div
          className="error-banner"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          role="alert"
          aria-live="assertive"
        >
          <span className="error-banner__icon">⚠️</span>
          <div>
            <strong>Backend Error:</strong> {error}
            <br />
            <span className="error-banner__hint">
              Start the backend:{' '}
              <code className="error-banner__code">cd backend &amp;&amp; uvicorn main:app --reload</code>
            </span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
