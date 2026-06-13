import { useState, useEffect } from 'react';
import { api } from '../api/toeicApi';
import { useSession } from '../context/Sessioncontext';

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

function LineChart({ data }) {
  if (!data.length) return <div className="empty-state">尚無練習紀錄</div>;

  const width = 600;
  const height = 200;
  const padX = 40;
  const padY = 20;
  const maxScore = 100;

  const points = data.map((d, i) => ({
    x: data.length === 1
      ? padX + (width - padX * 2) / 2
      : padX + (i / (data.length - 1)) * (width - padX * 2),
    y: padY + (1 - d.score / maxScore) * (height - padY * 2),
    ...d,
  }));

  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <svg viewBox={`0 0 ${width} ${height + 40}`} style={{ width: '100%', minWidth: 300 }}>
        {/* 格線 */}
        {[0, 25, 50, 75, 100].map(v => {
          const y = padY + (1 - v / maxScore) * (height - padY * 2);
          return (
            <g key={v}>
              <line x1={padX} y1={y} x2={width - padX} y2={y}
                stroke="var(--border)" strokeWidth="1" strokeDasharray="4 4" />
              <text x={padX - 6} y={y + 4} textAnchor="end"
                fontSize="10" fill="var(--text-muted)">{v}</text>
            </g>
          );
        })}

        {/* 折線 */}
        <path d={pathD} fill="none" stroke="var(--accent)" strokeWidth="2.5"
          strokeLinejoin="round" strokeLinecap="round" />

        {/* 填色區域 */}
        <path
          d={`${pathD} L ${points[points.length - 1].x} ${height - padY} L ${points[0].x} ${height - padY} Z`}
          fill="var(--accent)" fillOpacity="0.1"
        />

        {/* 資料點 */}
        {points.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r="5" fill="var(--accent)" stroke="var(--bg)" strokeWidth="2" />
            <text x={p.x} y={p.y - 10} textAnchor="middle"
              fontSize="11" fill="var(--accent)" fontWeight="600">{p.score}</text>
            <text x={p.x} y={height + 10} textAnchor="middle"
              fontSize="10" fill="var(--text-muted)">{p.date}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}

export default function StatsPage() {
  const { computeStats } = useSession();
  const [allQuestions, setAllQuestions] = useState([]);
  const [loadingQ, setLoadingQ] = useState(true);
  const [activeWrong, setActiveWrong] = useState(null);

  // 載入所有題目，供錯題回顧比對用
  useEffect(() => {
    api.getAllQuestionList()
      .then(data => setAllQuestions(data))
      .finally(() => setLoadingQ(false));
  }, []);

  const stats = computeStats(allQuestions);
  const hasData = stats.totalAttempted > 0;
  const overallPct = hasData
    ? Math.round((stats.totalCorrect / stats.totalAttempted) * 100)
    : 0;

  if (loadingQ) return (
    <div className="page-root center">
      <div className="loading-ring" />
      <p className="loading-text">載入統計資料...</p>
    </div>
  );

  return (
    <div className="page-root">
      <div className="page-header">
        <h1 className="page-title">統計分析</h1>
        <p className="page-desc">
          {hasData
            ? `共 ${stats.totalAttempted} 題・${stats.totalCorrect} 題答對`
            : '完成練習後，統計資料將顯示於此'}
        </p>
      </div>

      {!hasData ? (
        <div className="empty-state" style={{ marginTop: '4rem', fontSize: '1rem' }}>
          <p>尚未有任何練習紀錄</p>
          <p style={{ opacity: 0.5, marginTop: '0.5rem' }}>前往練習模式完成至少一次練習</p>
        </div>
      ) : (
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
                if (data.attempted === 0) return null;
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
            <LineChart data={stats.history} />
          </div>

          {/* Wrong Review */}
          {stats.wrongQuestions.length > 0 && (
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
                            {isReading
                              ? (q.passage || q.passages?.[0]?.text || '').slice(0, 300) + '...'
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
          )}
        </div>
      )}
    </div>
  );
}
