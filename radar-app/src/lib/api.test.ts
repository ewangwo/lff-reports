import { afterEach, describe, expect, it, vi } from 'vitest'
import { loadSnapshot } from './api'

describe('snapshot loader', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('bypasses browser cache on every refresh', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ schemaVersion: 1, instruments: [] }),
    })
    vi.stubGlobal('fetch', fetchMock)

    await loadSnapshot(12345)

    expect(fetchMock).toHaveBeenCalledOnce()
    const [url, options] = fetchMock.mock.calls[0]
    expect(String(url)).toContain('_=12345')
    expect(options).toMatchObject({ cache: 'no-store' })
  })

  it('throws a readable error for an unavailable snapshot', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }))

    await expect(loadSnapshot(1)).rejects.toThrow('数据快照暂时不可用（503）')
  })
})
