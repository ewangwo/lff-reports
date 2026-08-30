import type { DashboardSnapshot } from '../types'

const SNAPSHOT_URL = '/lff-reports/data/ibkr-radar/public-snapshot.json'

export async function loadSnapshot(now = Date.now()): Promise<DashboardSnapshot> {
  const response = await fetch(`${SNAPSHOT_URL}?_=${now}`, {
    cache: 'no-store',
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    throw new Error(`数据快照暂时不可用（${response.status}）`)
  }
  return response.json() as Promise<DashboardSnapshot>
}
