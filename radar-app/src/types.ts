export type SignalLevel = 'review' | 'watch' | 'normal' | 'unknown'

export interface SignalState {
  a: boolean
  b: boolean
  level: SignalLevel
  label: string
  reason: string
}

export interface FilingEvent {
  symbol?: string
  date: string
  form: string
  title: string
  category: string
  url: string
}

export interface InstrumentSeries {
  dates: string[]
  prices: number[]
  volumes: number[]
  pe: Array<{ date: string; value: number }>
}

export interface Instrument {
  symbol: string
  name: string
  securityType: 'stock' | 'etf' | string
  price: number
  priceDate: string
  sma200: number | null
  distanceToSma200: number | null
  pricePercentile2y: number | null
  ttmEps: number | null
  ttmPe: number | null
  pePercentile2y: number | null
  relativeVolume20d: number | null
  signal: SignalState
  events: FilingEvent[]
  series: InstrumentSeries
  generatedAt: string
}

export interface DataHealth {
  status: 'ok' | 'partial' | 'failed'
  sources: Array<{ name: string; role: string; asOf: string }>
  errors: Array<{ symbol: string; source: string; message: string }>
}

export interface DashboardSnapshot {
  schemaVersion: number
  mode: 'public_safe'
  generatedAt: string
  instruments: Instrument[]
  events: FilingEvent[]
  dataHealth: DataHealth
}

export type RadarFilter = 'all' | 'review' | 'events'
