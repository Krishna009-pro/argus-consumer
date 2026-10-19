import React from 'react';
import { motion } from 'framer-motion';
import { FileDown, Sparkles, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function HeroBanner({ company, state, evidenceCount, onExportPdf }) {
  const isAnomaly = state === 'validated' || state === 'unexplained';
  const statusTitle = isAnomaly ? 'Validated Anomaly' : 'Evidence-Grounded Abstention';

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="hero-card"
    >
      <div className="hero-main">
        <div className="hero-badges">
          <span className="tag-badge tag-neutral">
            ◈ Track C: FMCG & Consumer Retail
          </span>
          <span className={`status-pill ${isAnomaly ? 'status-emerald' : 'status-amber'}`}>
            <span className={`pulse-dot ${isAnomaly ? 'pulse-emerald' : 'pulse-amber'}`}></span>
            {statusTitle}
          </span>
        </div>
        <h1 className="hero-title">{company}</h1>
        <p className="hero-subtitle">
          Deterministic financial screening · Verifiable SHA-256 source ledger · Zero synthetic hallucinations
        </p>
      </div>

      <div className="hero-action">
        <div style={{ fontSize: '0.72rem', fontWeight: 750, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.45rem' }}>
          Formal Audit Export
        </div>
        <button
          onClick={onExportPdf}
          className="btn-primary"
          title="Print or export verifiable audit report"
        >
          <FileDown size={15} />
          <span>Export Dossier</span>
        </button>
        <span style={{ fontSize: '0.68rem', color: '#94a3b8', marginTop: '0.4rem' }}>
          SHA-256 Verified Audit Trail
        </span>
      </div>
    </motion.div>
  );
}
