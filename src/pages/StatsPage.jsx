import { useState, useEffect } from 'react';
import { api } from '../api/toeicApi';

const TYPE_LABELS = { grammar: '文法', vocabulary: '字彙', reading: '閱讀' };

function RadialProgress({ pct, label, size = 100 }) {
  const r = 38;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <div className="radial-wrap" style={{ width: size, height: size }}>
      <svg viewBox="0 0 100 100" width={size} height={size}>
        <circle cx="50" cy="50" r={r} fill="none" stroke="var(--border)" strokeWidth="8" />
        <circle
          cx="50" cy="50" r={r} fill="none"
          stroke={pct >= 80 ? 'var(--accent-green)' : pct >= 60 ? 'var(--accent)' : 'var(--accent-red)'}
          strokeWidth="8"
          strokeDasharray={`${dash} ${circ - dash}`}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          style={{ transition: 'stroke-dasharray 1s ease' }}
        />
      </svg>
      <div className="radial-center">
        <span className="radial-pct">{pct}%</span>
        <span className="radial-label">{label}</span>
      </div>
    </div>
  );
}

function BarChart({ data }) {
  const max = Math.max(...data.map(d => d.score));
  return (
    <div className="bar-chart">
      {data.map((d, i) => {
        const pct = (d.score / 100) * 100;
        return (
          <div key={i} className="bar-item">
            <div className="bar-track">
              <div className="bar-fill" style={{ height: `${pct}%`, '--delay': `${i * 0.1}s` }} />
            </div>
            <div className="bar-val">{d.score}</div>
            <div className="bar-date">{d.date}</div>
          </div>
        );
      })}
    </div>
  );
}

export default function StatsPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeWrong, setActiveWrong] = useState(null);

  useEffect(() => {
    api.getStats().then(s => { setStats(s); setLoading(false); });
  }, []);

  if (loading) return (
    <div className="page-root center">
      <div className="loading-ring" />
      <p className="loading-text">載入統計資料...</p>
    </div>
  );

  const overallPct = Math.round((stats.totalCorrect / stats.totalAttempted) * 100);

  return (
    <div className="page-root">
      <div className="page-header">
        <h1 className="page-title">統計分析</h1>
        <p className="page-desc">共 {stats.totalAttempted} 題・{stats.totalCorrect} 題答對</p>
      </div>

      <div className="stats-grid">
        {/* Overall */}
        <div className="stat-card large">
          <div className="stat-card-header">整體正確率</div>
          <div className="stat-card-body center-col">
            <RadialProgress pct={overallPct} label="正確率" size={140} />
            <div className="stat-sub-row">
              <div className="stat-sub">
                <span className="stat-num green">{stats.totalCorrect}</span>
                <span className="stat-sub-label">答對</span>
              </div>
              <div className="stat-divider" />
              <div className="stat-sub">
                <span className="stat-num red">{stats.totalAttempted - stats.totalCorrect}</span>
                <span className="stat-sub-label">答錯</span>
              </div>
              <div className="stat-divider" />
              <div className="stat-sub">
                <span className="stat-num">{stats.totalAttempted}</span>
                <span className="stat-sub-label">總題數</span>
              </div>
            </div>
          </div>
        </div>

        {/* By Type */}
        <div className="stat-card">
          <div className="stat-card-header">各題型表現</div>
          <div className="type-breakdown">
            {Object.entries(stats.byType).map(([type, data]) => {
              const pct = Math.round((data.correct / data.attempted) * 100);
              return (
                <div key={type} className="type-row">
                  <span className={`q-tag ${type}`}>{TYPE_LABELS[type]}</span>
                  <div className="type-bar-track">
                    <div className="type-bar-fill" style={{ width: `${pct}%`, '--pct': pct }} />
                  </div>
                  <span className="type-pct">{pct}%</span>
                  <span className="type-count">{data.correct}/{data.attempted}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* History */}
        <div className="stat-card wide">
          <div className="stat-card-header">歷次成績趨勢</div>
          <BarChart data={stats.history} />
        </div>

        {/* Wrong Review */}
        <div className="stat-card wide">
          <div className="stat-card-header">錯題回顧</div>
          <div className="wrong-list">
            {stats.wrongQuestions.map(q => {
              const isOpen = activeWrong === q.id;
              const isReading = q.type !== 'cloze';
              return (
                <div key={q.id} className="wrong-item">
                  <div className="wrong-item-header" onClick={() => setActiveWrong(isOpen ? null : q.id)}>
                    <div className="wrong-meta">
                      <span className="q-id-badge">{q.id}</span>
                      <span className={`q-tag ${q.category}`}>
                        {q.category === 'grammar' ? '文法' : q.category === 'vocabulary' ? '字彙' : '閱讀'}
                      </span>
                      {q.difficulty && <span className={`q-diff ${q.difficulty}`}>{q.difficulty}</span>}
                    </div>
                    <span className={`expand-icon ${isOpen ? 'open' : ''}`}>▾</span>
                  </div>
                  {isOpen && (
                    <div className="wrong-detail">
                      <p className="detail-passage">
                        {isReading ? (q.passage || q.passages?.[0]?.text || '').slice(0, 300) + '...'
                          : q.passage}
                      </p>
                      {!isReading && (
                        <>
                          <div className="options-grid compact-display">
                            {Object.entries(q.options).map(([k, v]) => (
                              <div key={k} className={`option-display ${k === q.answer ? 'correct' : ''}`}>
                                <span className="opt-key">{k}</span><span>{v}</span>
                              </div>
                            ))}
                          </div>
                          <div className="explanation-box small">
                            <span className="exp-label">解析</span>
                            <p>{q.explanation}</p>
                          </div>
                        </>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
