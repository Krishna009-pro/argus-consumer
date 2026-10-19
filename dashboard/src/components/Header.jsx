import React from 'react';
import { Database, Sparkles, Globe } from 'lucide-react';

export default function Header({ onOpenLiveIntake, isIntakeActive }) {
  return (
    <header className="top-navbar">
      <div className="top-nav-left">
        <div className="brand-badge">
          <div className="brand-icon">◈</div>
          <span>ARGUS</span>
        </div>
        <span className="nav-divider">/</span>
        <span className="nav-title">Autonomous Consumer Financial Intelligence</span>
        <span className="tag-badge tag-neutral" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Sparkles size={12} color="#0284c7" /> Track C: FMCG & Retail
        </span>
      </div>

      <div className="top-nav-right">
        {/* Quick Launcher for 🌐 Live Company Intake */}
        <button
          onClick={onOpenLiveIntake}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '0.42rem 0.95rem',
            borderRadius: '20px',
            background: isIntakeActive ? '#0284c7' : 'rgba(2, 132, 199, 0.08)',
            border: '1.5px solid',
            borderColor: isIntakeActive ? '#0284c7' : 'rgba(2, 132, 199, 0.35)',
            color: isIntakeActive ? '#ffffff' : '#0284c7',
            fontWeight: 800,
            fontSize: '0.78rem',
            cursor: 'pointer',
            transition: 'all 0.18s ease',
            boxShadow: isIntakeActive ? '0 2px 10px rgba(2, 132, 199, 0.3)' : 'none',
          }}
          title="Open Live Company Intake Showcase Studio"
        >
          <Globe size={14} />
          <span>🌐 Live Company Intake</span>
        </button>

        <div className="status-pill status-emerald">
          <span className="pulse-dot pulse-emerald"></span>
          <span>Deterministic R1–R8 Active</span>
        </div>

        <div className="status-pill" style={{ background: '#f8fafc', border: '1px solid #cbd5e1', color: '#475569' }}>
          <Database size={12} style={{ marginRight: '4px' }} />
          <span>SHA-256 Ledger Grounded</span>
        </div>
      </div>
    </header>
  );
}
