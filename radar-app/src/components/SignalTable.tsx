import type { Instrument } from '../types'

interface SignalTableProps {
  instruments: Instrument[]
  selectedSymbol?: string
  onSelect: (symbol: string) => void
}

const fmt = (value: number | null, digits = 1) =>
  value == null ? 'N/M' : value.toFixed(digits)

const pct = (value: number | null, ratio = false) =>
  value == null ? 'N/M' : `${(ratio ? value * 100 : value).toFixed(1)}%`

export function SignalTable({ instruments, selectedSymbol, onSelect }: SignalTableProps) {
  return (
    <div className="table-scroll">
      <table className="signal-table">
        <thead>
          <tr>
            <th>股票</th>
            <th>现价</th>
            <th>200日均线</th>
            <th>距离均线</th>
            <th>两年价格分位</th>
            <th>TTM PE</th>
            <th>两年PE分位</th>
            <th>相对成交量</th>
            <th>A / B</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          {instruments.map((instrument) => (
            <tr
              key={instrument.symbol}
              className={instrument.symbol === selectedSymbol ? 'selected-row' : undefined}
              onClick={() => onSelect(instrument.symbol)}
              tabIndex={0}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') onSelect(instrument.symbol)
              }}
            >
              <td>
                <strong>{instrument.symbol}</strong>
                <span>{instrument.name}</span>
              </td>
              <td>${fmt(instrument.price, 2)}</td>
              <td>{instrument.sma200 == null ? 'N/M' : `$${fmt(instrument.sma200, 2)}`}</td>
              <td className={(instrument.distanceToSma200 ?? 0) < 0 ? 'negative' : 'positive'}>
                {pct(instrument.distanceToSma200, true)}
              </td>
              <td>{pct(instrument.pricePercentile2y)}</td>
              <td>{fmt(instrument.ttmPe)}</td>
              <td>{pct(instrument.pePercentile2y)}</td>
              <td>{instrument.relativeVolume20d == null ? 'N/M' : `${fmt(instrument.relativeVolume20d, 2)}x`}</td>
              <td>
                <span className={instrument.signal.a ? 'condition on' : 'condition'}>A</span>
                <span className={instrument.signal.b ? 'condition on' : 'condition'}>B</span>
              </td>
              <td><span className={`status status-${instrument.signal.level}`}>{instrument.signal.label}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
      {instruments.length === 0 && <div className="empty-state">当前筛选条件下没有证券</div>}
    </div>
  )
}
