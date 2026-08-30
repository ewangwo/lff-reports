import { Database, ShieldCheck, TriangleAlert } from 'lucide-react'
import type { DataHealth as DataHealthType } from '../types'

export function DataHealth({ health }: { health: DataHealthType }) {
  return (
    <section className="health-panel" id="data-health">
      <div className="section-heading">
        <h2>数据健康</h2>
        <span className={`health-state health-${health.status}`}>
          {health.status === 'ok' ? <ShieldCheck size={15} /> : <TriangleAlert size={15} />}
          {health.status === 'ok' ? '正常' : health.status === 'partial' ? '部分缺失' : '不可用'}
        </span>
      </div>
      <div className="source-grid">
        {health.sources.map((source) => (
          <div className="source-item" key={source.name}>
            <Database size={16} aria-hidden="true" />
            <div><strong>{source.name}</strong><span>{source.role}</span></div>
            <time>{new Date(source.asOf).toLocaleString('zh-CN')}</time>
          </div>
        ))}
      </div>
      {health.errors.length > 0 && (
        <ul className="error-list">
          {health.errors.map((error) => <li key={`${error.symbol}-${error.message}`}>{error.symbol}：{error.message}</li>)}
        </ul>
      )}
    </section>
  )
}
