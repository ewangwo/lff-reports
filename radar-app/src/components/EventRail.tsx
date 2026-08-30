import { ExternalLink } from 'lucide-react'
import type { FilingEvent } from '../types'

export function EventRail({ events }: { events: FilingEvent[] }) {
  return (
    <aside className="event-rail" aria-label="重大变化">
      <div className="section-heading">
        <h2>最新重大变化</h2>
        <span>{events.length} 条</span>
      </div>
      <div className="event-list">
        {events.slice(0, 8).map((event, index) => (
          <a className="event-item" href={event.url} target="_blank" rel="noreferrer" key={`${event.symbol}-${event.date}-${index}`}>
            <div className="event-meta">
              <span>{event.symbol} · {event.category}</span>
              <time>{event.date}</time>
            </div>
            <strong>{event.form}</strong>
            <p>{event.title || '查看SEC原始文件'}</p>
            <ExternalLink size={14} aria-hidden="true" />
          </a>
        ))}
        {events.length === 0 && <p className="empty-copy">当前快照没有重大事件。</p>}
      </div>
    </aside>
  )
}
