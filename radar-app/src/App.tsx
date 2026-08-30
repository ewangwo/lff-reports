import { Bell, Database, RefreshCw, ShieldCheck } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { DataHealth } from './components/DataHealth'
import { DetailPanel } from './components/DetailPanel'
import { EventRail } from './components/EventRail'
import { SignalTable } from './components/SignalTable'
import { loadSnapshot } from './lib/api'
import { filterInstruments } from './lib/signals'
import type { DashboardSnapshot, RadarFilter } from './types'
import './styles.css'

const filters: Array<{ id: RadarFilter; label: string }> = [
  { id: 'all', label: '全部' },
  { id: 'review', label: '核心提醒' },
  { id: 'events', label: '事件风险' },
]

export default function App() {
  const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null)
  const [selectedSymbol, setSelectedSymbol] = useState<string>()
  const [filter, setFilter] = useState<RadarFilter>('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>()

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(undefined)
    try {
      const next = await loadSnapshot(Date.now())
      setSnapshot(next)
      setSelectedSymbol((current) =>
        current && next.instruments.some((item) => item.symbol === current)
          ? current
          : next.instruments[0]?.symbol,
      )
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : '数据刷新失败')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { void refresh() }, [refresh])

  const visible = useMemo(
    () => filterInstruments(snapshot?.instruments ?? [], filter),
    [snapshot, filter],
  )
  const selected = snapshot?.instruments.find((item) => item.symbol === selectedSymbol) ?? null
  const reviews = snapshot?.instruments.filter((item) => item.signal.level === 'review').length ?? 0
  const signalA = snapshot?.instruments.filter((item) => item.signal.a).length ?? 0
  const signalB = snapshot?.instruments.filter((item) => item.signal.b).length ?? 0
  const issues = snapshot?.dataHealth.errors.length ?? 0

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <ShieldCheck aria-hidden="true" />
          <div><h1>持仓估值与风险雷达</h1><span>公开市场研究 · 只读</span></div>
        </div>
        <div className="top-status"><i /><strong>公开数据模式</strong></div>
        <time>{snapshot ? `数据截至 ${new Date(snapshot.generatedAt).toLocaleString('zh-CN')}` : '等待数据'}</time>
        <nav aria-label="主导航">
          <a href="#holdings">持仓</a>
          <a href="#alerts"><Bell size={16} />提醒</a>
          <a href="#data-health"><Database size={16} />数据健康</a>
        </nav>
        <button className="refresh-button" onClick={() => void refresh()} disabled={loading} aria-label="刷新数据">
          <RefreshCw size={17} className={loading ? 'spinning' : ''} />
          刷新
        </button>
      </header>

      {error && <div className="error-banner" role="alert">{error}</div>}

      <section className="summary-strip" aria-label="信号摘要">
        <div><span>覆盖证券</span><strong>{snapshot?.instruments.length ?? '—'}</strong></div>
        <div><span>低于SMA200 · A</span><strong className="blue">{signalA}</strong></div>
        <div><span>双低分位 · B</span><strong className="amber">{signalB}</strong></div>
        <div><span>人工复核 · C</span><strong className="red">{reviews}</strong></div>
        <div><span>数据异常</span><strong className={issues ? 'amber' : ''}>{issues}</strong></div>
      </section>

      <section className="workspace" id="holdings">
        <div className="table-panel">
          <div className="table-toolbar" id="alerts">
            <div className="filter-group" aria-label="筛选">
              <span>筛选：</span>
              {filters.map((item) => (
                <button key={item.id} className={filter === item.id ? 'active' : ''} onClick={() => setFilter(item.id)}>
                  {item.label}
                </button>
              ))}
            </div>
            <span>显示 {visible.length} / {snapshot?.instruments.length ?? 0}</span>
          </div>
          <SignalTable instruments={visible} selectedSymbol={selectedSymbol} onSelect={setSelectedSymbol} />
          <p className="table-note">A：低于200日均线。B：价格与TTM PE均处于两年10%分位以下。C：A与B同时成立，仅触发人工复核。</p>
        </div>
        <EventRail events={snapshot?.events ?? []} />
      </section>

      <DetailPanel instrument={selected} />
      {snapshot && <DataHealth health={snapshot.dataHealth} />}

      <footer>
        <span>数据用于研究与风险提示，不构成交易建议。</span>
        <span>网页刷新会请求最新公开快照；更新时间受上游数据源和GitHub Actions频率限制。</span>
      </footer>
    </main>
  )
}
