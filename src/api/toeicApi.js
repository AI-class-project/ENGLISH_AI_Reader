// api/toeicApi.js
// Simulates backend API (e.g. FastAPI) responses
// Replace fetch() calls here when real backend is ready

import { toeicPool } from '../data/toeic_pool';

const delay = (ms) => new Promise(r => setTimeout(r, ms));

// Shuffle helper
const shuffle = (arr) => [...arr].sort(() => Math.random() - 0.5);

export const api = {
  // GET /questions/cloze?count=5
  async getClozeQuestions(count = 5) {
    await delay(300);
    const shuffled = shuffle(toeicPool.cloze);
    return shuffled.slice(0, Math.min(count, shuffled.length));
  },

  // GET /questions/reading?type=single|multi|all
  async getReadingQuestions(type = 'all') {
    await delay(300);
    if (type === 'single') return toeicPool.reading.filter(q => q.type === 'reading_single');
    if (type === 'multi') return toeicPool.reading.filter(q => q.type === 'reading_multi');
    return shuffle(toeicPool.reading);
  },

  // GET /questions/all - random full session
  async getAllQuestions() {
    await delay(400);
    const cloze = shuffle(toeicPool.cloze).slice(0, 5);
    const reading = shuffle(toeicPool.reading).slice(0, 3);
    return { cloze, reading };
  },

  // POST /questions (create new question) - mock write
  async createQuestion(questionData) {
    await delay(500);
    console.log('[API] Creating question:', questionData);
    return { success: true, id: `NEW_${Date.now()}`, ...questionData };
  },

  // GET /stats
  async getStats() {
    await delay(200);
    // Return mock stats (in real app this comes from user session storage/DB)
    return {
      totalAttempted: 42,
      totalCorrect: 31,
      byType: {
        grammar: { attempted: 18, correct: 14 },
        vocabulary: { attempted: 12, correct: 9 },
        reading: { attempted: 12, correct: 8 },
      },
      history: [
        { date: '2024-11', score: 68, total: 100 },
        { date: '2024-12', score: 74, total: 100 },
        { date: '2025-01', score: 79, total: 100 },
        { date: '2025-02', score: 82, total: 100 },
        { date: '2025-03', score: 85, total: 100 },
      ],
      wrongQuestions: shuffle([...toeicPool.cloze, ...toeicPool.reading]).slice(0, 3)
    };
  }
};
