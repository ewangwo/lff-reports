import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Instrument } from '../types'

const metric = (value: number | null, suffix = '') =>
  value == null ? 'N/M' : `${value.toFixed(1)}${suffix}`

export function DetailPanel({ instrument }: { instrument: Instrument | null }) {
  if (!instrument) return <section className="detail-panel empty-state">请选择一只证券查看详情</section>

  const chartData = instrument.series.dates.map((date, index) => ({
    date,
    price: instrument.series.prices[index],
    sma200: instrument.sma200,
  }))
  return (
    <section className="detail-panel">
      <div className="detail-summary">
        <div>
          <h2>{instrument.symbol}</h2>
          <p>{instrument.name}</p>
        </div>
        <strong>${instrument.price.toFixed(2)}</strong>
        <dl>
          <div><dt>价格分位</dt><dd>{metric(instrument.pricePercentile2y, '%')}</dd></div>
          <div><dt>TTM PE</dt><dd>{metric(instrument.ttmPe)}</dd></div>
          <div><dt>PE分位</dt><dd>{metric(instrument.pePercentile2y, '%')}</dd></div>
          <div><dt>相对成交量</dt><dd>{metric(instrument.relativeVolume20d, 'x')}</dd></div>
        </dl>
        <p className={`detail-reason status-${instrument.signal.level}`}>{instrument.signal.reason}</p>
      </div>
      <div className="chart-wrap" aria-label={`${instrument.symbol} 两年价格走势`}>
        <div className="chart-title">
          <strong>两年价格趋势</strong>
          <span>调整收盘价 · SMA200</span>
        </div>
        <ResponsiveContainer width="100%" height={245}>
          <LineChart data={chartData} margin={{ top: 12, right: 18, left: -12, bottom: 0 }}>
            <CartesianGrid stroke="#263849" vertical={false} />
            <XAxis dataKey="date" tick={{ fill: '#8396a8', fontSize: 11 }} minTickGap={55} />
            <YAxis tick={{ fill: '#8396a8', fontSize: 11 }} domain={['auto', 'auto']} />
            <Tooltip contentStyle={{ background: '#101d29', border: '1px solid #2c4052', borderRadius: 8 }} />
            <Line type="monotone" dataKey="price" stroke="#4f9cff" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="sma200" stroke="#f0b447" strokeWidth={1.5} strokeDasharray="5 4" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
