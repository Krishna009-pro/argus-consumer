import React, { useState } from 'react';
import { motion } from 'framer-motion';

export default function CohortsView({ analysis }) {
  const panels = analysis?.panels || [];
  const [selectedPanelIdx, setSelectedPanelIdx] = useState(0);

  if (panels.length === 0) {
    return (
      <div className="callout-box">
        <p style={{ color: '#64748b' }}>No panels assembled for this company.</p>
      </div>
    );
  }

  const chosenPanel = panels[selectedPanelIdx] || panels[0];
  const pData = chosenPanel.panel || {};
  const periods = (pData.periods || []).map((p) => p.period);
  const metrics = pData.metrics || {};
  const ledgerIds = pData.ledger_ids || {};
  const units = pData.units || {};

  // Build disclosures table rows
  const disclosureRows = [];
  Object.entries(metrics).forEach(([mName, vals]) => {
    const idsByPeriod = ledgerIds[mName] || [];
    const unit = units[mName] || '';
    periods.forEach((period, idx) => {
      const val = vals[idx];
      const ids = idsByPeriod[idx] || [];
      disclosureRows.push({
        period,
        metric: mName.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        value: val,
        unit,
        ledgerIds: ids.join(', '),
      });
    });
  });

  // Angle Status Rows
  const angles = chosenPanel.angles || {};
  const angleRows = Object.entries(angles).map(([k, v]) => ({
    angle: k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    status: (v.status || 'unknown').toUpperCase(),
    reason: v.abstain_reason || 'Tested without abstention.',
    disclosedPeriods: (v.periods || []).length,
  }));

  const cohortMetadata = [
    { label: 'Consolidation Basis', val: pData.consolidation_basis || 'Unknown', color: '#0284c7' },
    { label: 'Reporting Scope', val: (pData.reporting_scope || 'Unknown').replace(/_/g, ' '), color: '#059669' },
    { label: 'Reporting Currency', val: pData.currency || 'INR', color: '#4f46e5' },
    { label: 'Period Granularity', val: pData.period_type || 'Annual', color: '#7c3aed' },
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
      <div style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.2rem' }}>
          📑 Audited Financial Panels & Statement Cohorts
        </h3>
        <p style={{ fontSize: '0.84rem', color: '#64748b' }}>
          Financial figures are grouped into strictly isolated comparability cohorts (e.g. pre-demerger vs post-demerger) to prevent false trends.
        </p>
      </div>

      <div style={{ marginBottom: '1.25rem' }}>
        <label style={{ fontSize: '0.76rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>
          Select Panel Cohort
        </label>
        <select
          className="dossier-selector"
          style={{ maxWidth: '650px' }}
          value={selectedPanelIdx}
          onChange={(e) => setSelectedPanelIdx(Number(e.target.value))}
        >
          {panels.map((p, idx) => (
            <option key={idx} value={idx}>
              Panel {idx + 1}: {p.panel?.comparability_cohort} · {p.panel?.consolidation_basis} ({p.panel?.periods?.length || 0} periods)
            </option>
          ))}
        </select>
      </div>

      {/* Cohort Metadata Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {cohortMetadata.map((c) => (
          <div key={c.label} className="kpi-card" style={{ padding: '0.9rem 1.1rem' }}>
            <div className="kpi-label">{c.label}</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: c.color, textTransform: 'capitalize' }}>
              {c.val}
            </div>
          </div>
        ))}
      </div>

      {/* Audited Disclosures Table */}
      <div style={{ marginBottom: '1.75rem' }}>
        <h4 style={{ fontSize: '1rem', fontWeight: 750, color: '#0f172a', marginBottom: '0.5rem' }}>
          Audited Financial Disclosures
        </h4>
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Period</th>
                <th>Metric</th>
                <th>Disclosed Value</th>
                <th>Unit</th>
                <th>Source Ledger IDs</th>
              </tr>
            </thead>
            <tbody>
              {disclosureRows.map((r, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 700, color: '#0f172a' }}>{r.period}</td>
                  <td>{r.metric}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 650 }}>
                    {r.value !== null && r.value !== undefined ? Number(r.value).toLocaleString() : '—'}
                  </td>
                  <td style={{ color: '#64748b' }}>{r.unit}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: '#0284c7' }}>{r.ledgerIds || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Angle Testing Status */}
      <div>
        <h4 style={{ fontSize: '1rem', fontWeight: 750, color: '#0f172a', marginBottom: '0.5rem' }}>
          Angle Testing Status for this Panel
        </h4>
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Angle</th>
                <th>Screening Status</th>
                <th>Evaluation / Abstain Reason</th>
                <th>Disclosed Periods</th>
              </tr>
            </thead>
            <tbody>
              {angleRows.map((a, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 700, color: '#0f172a' }}>{a.angle}</td>
                  <td>
                    <span className={`tag-badge ${a.status === 'TESTED' ? 'status-emerald' : 'status-amber'}`}>
                      {a.status}
                    </span>
                  </td>
                  <td style={{ color: '#475569', fontSize: '0.8rem' }}>{a.reason}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{a.disclosedPeriods}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
