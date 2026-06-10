import { useState, useEffect } from 'react';
import { toeicPool } from '../data/toeic_pool';
import { api } from '../api/toeicApi';

const TYPE_LABELS = {
  cloze: '克漏字',
  reading_single: '閱讀・單篇',
  reading_multi: '閱讀・多篇',
};

const CAT_LABELS = {
  grammar: '文法',
  vocabulary: '字彙',
  reading: '閱讀',
};

function QuestionRow({ q, onSelect, selected }) {
  const isReading = q.type !== 'cloze';
  const preview = isReading
    ? (q.passage || q.passages?.[0]?.text || '').slice(0, 60)
    : q.passage?.slice(0, 60);

  return (
    <div className={`q-row ${selected ? 'selected' : ''}`} onClick={() => onSelect(q)}>
      <div className="q-row-left">
        <span className="q-id-badge">{q.id}</span>
        <div className="q-row-info">
          <p className="q-preview">{preview}…</p>
          <div className="q-row-tags">
            <span className={`q-tag ${q.category}`}>{CAT_LABELS[q.category]}</span>
            <span className="q-tag type">{TYPE_LABELS[q.type]}</span>
            {q.difficulty && <span className={`q-diff ${q.difficulty}`}>{q.difficulty}</span>}
            {isReading && <span className="q-sub-count">{q.questions?.length} 題</span>}
          </div>
        </div>
      </div>
      <span className="q-row-arrow">{selected ? '▶' : '›'}</span>
    </div>
  );
}

function QuestionDetail({ q }) {
  if (!q) return (
    <div className="detail-empty">
      <span className="detail-empty-icon">⊡</span>
      <p>選擇左側題目查看詳情</p>
    </div>
  );

  const isReading = q.type !== 'cloze';

  return (
    <div className="detail-panel">
      <div className="detail-header">
        <span className="q-id-badge large">{q.id}</span>
        <div className="detail-tags">
          <span className={`q-tag ${q.category}`}>{CAT_LABELS[q.category]}</span>
          <span className="q-tag type">{TYPE_LABELS[q.type]}</span>
          {q.difficulty && <span className={`q-diff ${q.difficulty}`}>{q.difficulty}</span>}
        </div>
      </div>

      {!isReading ? (
        <>
          <div className="detail-section">
            <label>題目</label>
            <p className="detail-passage">{q.passage}</p>
          </div>
          <div className="detail-section">
            <label>選項</label>
            <div className="options-grid compact-display">
              {Object.entries(q.options).map(([k, v]) => (
                <div key={k} className={`option-display ${k === q.answer ? 'correct' : ''}`}>
                  <span className="opt-key">{k}</span>
                  <span>{v}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="detail-section">
            <label>解析</label>
            <p className="detail-explanation">{q.explanation}</p>
          </div>
          {q.tags?.length > 0 && (
            <div className="detail-section">
              <label>標籤</label>
              <div className="tags-row">
                {q.tags.map(t => <span key={t} className="tag-chip">{t}</span>)}
              </div>
            </div>
          )}
        </>
      ) : (
        <>
          {(q.passages || [{ text: q.passage }]).map((p, i) => (
            <div key={i} className="detail-section">
              <label>{q.passages ? p.label : '文章'}</label>
              <p className="detail-passage">{p.text}</p>
            </div>
          ))}
          <div className="detail-section">
            <label>題目 ({q.questions.length} 題)</label>
            {q.questions.map((sub, i) => (
              <div key={sub.id} className="sub-q-display">
                <p className="sub-stem-display">Q{i + 1}. {sub.stem}</p>
                <div className="options-grid compact-display">
                  {Object.entries(sub.options).map(([k, v]) => (
                    <div key={k} className={`option-display ${k === sub.answer ? 'correct' : ''}`}>
                      <span className="opt-key">{k}</span>
                      <span>{v}</span>
                    </div>
                  ))}
                </div>
                <p className="detail-explanation small">{sub.explanation}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function AddQuestionForm({ onClose, onSuccess }) {
  const [type, setType] = useState('cloze');
  const [form, setForm] = useState({
    category: 'grammar',
    difficulty: 'medium',
    passage: '',
    optA: '', optB: '', optC: '', optD: '',
    answer: 'A',
    explanation: '',
    tags: '',
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSubmit = async () => {
    setSaving(true);
    const payload = type === 'cloze' ? {
      type: 'cloze',
      category: form.category,
      difficulty: form.difficulty,
      passage: form.passage,
      options: { A: form.optA, B: form.optB, C: form.optC, D: form.optD },
      answer: form.answer,
      explanation: form.explanation,
      tags: form.tags.split(',').map(t => t.trim()).filter(Boolean),
    } : {
      type: 'reading_single',
      category: 'reading',
      difficulty: form.difficulty,
      passage: form.passage,
    };
    await api.createQuestion(payload);
    setSaving(false);
    setSaved(true);
    setTimeout(() => { setSaved(false); onSuccess?.(); }, 1200);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>新增題目</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="form-body">
          <div className="form-row">
            <label>題型</label>
            <div className="toggle-group">
              {['cloze', 'reading_single', 'reading_multi'].map(t => (
                <button key={t} className={`toggle-btn ${type === t ? 'active' : ''}`} onClick={() => setType(t)}>
                  {TYPE_LABELS[t]}
                </button>
              ))}
            </div>
          </div>
          <div className="form-row two-col">
            <div>
              <label>分類</label>
              <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}>
                <option value="grammar">文法</option>
                <option value="vocabulary">字彙</option>
                <option value="reading">閱讀</option>
              </select>
            </div>
            <div>
              <label>難度</label>
              <select value={form.difficulty} onChange={e => setForm(f => ({ ...f, difficulty: e.target.value }))}>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
          </div>
          <div className="form-row">
            <label>{type === 'cloze' ? '題目（用 ______ 表示空格）' : '文章內容'}</label>
            <textarea
              rows={4}
              placeholder={type === 'cloze' ? 'The manager ______ the report before the meeting.' : '貼上文章內容...'}
              value={form.passage}
              onChange={e => setForm(f => ({ ...f, passage: e.target.value }))}
            />
          </div>
          {type === 'cloze' && (
            <>
              <div className="form-row">
                <label>選項</label>
                <div className="options-input-grid">
                  {['A', 'B', 'C', 'D'].map(k => (
                    <div key={k} className="opt-input-row">
                      <span className="opt-key">{k}</span>
                      <input
                        placeholder={`選項 ${k}`}
                        value={form[`opt${k}`]}
                        onChange={e => setForm(f => ({ ...f, [`opt${k}`]: e.target.value }))}
                      />
                    </div>
                  ))}
                </div>
              </div>
              <div className="form-row two-col">
                <div>
                  <label>正確答案</label>
                  <select value={form.answer} onChange={e => setForm(f => ({ ...f, answer: e.target.value }))}>
                    {['A', 'B', 'C', 'D'].map(k => <option key={k} value={k}>{k}</option>)}
                  </select>
                </div>
                <div>
                  <label>標籤（逗號分隔）</label>
                  <input placeholder="passive voice, grammar" value={form.tags}
                    onChange={e => setForm(f => ({ ...f, tags: e.target.value }))} />
                </div>
              </div>
              <div className="form-row">
                <label>解析</label>
                <textarea rows={2} placeholder="解題說明..." value={form.explanation}
                  onChange={e => setForm(f => ({ ...f, explanation: e.target.value }))} />
              </div>
            </>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn-ghost" onClick={onClose}>取消</button>
          <button className="btn-primary" onClick={handleSubmit} disabled={saving || saved}>
            {saved ? '✓ 已儲存' : saving ? '儲存中...' : '新增題目'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function QuestionManagerPage() {
  const [filter, setFilter] = useState('all');
  const [selected, setSelected] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [search, setSearch] = useState('');

  const allQuestions = [
    ...toeicPool.cloze,
    ...toeicPool.reading,
  ];

  const filtered = allQuestions.filter(q => {
    const matchType = filter === 'all' || q.type === filter ||
      (filter === 'reading' && q.type.startsWith('reading'));
    const matchSearch = !search || q.id.includes(search.toUpperCase()) ||
      (q.passage || q.passages?.[0]?.text || '').toLowerCase().includes(search.toLowerCase());
    return matchType && matchSearch;
  });

  return (
    <div className="page-root manager-layout">
      <div className="manager-sidebar">
        <div className="manager-toolbar">
          <h1 className="page-title small">題庫管理</h1>
          <button className="btn-primary small" onClick={() => setShowAdd(true)}>＋ 新增</button>
        </div>
        <input
          className="search-input"
          placeholder="搜尋 ID 或關鍵字..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <div className="filter-tabs">
          {[
            { id: 'all', label: `全部 (${allQuestions.length})` },
            { id: 'cloze', label: `克漏字 (${toeicPool.cloze.length})` },
            { id: 'reading', label: `閱讀 (${toeicPool.reading.length})` },
          ].map(f => (
            <button key={f.id} className={`filter-tab ${filter === f.id ? 'active' : ''}`}
              onClick={() => setFilter(f.id)}>
              {f.label}
            </button>
          ))}
        </div>
        <div className="q-list">
          {filtered.map(q => (
            <QuestionRow key={q.id} q={q} selected={selected?.id === q.id}
              onSelect={setSelected} />
          ))}
          {filtered.length === 0 && (
            <div className="empty-state">找不到符合的題目</div>
          )}
        </div>
      </div>
      <div className="manager-detail">
        <QuestionDetail q={selected} />
      </div>
      {showAdd && <AddQuestionForm onClose={() => setShowAdd(false)} onSuccess={() => setShowAdd(false)} />}
    </div>
  );
}
