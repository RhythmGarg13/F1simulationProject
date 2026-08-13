/**
 * Dashboard.test.jsx — Unit tests for the Dashboard component.
 *
 * Tests:
 *   1. Error banner renders when calculateStrategy rejects.
 *   2. Loading overlay renders while isLoading is true.
 *   3. Track selector falls back to TRACK_PATHS when fetchTracks() rejects.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

// Mock the API module before importing Dashboard
vi.mock('../api/strategyApi', () => ({
  calculateStrategy: vi.fn(),
  fetchTracks: vi.fn(),
  updateWeather: vi.fn(),
}))

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => React.createElement('div', props, children),
    button: ({ children, ...props }) => React.createElement('button', props, children),
  },
  AnimatePresence: ({ children }) => children,
}))

// Mock heavy D3/recharts child components
vi.mock('./CircuitMap', () => ({
  default: () => React.createElement('div', { 'data-testid': 'circuit-map' }, 'CircuitMap'),
}))
vi.mock('./LapTimeChart', () => ({
  default: () => React.createElement('div', { 'data-testid': 'lap-time-chart' }, 'LapTimeChart'),
}))
vi.mock('./PitStrategy', () => ({
  default: () => React.createElement('div', { 'data-testid': 'pit-strategy' }, 'PitStrategy'),
}))
vi.mock('./TireStrategy', () => ({
  default: () => React.createElement('div', { 'data-testid': 'tire-strategy' }, 'TireStrategy'),
}))
vi.mock('./TelemetryCard', () => ({
  default: () => React.createElement('div', { 'data-testid': 'telemetry-card' }, 'TelemetryCard'),
}))
vi.mock('./WeatherToggle', () => ({
  default: () => React.createElement('div', { 'data-testid': 'weather-toggle' }, 'WeatherToggle'),
}))

import { calculateStrategy, fetchTracks } from '../api/strategyApi'
import Dashboard from './Dashboard'

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Default: fetchTracks succeeds with a minimal list
    fetchTracks.mockResolvedValue([
      { track_id: 'suzuka', name: 'Suzuka Circuit', country: 'Japan' },
    ])
  })

  it('renders error banner when calculateStrategy rejects', async () => {
    calculateStrategy.mockRejectedValue(new Error('Backend connection failed'))

    render(React.createElement(Dashboard))

    // Wait for the error to appear
    await waitFor(() => {
      expect(screen.getByText(/Backend Error/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('renders loading state while isLoading is true', async () => {
    // Keep the promise pending so loading stays true
    calculateStrategy.mockReturnValue(new Promise(() => {}))

    render(React.createElement(Dashboard))

    // The loading overlay text should appear
    await waitFor(() => {
      expect(screen.getByText(/Monte Carlo Simulation/i)).toBeInTheDocument()
    }, { timeout: 2000 })
  })

  it('falls back to TRACK_PATHS when fetchTracks rejects', async () => {
    fetchTracks.mockRejectedValue(new Error('Network error'))
    // Keep strategy pending to prevent errors from strategy call
    calculateStrategy.mockReturnValue(new Promise(() => {}))

    render(React.createElement(Dashboard))

    // Should still render a track selector (fallback local data)
    await waitFor(() => {
      const selector = document.getElementById('track-selector')
      expect(selector).not.toBeNull()
    }, { timeout: 2000 })
  })
})
