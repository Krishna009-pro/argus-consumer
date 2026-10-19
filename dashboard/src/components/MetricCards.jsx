import React from 'react';
import { motion } from 'framer-motion';

export default function MetricCards({ state, obsCount, panelCount, score, scoreLabel }) {
  const isAnomaly = state === 'validated' || state === 'unexplained';

  const cards = [
    {
      label: 'Run Result',
      value: state ? state.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) : 'Unknown',
      color: isAnomaly ? '#059669' : '#d97706',
      sub: 'Persistence & peer gates enforced',
    },
    {
      label: 'Verified Observations',
      value: obsCount,
      color: '#0284c7',
      sub: 'Traced to official BSE/NSE filings',
    },
    {
      label: 'Audit Panels',
      value: panelCount,
      color: '#4f46e5',
      sub: 'Isolated comparability cohorts',
    },
    {
      label: 'Evidence Score',
      value: `${Number(score || 0).toFixed(1)} (${scoreLabel || 'Weak'})`,
      color: '#7c3aed',
      sub: '5 deterministic component weights',
    },
  ];

  return (
    <div className="kpi-grid">
      {cards.map((c, i) => (
        <motion.div
          key={c.label}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25, delay: i * 0.05 }}
          className="kpi-card"
        >
          <div className="kpi-label">{c.label}</div>
          <div className="kpi-value" style={{ color: c.color }}>
            {c.value}
          </div>
          <div className="kpi-sub">{c.sub}</div>
        </motion.div>
      ))}
    </div>
  );
}
