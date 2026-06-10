import { useState, useEffect } from 'react';
import { api } from '../api/toeicApi';

const MODES = [
  { id: 'cloze', label: '克漏字練習', sub: '文法・字彙單選題', icon: '✦' },
  { id: 'reading', label: '閱讀理解練習', sub: '單篇 & 多篇文章題', icon: '❋' },
];

function ClozeCard({ question, index, total, onAnswer, userAnswer, showResult }) {
  const passage = question.passage;

  return (
    <div className="question-card">
      <div className="q-meta">
        <span className="q-index">{index + 1} / {total}</span>
        <span className={`q-tag ${question.category}`}>{question.category === 'grammar' ? '文法' : '字彙'}</span>
        <span className={`q-diff ${question.difficulty}`}>{question.difficulty}</span>
      </div>
      <div className="q-passage">
        {passage.split('______').map((part, i, arr) => (
          <span key={i}>
            {part}
            {i < arr.length - 1 && (
              <span className={`blank-highlight ${showResult ? (userAnswer === question.answer ? 'correct' : 'wrong') : userAnswer ? 'filled' : ''}`}>
                {userAnswer ? question.options[userAnswer] : '_________'}
              </span>
            )}
          </span>
        ))}
      </div>
      <div className="options-grid">
        {Object.entries(question.options).map(([key, val]) => {
          let cls = 'option-btn';
          if (showResult) {
            if (key === question.answer) cls += ' correct';
            else if (key === userAnswer && userAnswer !== question.answer) cls += ' wrong';
          } else if (key === userAnswer) {
            cls += ' selected';
          }
          return (
            <button key={key} className={cls} onClick={() => !showResult && onAnswer(key)}>
              <span className="opt-key">{key}</span>
              <span className="opt-val">{val}</span>
            </button>
          );
        })}
      </div>
      {showResult && (
        <div className="explanation-box">
          <span className="exp-label">解析</span>
          <p>{question.explanation}</p>
        </div>
      )}
    </div>
  );
}

function ReadingCard({ question, index, total, onAnswers, userAnswers, showResult }) {
  const isMulti = question.type === 'reading_multi';
  const passages = isMulti ? question.passages : [{ label: '文章', text: question.passage }];

  return (
    <div className="question-card reading-card">
      <div className="q-meta">
        <span className="q-index">{index + 1} / {total}</span>
        <span className={`q-tag reading`}>閱讀</span>
        <span className={`q-tag ${isMulti ? 'multi' : 'single'}`}>{isMulti ? '多篇' : '單篇'}</span>
        <span className={`q-diff ${question.difficulty}`}>{question.difficulty}</span>
      </div>
      <div className="reading-layout">
        <div className="passage-panel">
          {passages.map((p, i) => (
            <div key={i} className="passage-block">
              {isMulti && <div className="passage-label">{p.label}</div>}
              <p className="passage-text">{p.text}</p>
            </div>
          ))}
        </div>
        <div className="questions-panel">
          {question.questions.map((q, qi) => (
            <div key={q.id} className="sub-question">
              <p className="sub-stem"><span className="sub-num">Q{qi + 1}</span>{q.stem}</p>
              <div className="sub-options">
                {Object.entries(q.options).map(([key, val]) => {
                  const ans = userAnswers[q.id];
                  let cls = 'option-btn compact';
                  if (showResult) {
                    if (key === q.answer) cls += ' correct';
                    else if (key === ans && ans !== q.answer) cls += ' wrong';
                  } else if (key === ans) cls += ' selected';
                  return (
                    <button key={key} className={cls}
                      onClick={() => !showResult && onAnswers(q.id, key)}>
                      <span className="opt-key">{key}</span>
                      <span className="opt-val">{val}</span>
                    </button>
                  );
                })}
              </div>
              {showResult && (
                <div className="explanation-box small">
                  <span className="exp-label">解析</span>
                  <p>{q.explanation}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function PracticePage() {
  const [mode, setMode] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [showResult, setShowResult] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sessionDone, setSessionDone] = useState(false);

  const startSession = async (m) => {
    setLoading(true);
    setMode(m);
    setCurrentIdx(0);
    setUserAnswers({});
    setShowResult(false);
    setSessionDone(false);
    const data = m === 'cloze'
      ? await api.getClozeQuestions(6)
      : await api.getReadingQuestions('all');
    setQuestions(data);
    setLoading(false);
  };

  const currentQ = questions[currentIdx];

  const handleClozeAnswer = (key) => {
    setUserAnswers(prev => ({ ...prev, [currentQ.id]: key }));
    setTimeout(() => setShowResult(true), 150);
  };

  const handleReadingAnswer = (qid, key) => {
    setUserAnswers(prev => ({ ...prev, [qid]: key }));
  };

  const handleCheckReading = () => setShowResult(true);

  const handleNext = () => {
    if (currentIdx + 1 >= questions.length) {
      setSessionDone(true);
    } else {
      setCurrentIdx(i => i + 1);
      setShowResult(false);
    }
  };

  const calcScore = () => {
    if (!questions.length) return { correct: 0, total: 0 };
    let correct = 0, total = 0;
    questions.forEach(q => {
      if (q.type === 'cloze') {
        total++;
        if (userAnswers[q.id] === q.answer) correct++;
      } else {
        q.questions.forEach(sub => {
          total++;
          if (userAnswers[sub.id] === sub.answer) correct++;
        });
      }
    });
    return { correct, total };
  };

  if (!mode) {
    return (
      <div className="page-root">
        <div className="page-header">
          <h1 className="page-title">練習模式</h1>
          <p className="page-desc">選擇題型開始本次練習</p>
        </div>
        <div className="mode-grid">
          {MODES.map(m => (
            <button key={m.id} className="mode-card" onClick={() => startSession(m.id)}>
              <span className="mode-icon">{m.icon}</span>
              <span className="mode-label">{m.label}</span>
              <span className="mode-sub">{m.sub}</span>
              <span className="mode-arrow">→</span>
            </button>
          ))}
        </div>
      </div>
    );
  }

  if (loading) return (
    <div className="page-root center">
      <div className="loading-ring" />
      <p className="loading-text">載入題目中...</p>
    </div>
  );

  if (sessionDone) {
    const { correct, total } = calcScore();
    const pct = Math.round((correct / total) * 100);
    return (
      <div className="page-root center">
        <div className="result-card">
          <div className="result-score" style={{ '--pct': pct }}>{pct}<span>%</span></div>
          <p className="result-label">{correct} / {total} 題答對</p>
          <p className="result-comment">{pct >= 80 ? '🎉 表現優秀！' : pct >= 60 ? '👍 繼續加油！' : '📖 建議多加練習'}</p>
          <div className="result-actions">
            <button className="btn-primary" onClick={() => startSession(mode)}>再練一次</button>
            <button className="btn-ghost" onClick={() => setMode(null)}>選擇題型</button>
          </div>
        </div>
      </div>
    );
  }

  if (!currentQ) return null;

  const allReadingAnswered = mode === 'reading' && currentQ.questions &&
    currentQ.questions.every(q => userAnswers[q.id]);

  return (
    <div className="page-root">
      <div className="practice-header">
        <button className="btn-ghost small" onClick={() => setMode(null)}>← 返回</button>
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${((currentIdx) / questions.length) * 100}%` }} />
        </div>
        <span className="progress-label">{currentIdx + 1}/{questions.length}</span>
      </div>

      {mode === 'cloze' ? (
        <ClozeCard
          question={currentQ}
          index={currentIdx}
          total={questions.length}
          onAnswer={handleClozeAnswer}
          userAnswer={userAnswers[currentQ.id]}
          showResult={showResult}
        />
      ) : (
        <ReadingCard
          question={currentQ}
          index={currentIdx}
          total={questions.length}
          onAnswers={handleReadingAnswer}
          userAnswers={userAnswers}
          showResult={showResult}
        />
      )}

      <div className="action-row">
        {mode === 'reading' && !showResult && (
          <button className="btn-primary" disabled={!allReadingAnswered} onClick={handleCheckReading}>
            確認作答
          </button>
        )}
        {showResult && (
          <button className="btn-primary" onClick={handleNext}>
            {currentIdx + 1 >= questions.length ? '查看成績' : '下一題 →'}
          </button>
        )}
      </div>
    </div>
  );
}
