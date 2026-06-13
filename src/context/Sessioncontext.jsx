import { createContext, useContext, useState, useCallback } from 'react';

const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [sessions, setSessions] = useState([]);

  // 每次練習完成後呼叫，傳入該次練習的結果
  const addSession = useCallback((sessionData) => {
    setSessions(prev => [...prev, {
      ...sessionData,
      timestamp: new Date(),
    }]);
  }, []);

  const clearSessions = useCallback(() => setSessions([]), []);

  // 計算統計資料給 StatsPage 用
  const computeStats = useCallback((allQuestions = []) => {
    if (sessions.length === 0) {
      return {
        totalAttempted: 0,
        totalCorrect: 0,
        byType: {
          grammar: { attempted: 0, correct: 0 },
          vocabulary: { attempted: 0, correct: 0 },
          reading: { attempted: 0, correct: 0 },
        },
        history: [],
        wrongQuestions: [],
      };
    }

    let totalAttempted = 0;
    let totalCorrect = 0;
    const byType = {
      grammar: { attempted: 0, correct: 0 },
      vocabulary: { attempted: 0, correct: 0 },
      reading: { attempted: 0, correct: 0 },
    };
    const wrongSupabaseIds = new Set();

    sessions.forEach(session => {
      session.results.forEach(r => {
        totalAttempted++;
        if (r.isCorrect) totalCorrect++;
        else wrongSupabaseIds.add(r.supabaseId);

        // 分類統計
        const cat = r.category; // 'grammar' | 'vocabulary' | 'reading'
        if (byType[cat]) {
          byType[cat].attempted++;
          if (r.isCorrect) byType[cat].correct++;
        }
      });
    });

    // 歷次成績 - 每個 session 一筆
    const history = sessions.map((s, i) => {
      const correct = s.results.filter(r => r.isCorrect).length;
      const total = s.results.length;
      return {
        date: `第${i + 1}次`,
        score: total > 0 ? Math.round((correct / total) * 100) : 0,
        total: 100,
      };
    });

    // 錯題回顧 - 從 allQuestions 撈出答錯的題目
    const wrongQuestions = allQuestions.filter(q =>
      wrongSupabaseIds.has(q.supabaseId)
    );

    return { totalAttempted, totalCorrect, byType, history, wrongQuestions };
  }, [sessions]);

  return (
    <SessionContext.Provider value={{ sessions, addSession, clearSessions, computeStats }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSession must be used within SessionProvider');
  return ctx;
}
