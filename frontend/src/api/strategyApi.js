/**
 * strategyApi.js — F1 Race Strategy Engine API Client
 *
 * Axios-based API client for communicating with the FastAPI backend.
 * All calls go through the Vite proxy (/api → http://localhost:8000/api).
 */
import axios from 'axios'

const BASE_URL = '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,  // 2 min — Monte Carlo can take time
  headers: { 'Content-Type': 'application/json' },
})

/**
 * Calculate the full race strategy for a given track + weather.
 * @param {Object} params
 * @param {string} params.trackId
 * @param {string} params.driverName
 * @param {string} params.teamName
 * @param {number} params.initialFuelKg
 * @param {string} params.startingCompound
 * @param {number} params.startingPosition
 * @param {number} params.nSimulations
 * @param {Object} params.weather
 * @returns {Promise<Object>} StrategyResponse
 */
export async function calculateStrategy(params) {
  const payload = {
    track_id: params.trackId,
    driver_name: params.driverName || 'VER',
    team_name: params.teamName || 'Red Bull Racing',
    initial_fuel_kg: params.initialFuelKg || 110.0,
    starting_compound: params.startingCompound || 'MEDIUM',
    starting_position: params.startingPosition || 1,
    n_simulations: params.nSimulations || 3000,
    weather: {
      weather_type: params.weather?.type || 'DRY',
      air_temp_c: params.weather?.airTemp || 24.0,
      track_temp_c: params.weather?.trackTemp || 38.0,
      rain_intensity: params.weather?.rainIntensity || 0.0,
      wind_speed_kph: params.weather?.windSpeed || 10.0,
    },
  }
  const { data } = await api.post('/calculate_strategy', payload)
  return data
}

/**
 * Fetch all available F1 2026 tracks.
 * @returns {Promise<Array>} List of track objects
 */
export async function fetchTracks() {
  const { data } = await api.get('/tracks')
  return data.tracks
}

/**
 * Fetch metadata for a specific track.
 * @param {string} trackId
 * @returns {Promise<Object>}
 */
export async function fetchTrack(trackId) {
  const { data } = await api.get(`/tracks/${trackId}`)
  return data
}

/**
 * Update weather and trigger re-optimization.
 * @param {Object} params
 * @returns {Promise<Object>} Updated StrategyResponse
 */
export async function updateWeather(params) {
  const url = `/update_weather?track_id=${params.trackId}&driver_name=${encodeURIComponent(params.driverName)}&team_name=${encodeURIComponent(params.teamName)}&prev_weather_type=${params.prevWeatherType}`
  const payload = {
    weather_type: params.weather.type,
    air_temp_c: params.weather.airTemp || 20.0,
    track_temp_c: params.weather.trackTemp || 28.0,
    rain_intensity: params.weather.rainIntensity || 0.0,
    wind_speed_kph: params.weather.windSpeed || 10.0,
  }
  const { data } = await api.post(url, payload)
  return data
}
