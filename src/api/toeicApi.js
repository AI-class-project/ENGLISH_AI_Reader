// api/toeicApi.js
// Frontend API layer: read TOEIC question groups from Supabase and normalize them
// into the UI format used by PracticePage / QuestionManagerPage / StatsPage.

import { supabase } from './supabaseClient';

const QUESTION_TABLE = 'toeic_questions';

const shuffle = (arr) => [...arr].sort(() => Math.random() - 0.5);

const normalizeOptions = (options = {}) => ({
  A: options.A ?? options.a ?? '',
  B: options.B ?? options.b ?? '',
  C: options.C ?? options.c ?? '',
  D: options.D ?? options.d ?? '',
});

const buildDisplayId = (row, type, index) => {
  const prefix =
    type === 'cloze' ? 'CL' :
    type === 'reading_multi' ? 'RM' :
    'RS';

  if (row.id) return `${prefix}-${String(row.id).slice(0, 8)}`;
  return `${prefix}${String(index + 1).padStart(3, '0')}`;
};

const inferType = (category = '', passages = []) => {
  const text = String(category);

  if (
    text.includes('單字') ||
    text.includes('字彙') ||
    text.includes('文法') ||
    text.includes('克漏字') ||
    text.includes('選擇')
  ) {
    return 'cloze';
  }

  if (text.includes('雙篇') || text.includes('多篇') || passages.length > 1) {
    return 'reading_multi';
  }

  return 'reading_single';
};

const inferClozeCategory = (category = '') => {
  const text = String(category);
  if (text.includes('文法')) return 'grammar';
  return 'vocabulary';
};

const normalizeQuestionGroup = (row, index = 0) => {
  const passages = Array.isArray(row.passages) ? row.passages : [];
  const questions = Array.isArray(row.questions) ? row.questions : [];
  const type = inferType(row.category, passages);
  const id = buildDisplayId(row, type, index);

  if (type === 'cloze') {
    const q = questions[0] ?? {};

    return {
      id,
      supabaseId: row.id,
      type: 'cloze',
      category: inferClozeCategory(row.category),
      originalCategory: row.category,
      theme: row.theme ?? '',
      passage: passages[0] || q.question || '',
      options: normalizeOptions(q.options),
      answer: String(q.answer ?? '').toUpperCase(),
      explanation: q.explanation ?? '',
      difficulty: 'medium',
      tags: [row.theme].filter(Boolean),
      created_at: row.created_at,
    };
  }

  const normalizedSubQuestions = questions.map((q, qi) => ({
    id: `${id}-Q${qi + 1}`,
    stem: q.question ?? '',
    options: normalizeOptions(q.options),
    answer: String(q.answer ?? '').toUpperCase(),
    explanation: q.explanation ?? '',
  }));

  const base = {
    id,
    supabaseId: row.id,
    type,
    category: 'reading',
    originalCategory: row.category,
    theme: row.theme ?? '',
    difficulty: 'medium',
    questions: normalizedSubQuestions,
    created_at: row.created_at,
  };

  if (type === 'reading_multi') {
    return {
      ...base,
      passages: passages.map((text, i) => ({
        label: `文章 ${String.fromCharCode(65 + i)}`,
        text,
      })),
    };
  }

  return {
    ...base,
    passage: passages[0] ?? '',
  };
};

const fetchQuestionGroups = async () => {
  const { data, error } = await supabase
    .from(QUESTION_TABLE)
    .select('id, category, theme, passages, questions, created_at')
    .order('created_at', { ascending: false });

  if (error) throw error;
  return (data ?? []).map(normalizeQuestionGroup);
};

const toSupabaseInsertPayload = (questionData) => {
  if (questionData.type === 'cloze') {
    return {
      category: questionData.category === 'grammar' ? '文法選擇' : '單字克漏字',
      theme: questionData.tags?.[0] || '前端新增題目',
      passages: [questionData.passage],
      questions: [
        {
          question: questionData.passage,
          options: questionData.options,
          answer: questionData.answer,
          explanation: questionData.explanation,
        },
      ],
    };
  }

  return {
    category: questionData.type === 'reading_multi' ? '雙篇/多篇閱讀理解' : '單篇閱讀理解',
    theme: '前端新增閱讀題',
    passages: questionData.passages?.map(p => p.text) ?? [questionData.passage].filter(Boolean),
    questions: questionData.questions ?? [],
  };
};

export const api = {
  async getAllQuestionList() {
    return fetchQuestionGroups();
  },

  async getClozeQuestions(count = 5) {
    const allQuestions = await fetchQuestionGroups();
    const cloze = allQuestions.filter(q => q.type === 'cloze');
    return shuffle(cloze).slice(0, Math.min(count, cloze.length));
  },

  async getReadingQuestions(type = 'all') {
    const allQuestions = await fetchQuestionGroups();
    const reading = allQuestions.filter(q => q.type.startsWith('reading'));

    if (type === 'single') return reading.filter(q => q.type === 'reading_single');
    if (type === 'multi') return reading.filter(q => q.type === 'reading_multi');
    return shuffle(reading);
  },

  async getAllQuestions() {
    const allQuestions = await fetchQuestionGroups();
    const cloze = shuffle(allQuestions.filter(q => q.type === 'cloze')).slice(0, 5);
    const reading = shuffle(allQuestions.filter(q => q.type.startsWith('reading'))).slice(0, 3);
    return { cloze, reading };
  },

  async createQuestion(questionData) {
    const payload = toSupabaseInsertPayload(questionData);

    const { data, error } = await supabase
      .from(QUESTION_TABLE)
      .insert(payload)
      .select('id, category, theme, passages, questions, created_at')
      .single();

    if (error) throw error;
    return normalizeQuestionGroup(data);
  },

  async getStats() {
    const allQuestions = await fetchQuestionGroups();
    const wrongQuestions = shuffle(allQuestions).slice(0, 3);

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
      wrongQuestions,
    };
  },
};
