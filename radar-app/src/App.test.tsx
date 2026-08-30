import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import * as api from './lib/api'
import type { DashboardSnapshot } from './types'

vi.mock('./lib/api')

const snapshot: DashboardSnapshot = {
  schemaVersion: 1,
  mode: 'public_safe',
  generatedAt: '2026-08-30T08:00:00+00:00',
  instruments: [
    {
      symbol: 'AAA', name: 'Alpha', securityType: 'stock', price: 80, priceDate: '2026-08-29',
      sma200: 100, distanceToSma200: -0.2, pricePercentile2y: 8, ttmEps: 4,
      ttmPe: 20, pePercentile2y: 7, relativeVolume20d: 1.5,
      signal: { a: true, b: true, level: 'review', label: '人工复核', reason: '组合条件成立' },
      events: [], series: { dates: ['2026-08-29'], prices: [80], volumes: [100], pe: [] },
      generatedAt: '2026-08-30T08:00:00+00:00',
    },
    {
      symbol: 'BBB', name: 'Beta', securityType: 'stock', price: 120, priceDate: '2026-08-29',
      sma200: 110, distanceToSma200: 0.09, pricePercentile2y: 60, ttmEps: 6,
      ttmPe: 20, pePercentile2y: 50, relativeVolume20d: 0.9,
      signal: { a: false, b: false, level: 'normal', label: '正常', reason: '未触发' },
      events: [], series: { dates: ['2026-08-29'], prices: [120], volumes: [100], pe: [] },
      generatedAt: '2026-08-30T08:00:00+00:00',
    },
  ],
  events: [],
  dataHealth: { status: 'ok', sources: [], errors: [] },
}

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(api.loadSnapshot).mockResolvedValue(snapshot)
  })

  it('renders the latest public-safe snapshot and filters core reviews', async () => {
    render(<App />)

    expect((await screen.findAllByText('Alpha')).length).toBeGreaterThan(0)
    fireEvent.click(screen.getByRole('button', { name: '核心提醒' }))

    expect(screen.getAllByText('Alpha').length).toBeGreaterThan(0)
    expect(screen.queryByText('Beta')).not.toBeInTheDocument()
    expect(screen.getByText('公开数据模式')).toBeInTheDocument()
  })

  it('selects a row and refreshes the snapshot', async () => {
    render(<App />)
    await screen.findAllByText('Alpha')

    fireEvent.click(screen.getByText('Beta'))
    expect(screen.getByRole('heading', { name: 'BBB' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '刷新数据' }))
    await waitFor(() => expect(api.loadSnapshot).toHaveBeenCalledTimes(2))
  })
})
