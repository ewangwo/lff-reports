import type { RadarFilter, SignalLevel } from '../types'

const LABELS: Record<SignalLevel, string> = {
  review: '人工复核',
  watch: '观察',
  normal: '正常',
  unknown: '数据不足',
}

export function displaySignal(level: SignalLevel | string): string {
  return LABELS[level as SignalLevel] ?? '数据不足'
}

export function filterInstruments<T extends { symbol: string; signal: { level: string }; events: unknown[] }>(
  instruments: T[],
  filter: RadarFilter,
): T[] {
  if (filter === 'review') {
    return instruments.filter((instrument) => instrument.signal.level === 'review')
  }
  if (filter === 'events') {
    return instruments.filter((instrument) => instrument.events.length > 0)
  }
  return instruments
}
