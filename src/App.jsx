import { useState } from 'react';
import PracticePage from './pages/PracticePage';
import QuestionManagerPage from './pages/QuestionManagerPage';
import StatsPage from './pages/StatsPage';
import { SessionProvider } from './context/Sessioncontext';
import './index.css';

const NAV_ITEMS = [
  { id: 'practice', label: '練習模式', icon: '◎' },
  { id: 'manage', label: '題庫管理', icon: '⊞' },
  { id: 'stats', label: '統計分析', icon: '◈' },
];

export default function App() {
  const [activePage, setActivePage] = useState('practice');

  return (
    <SessionProvider>
      <div className="app-shell">
        <aside className="sidebar">
          <div className="sidebar-brand">
            <span className="brand-mark">T</span>
            <div className="brand-text">
              <span className="brand-title">TOEIC</span>
              <span className="brand-sub">Training System</span>
            </div>
          </div>
          <nav className="sidebar-nav">
            {NAV_ITEMS.map(item => (
              <button
                key={item.id}
                className={`nav-item ${activePage === item.id ? 'active' : ''}`}
                onClick={() => setActivePage(item.id)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
                {activePage === item.id && <span className="nav-indicator" />}
              </button>
            ))}
          </nav>
          <div className="sidebar-footer">
            <div className="version-badge">Beta v0.1</div>
            <p className="footer-note">Supabase Connected</p>
          </div>
        </aside>
        <main className="main-content">
          {activePage === 'practice' && <PracticePage />}
          {activePage === 'manage' && <QuestionManagerPage />}
          {activePage === 'stats' && <StatsPage />}
        </main>
      </div>
    </SessionProvider>
  );
}
