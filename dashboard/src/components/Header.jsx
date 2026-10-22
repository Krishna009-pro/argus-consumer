import React from 'react';
import { Database, Sparkles } from 'lucide-react';

export default function Header() {
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
