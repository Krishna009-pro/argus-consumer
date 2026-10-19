import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, HelpCircle, CheckCircle, AlertTriangle } from 'lucide-react';

export default function FalsificationView({ dossier }) {
  const falsificationCondition = dossier?.falsification_condition || 'The signal should be withdrawn if subsequent comparable periods return within the historical range or verified peer/source evidence explains the deviation.';
  const counterargument = dossier?.counterargument || 'Seasonality, base effects, one-off events, accounting changes, acquisitions, pricing lags and sector movement remain alternatives unless independently tested.';

  const redTeamChecks = [
    { title: 'Seasonality', desc: 'Quarterly or intra-year working capital cycles.', status: 'NOT TESTED', note: 'Requires verified multi-quarter filing series.' },
    { title: 'Base Effects', desc: 'Abnormal pandemic or lockdown comparison base.', status: 'NOT TESTED', note: 'Requires comparative base adjustment.' },
    { title: 'One-off Events', desc: 'Litigation settlements, restructuring, exceptional items.', status: 'NOT TESTED', note: 'No exceptional items flagged in notes.' },
    { title: 'Accounting Changes', desc: 'New Ind AS / IFRS adoption altering asset recognition.', status: 'NOT TESTED', note: 'Accounting policy disclosures unreviewed.' },
    { title: 'Acquisitions & Demergers', desc: 'Undertaking spin-offs (e.g. Note 44 ice cream transfer).', status: 'NOT TESTED', note: 'Demerger cohorts isolated; impact unquantified.' },
    { title: 'Pricing Lags', desc: 'Input cost inflation passthrough delay.', status: 'NOT TESTED', note: 'Commodity WPI index series not connected.' },
    { title: 'Sector-Wide Movements', desc: 'Industry-wide trends affecting all FMCG peers equally.', status: 'NOT TESTED', note: 'Peer panels < 3; sector dispersion unmeasured.' },
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
      <div style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.2rem' }}>
          🛡️ Falsification Rigor & Evaluation Benchmarks
        </h3>
        <p style={{ fontSize: '0.84rem', color: '#64748b' }}>
          Scientific falsification gates ensure that ARGUS withdraws candidate signals unless all 7 benign alternatives are ruled out.
        </p>
      </div>

      {/* Falsification Condition & Counterargument Dual Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '1.75rem' }}>
        <div style={{ background: '#fff5f5', border: '1px solid #fed7d7', borderLeft: '4px solid #dc2626', borderRadius: '12px', padding: '1.2rem 1.4rem' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#dc2626', textTransform: 'uppercase', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <ShieldAlert size={15} /> Scientific Falsification Condition
          </div>
          <p style={{ fontSize: '0.86rem', color: '#1e293b', lineHeight: 1.5 }}>
            {falsificationCondition}
          </p>
        </div>

        <div style={{ background: '#f5f3ff', border: '1px solid #e9d5ff', borderLeft: '4px solid #7c3aed', borderRadius: '12px', padding: '1.2rem 1.4rem' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#7c3aed', textTransform: 'uppercase', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <HelpCircle size={15} /> Skeptic Counterargument
          </div>
          <p style={{ fontSize: '0.86rem', color: '#1e293b', lineHeight: 1.5 }}>
            {counterargument}
          </p>
        </div>
      </div>

      {/* 7 Benign Alternative Checks Grid */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.35rem' }}>
          <h4 style={{ fontSize: '1.05rem', fontWeight: 750, color: '#0f172a' }}>
            🧪 The 7 Benign Alternative Checks (Red-Team Audit)
          </h4>
        </div>
        <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1rem' }}>
          A persistent financial gap is rejected if benign operational alternatives account for the deviation.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.9rem' }}>
          {redTeamChecks.map((c) => (
            <div
              key={c.title}
              style={{
                background: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '10px',
                padding: '0.9rem',
                minHeight: '140px',
                boxShadow: '0 1px 3px rgba(15,23,42,0.03)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ fontSize: '0.88rem', fontWeight: 750, color: '#0f172a', marginBottom: '0.2rem' }}>
                  {c.title}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#475569', lineHeight: 1.4 }}>
                  {c.desc}
                </div>
              </div>
              <div style={{ marginTop: '0.75rem', paddingTop: '0.45rem', borderTop: '1px solid #f1f5f9' }}>
                <div style={{ fontSize: '0.7rem', fontWeight: 750, color: '#d97706' }}>
                  {c.status}
                </div>
                <div style={{ fontSize: '0.68rem', color: '#94a3b8' }}>
                  {c.note}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
