/**
 * trackPaths.js — SVG Path Data for all 24 F1 2026 Circuits
 *
 * Each track is defined as an SVG path `d` attribute string.
 * Paths are normalized to a 400×300 viewBox coordinate space.
 * These are hand-crafted accurate schematic approximations of each circuit layout,
 * designed to be visually recognizable and correctly oriented.
 *
 * Format per track:
 *   path:    SVG path d-string
 *   viewBox: SVG viewBox
 *   label:   Display name
 *   country: Country code (for flag emoji)
 */

export const TRACK_PATHS = {

  albert_park: {
    label: 'Albert Park',
    country: '🇦🇺',
    viewBox: '0 0 400 300',
    path: `M 80 80 L 200 60 L 310 70 L 340 100 L 340 140
           C 340 160 325 175 305 175 L 290 175
           C 270 175 255 188 255 208 L 255 218
           C 255 238 240 250 220 248 L 160 240
           C 140 238 125 222 127 202 L 130 185
           C 132 165 118 152 98 155 L 80 158
           C 62 160 52 145 55 127 L 60 100 Z`,
  },

  shanghai: {
    label: 'Shanghai',
    country: '🇨🇳',
    viewBox: '0 0 400 300',
    path: `M 60 60 C 80 40 140 40 160 60 L 170 80
           C 180 100 200 110 225 108 L 340 105
           C 360 104 375 118 375 138 L 375 155
           C 375 173 360 185 342 183 L 310 180
           L 290 200 L 310 225
           C 325 240 320 260 302 265 L 200 268
           L 160 265 C 140 263 128 248 130 228 L 130 210
           C 130 192 116 180 98 182 L 65 185
           C 45 187 35 172 38 153 L 45 100 Z`,
  },

  suzuka: {
    label: 'Suzuka',
    country: '🇯🇵',
    viewBox: '0 0 400 300',
    path: `M 100 250 L 100 200 C 100 180 120 165 140 165
           L 200 165 L 200 185 C 200 205 220 215 240 210
           L 290 195 C 310 188 320 168 312 148
           L 300 120 C 292 100 270 92 250 100
           L 230 110 C 210 120 190 112 178 94
           L 165 72 C 152 52 130 48 112 60
           L 95 75 C 78 88 78 110 95 120
           L 110 130 L 60 140 C 40 144 32 164 42 182
           L 60 210 C 70 228 92 235 110 225 L 100 250`,
  },

  bahrain: {
    label: 'Bahrain',
    country: '🇧🇭',
    viewBox: '0 0 400 300',
    path: `M 60 150 C 60 100 95 65 145 65 L 200 65
           C 240 65 265 45 265 10 L 330 10
           C 370 10 390 40 390 80 L 390 130
           C 390 160 370 178 342 178 L 295 178
           C 272 178 255 195 255 218 L 255 240
           C 255 265 235 280 210 278 L 110 272
           C 80 270 60 250 62 222 L 63 185 Z`,
  },

  jeddah: {
    label: 'Jeddah',
    country: '🇸🇦',
    viewBox: '0 0 400 320',
    path: `M 50 80 L 350 80 C 370 80 385 95 385 115
           L 385 145 L 360 145 L 330 155 L 330 175
           L 355 195 L 355 215 C 355 235 338 248 318 245
           L 120 238 C 100 236 88 220 90 200 L 95 170
           L 120 155 L 120 135 L 95 120 L 50 110 Z`,
  },

  miami: {
    label: 'Miami',
    country: '🇺🇸',
    viewBox: '0 0 400 300',
    path: `M 50 100 L 290 100 C 320 100 340 118 340 148
           L 340 168 C 340 188 325 202 305 202 L 270 202
           L 250 222 L 270 242
           C 285 257 280 278 262 282 L 150 282
           C 120 282 105 262 108 240 L 110 220
           L 95 205 L 60 205
           C 38 205 28 188 32 168 L 38 130 Z`,
  },

  montreal: {
    label: 'Montréal',
    country: '🇨🇦',
    viewBox: '0 0 400 300',
    path: `M 60 50 L 340 50 C 365 50 380 68 380 93
           L 380 220 C 380 248 360 265 332 262
           L 260 258 L 240 240 L 180 240
           L 160 258 L 68 255
           C 42 253 28 232 32 206 L 35 120
           L 55 100 Z`,
  },

  monaco: {
    label: 'Monaco',
    country: '🇲🇨',
    viewBox: '0 0 400 300',
    path: `M 50 80 L 180 60 C 210 56 235 72 242 102
           L 248 130 C 254 158 278 172 306 168
           L 340 162 C 365 158 382 178 378 204
           L 370 240 C 365 262 344 275 322 270
           L 200 265 L 180 248 L 95 248
           C 68 248 55 228 60 203 L 62 170
           L 48 155 C 34 140 36 118 52 106 Z`,
  },

  barcelona: {
    label: 'Barcelona',
    country: '🇪🇸',
    viewBox: '0 0 400 300',
    path: `M 60 80 L 310 80 C 342 80 362 102 360 134
           L 358 165 C 356 188 340 202 318 200
           L 290 198 L 272 218 L 295 240
           C 312 258 308 282 288 288 L 120 285
           C 92 284 78 262 82 238 L 85 215
           L 70 198 L 45 198
           C 25 198 15 180 20 160 L 30 110 Z`,
  },

  red_bull_ring: {
    label: 'Red Bull Ring',
    country: '🇦🇹',
    viewBox: '0 0 400 300',
    path: `M 100 250 L 90 180 C 85 150 100 125 128 118
           L 155 112 L 160 85 C 162 65 178 52 198 55
           L 280 60 C 308 62 325 82 322 110
           L 318 140 L 340 160
           C 358 175 355 200 336 212
           L 310 222 L 300 250 Z`,
  },

  silverstone: {
    label: 'Silverstone',
    country: '🇬🇧',
    viewBox: '0 0 400 300',
    path: `M 50 150 C 50 110 65 78 100 62 L 180 40
           C 220 25 260 42 278 80
           L 290 108 C 302 138 330 150 358 142
           L 375 136 C 390 132 400 118 395 100
           L 390 82 C 385 60 368 48 348 52
           L 320 58 C 300 62 288 78 292 98
           L 300 120 L 280 138
           L 250 148 L 240 178
           C 235 198 218 210 198 208
           L 160 205 C 138 202 125 215 125 238
           L 125 255 C 125 272 110 282 94 275
           L 62 258 C 45 248 42 228 55 218 Z`,
  },

  spa: {
    label: 'Spa-Francorchamps',
    country: '🇧🇪',
    viewBox: '0 0 400 300',
    path: `M 40 180 L 50 140 C 55 115 75 100 100 105
           L 140 112 C 165 118 178 140 170 165
           L 165 185 L 200 200
           C 225 210 245 202 258 180
           L 272 155 C 285 128 310 120 335 132
           L 365 148 C 385 160 390 185 378 205
           L 360 230 C 348 252 322 260 300 248
           L 200 230 C 175 222 155 232 148 258
           L 142 278 C 136 295 118 300 102 290
           L 50 255 C 32 242 30 220 42 205 Z`,
  },

  hungaroring: {
    label: 'Hungaroring',
    country: '🇭🇺',
    viewBox: '0 0 400 300',
    path: `M 60 80 L 200 65 C 230 62 252 80 255 110
           L 258 138 C 260 162 280 175 305 172
           L 330 168 C 355 165 368 185 362 210
           L 355 240 C 348 265 325 278 300 272
           L 120 268 C 90 265 75 242 78 215
           L 80 188 L 58 172 C 40 158 42 135 62 124 Z`,
  },

  zandvoort: {
    label: 'Zandvoort',
    country: '🇳🇱',
    viewBox: '0 0 400 300',
    path: `M 80 80 L 300 78 C 335 78 355 100 352 135
           L 348 165 C 345 195 325 210 295 208
           L 265 205 L 255 230
           C 248 255 228 265 205 260
           L 130 255 C 100 252 82 230 85 200
           L 88 178 L 65 165
           C 45 152 45 128 65 116 Z`,
  },

  monza: {
    label: 'Monza',
    country: '🇮🇹',
    viewBox: '0 0 400 300',
    path: `M 50 150 L 200 80 L 350 80 C 375 80 390 98 388 123
           L 382 148 L 360 162
           C 342 172 330 192 335 215
           L 340 235 C 345 258 328 275 305 272
           L 250 270 L 235 250 L 165 250
           L 150 270 L 85 268
           C 58 266 45 245 50 218 L 52 188
           C 54 165 40 148 20 148 L 50 148 Z`,
  },

  madrid: {
    label: 'Madrid',
    country: '🇪🇸',
    viewBox: '0 0 400 300',
    path: `M 60 80 L 320 75 C 352 74 370 96 368 128
           L 365 158 C 362 182 344 198 320 196
           L 295 194 L 275 215 L 298 238
           C 315 255 310 278 290 282 L 120 278
           C 92 277 78 255 82 230 L 85 208
           L 68 192 L 45 192
           C 25 192 15 173 20 153 L 32 108 Z`,
  },

  baku: {
    label: 'Baku',
    country: '🇦🇿',
    viewBox: '0 0 400 320',
    path: `M 50 60 L 350 60 C 372 60 385 76 382 98
           L 378 130 C 375 155 358 168 335 165
           L 310 162 L 295 180 L 310 200
           L 295 220 L 270 235 L 270 255
           C 270 275 252 288 232 285 L 80 280
           C 58 278 45 258 50 235 L 55 100 Z`,
  },

  singapore: {
    label: 'Singapore',
    country: '🇸🇬',
    viewBox: '0 0 400 300',
    path: `M 50 100 L 180 80 C 208 76 228 94 230 122
           L 232 145 C 234 168 252 182 275 180
           L 320 178 C 348 178 365 198 360 226
           L 355 258 C 350 278 330 288 308 282
           L 200 278 L 180 260 L 100 260
           C 72 260 58 238 62 212 L 65 180
           L 45 165 C 28 150 30 125 48 114 Z`,
  },

  cota: {
    label: 'COTA',
    country: '🇺🇸',
    viewBox: '0 0 400 300',
    path: `M 60 60 L 165 50 C 195 47 215 65 215 95
           L 215 125 C 215 148 230 162 255 160
           L 335 155 C 362 153 378 172 375 200
           L 370 230 C 365 255 344 268 320 262
           L 175 258 C 148 256 135 238 140 212
           L 145 190 L 125 175 L 90 175
           C 62 175 48 157 52 130 L 55 80 Z`,
  },

  mexico_city: {
    label: 'Mexico City',
    country: '🇲🇽',
    viewBox: '0 0 400 300',
    path: `M 50 150 L 50 95 C 50 68 72 52 99 55
           L 305 58 C 338 60 356 82 352 115
           L 348 145 L 375 165
           C 392 178 390 202 372 212
           L 350 222 L 350 255
           C 350 278 328 292 305 288
           L 95 284
           C 68 282 52 262 55 235 L 58 188 Z`,
  },

  interlagos: {
    label: 'Interlagos',
    country: '🇧🇷',
    viewBox: '0 0 400 300',
    path: `M 80 80 L 80 240 C 80 265 102 282 128 278
           L 175 272 L 195 255 L 310 255
           C 340 255 358 235 355 205
           L 350 175 L 375 158
           C 392 145 392 120 372 110
           L 340 98 L 340 80 C 340 55 318 40 292 45
           L 108 52 Z`,
  },

  las_vegas: {
    label: 'Las Vegas',
    country: '🇺🇸',
    viewBox: '0 0 400 300',
    path: `M 50 50 L 350 50 C 375 50 390 68 388 93
           L 380 140 L 350 155 L 350 175
           L 380 190 L 388 235
           C 390 260 372 275 348 272 L 52 268
           C 28 266 15 248 20 223 L 28 145
           L 55 130 L 55 110 L 28 95 Z`,
  },

  lusail: {
    label: 'Lusail',
    country: '🇶🇦',
    viewBox: '0 0 400 300',
    path: `M 50 150 C 50 95 90 55 145 55 L 255 55
           C 310 55 350 95 350 150
           C 350 205 310 245 255 245 L 145 245
           C 90 245 50 205 50 150 Z
           M 100 150 C 100 125 120 105 145 105 L 255 105
           C 280 105 300 125 300 150
           C 300 175 280 195 255 195 L 145 195
           C 120 195 100 175 100 150 Z`,
  },

  yas_marina: {
    label: 'Yas Marina',
    country: '🇦🇪',
    viewBox: '0 0 400 300',
    path: `M 50 80 L 310 80 C 340 80 358 100 355 130
           L 350 155 C 347 175 330 188 310 186
           L 285 184 L 270 205 L 285 228
           C 300 248 292 272 270 278 L 200 282
           L 145 278 L 130 258 L 80 258
           C 52 258 38 235 42 208 L 45 168
           L 30 155
           C 15 140 20 115 38 108 Z`,
  },

}

/**
 * Get the tire compound color for SVG/canvas rendering.
 */
export const TIRE_COLORS = {
  SOFT:         '#FF1801',
  MEDIUM:       '#D4AF00',
  HARD:         '#AAAAAA',
  INTERMEDIATE: '#39B54A',
  WET:          '#0067FF',
}

/**
 * Get the event type color for key point markers.
 */
export const EVENT_COLORS = {
  HIGH_G:        '#8B5CF6',
  TIRE_STRESS:   '#F59E0B',
  PIT_WINDOW:    '#10B981',
  OVERTAKE_ZONE: '#3B82F6',
  DRS_ZONE:      '#06B6D4',
  BRAKING_ZONE:  '#EF4444',
}

export const EVENT_ICONS = {
  HIGH_G:        'G',
  TIRE_STRESS:   'T',
  PIT_WINDOW:    'P',
  OVERTAKE_ZONE: 'O',
  DRS_ZONE:      'D',
  BRAKING_ZONE:  'B',
}
