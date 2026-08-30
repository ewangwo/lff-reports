import { describe, expect, it } from 'vitest'
import { displaySignal, filterInstruments } from './signals'

const instruments = [
  { symbol: 'AAA', signal: { level: 'review', label: '人工复核' }, events: [] },
  { symbol: 'BBB', signal: { level: 'watch', label: '观察' }, events: [{ date: '2026-08-30' }] },
  { symbol: 'CCC', signal: { level: 'normal', label: '正常' }, events: [] },
]

describe('dashboard signal helpers', () => {
  it('maps review level to the approved Chinese label', () => {
    expect(displaySignal('review')).toBe('人工复核')
    expect(displaySignal('unknown')).toBe('数据不足')
  })

  it('filters review and event-risk instruments', () => {
    expect(filterInstruments(instruments, 'review').map((item) => item.symbol)).toEqual(['AAA'])
    expect(filterInstruments(instruments, 'events').map((item) => item.symbol)).toEqual(['BBB'])
    expect(filterInstruments(instruments, 'all')).toHaveLength(3)
  })
})
