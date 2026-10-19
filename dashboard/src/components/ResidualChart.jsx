import React, { useState } from 'react';
import { motion } from 'framer-motion';

export default function ResidualChart({ analysis }) {
  const panels = analysis?.panels || [];

  // Extract all tested angles
  const allAngles = [];
  panels.forEach((pObj, pIdx) => {
    const p = pObj.panel || {};
    const pLabel = `Panel ${pIdx + 1}: ${p.comparability_cohort} (${p.consolidation_basis})`;
    const angles = pObj.angles || {};
    Object.entries(angles).forEach(([aName, aData]) => {
      if (aData.status === 'tested' && (aData.reported || []).some((v) => v !== null)) {
        allAngles.push({
          panelLabel: pLabel,
          angleName: aName,
          panelInfo: p,
          data: aData,
        });
      }
    });
  });

  const [selectedIdx, setSelectedIdx] = useState(0);
  const [hoveredPoint, setHoveredPoint] = useState(null);

  if (allAngles.length === 0) {
    return (
      <div className="callout-box" style={{ background: '#f8fafc' }}>
        <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
          No tested angles present in this dossier. Panels with fewer than 6 disclosed periods abstain under Rule R4.
        </p>
      </div>
    );
  }

  const activeAngle = allAngles[selectedIdx] || allAngles[0];
  const { angleName, panelLabel, data } = activeAngle;

  const periods = data.periods || [];
  const reported = data.reported || [];
  const lows = data.expected_low || [];
  const highs = data.expected_high || [];
  const spreads = data.expected_spread || [];
  const flags = data.gap_flags || [];

  const points = periods.map((period, i) => ({
    period,
    observed: reported[i],
    low: lows[i],
    high: highs[i],
    spread: spreads[i],
    breach: Boolean(flags[i]),
  })).filter((pt) => pt.observed !== null && pt.observed !== undefined);

  // SVG Chart Geometry
  const width = 800;
  const height = 300;
  const padding = { top: 25, right: 30, bottom: 45, left: 60 };

  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const validVals = points.flatMap((p) => [p.observed, p.low, p.high].filter((v) => v !== null && v !== undefined));
  const minVal = validVals.length ? Math.floor(Math.min(...validVals) * 0.85) : 0;
  const maxVal = validVals.length ? Math.ceil(Math.max(...validVals) * 1.15) : 30;
  const valRange = maxVal - minVal || 1;

  const getX = (idx) => padding.left + (idx / Math.max(points.length - 1, 1)) * chartW;
  const getY = (val) => padding.top + chartH - ((val - minVal) / valRange) * chartH;

  // Build area path for confidence corridor
  const validBandPoints = points.filter((p) => p.low !== null && p.high !== null);
  let bandPath = '';
  if (validBandPoints.length >= 2) {
    const topPath = validBandPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(points.indexOf(p))} ${getY(p.high)}`).join(' ');
    const bottomPath = [...validBandPoints].reverse().map((p) => `L ${getX(points.indexOf(p))} ${getY(p.low)}`).join(' ');
    bandPath = `${topPath} ${bottomPath} Z`;
  }

  // Trajectory Line
  const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(p.observed)}`).join(' ');

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
      <div style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.2rem' }}>
          📈 Quantitative Angle & Historical Range Inspector
        </h3>
        <p style={{ fontSize: '0.84rem', color: '#64748b' }}>
          Center and spread are calculated from historical periods excluding the latest two observations. Values breaching the ±2 spread band are flagged.
        </p>
      </div>

      <div style={{ marginBottom: '1.25rem' }}>
        <label style={{ fontSize: '0.76rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>
          Select Financial Angle to Inspect
        </label>
        <select
          className="dossier-selector"
          style={{ maxWidth: '600px' }}
          value={selectedIdx}
          onChange={(e) => setSelectedIdx(Number(e.target.value))}
        >
          {allAngles.map((item, idx) => (
            <option key={idx} value={idx}>
              {item.angleName.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())} — {item.panelLabel}
            </option>
          ))}
        </select>
      </div>

      {/* SVG Interactive Chart */}
      <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '14px', padding: '1.25rem 1.5rem', boxShadow: 'var(--shadow-sm)', position: 'relative' }}>
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto', overflow: 'visible' }}>
          {/* Y Axis Grid Lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
            const val = minVal + ratio * valRange;
            const y = getY(val);
            return (
              <g key={ratio}>
                <line x1={padding.left} y1={y} x2={width - padding.right} y2={y} stroke="#f1f5f9" strokeWidth="1" />
                <text x={padding.left - 10} y={y + 4} textAnchor="end" fontSize="10" fill="#94a3b8" fontFamily="sans-serif">
                  {val.toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* Shaded Expected Range Band */}
          {bandPath && <path d={bandPath} fill="#bae6fd" opacity="0.4" />}

          {/* Observed Line */}
          <path d={linePath} fill="none" stroke="#0284c7" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />

          {/* Observed Data Points & Markers */}
          {points.map((p, i) => {
            const cx = getX(i);
            const cy = getY(p.observed);
            const isBreach = p.breach;
            const isHovered = hoveredPoint?.period === p.period;

            return (
              <g key={p.period} style={{ cursor: 'pointer' }} onMouseEnter={() => setHoveredPoint(p)} onMouseLeave={() => setHoveredPoint(null)}>
                {/* X Axis Label */}
                <text x={cx} y={height - padding.bottom + 20} textAnchor="middle" fontSize="11" fontWeight="600" fill="#475569" fontFamily="sans-serif">
                  {p.period}
                </text>

                {/* Normal vs Breach Point */}
                <circle cx={cx} cy={cy} r={isBreach ? 7 : 5} fill={isBreach ? '#dc2626' : '#0369a1'} stroke="#ffffff" strokeWidth="2" />
                {isBreach && <circle cx={cx} cy={cy} r={12} fill="none" stroke="#dc2626" strokeWidth="1.5" strokeDasharray="3 3" opacity="0.75" />}
                {isHovered && <circle cx={cx} cy={cy} r={10} fill="none" stroke="#0284c7" strokeWidth="2" />}
              </g>
            );
          })}
        </svg>

        {/* Floating Tooltip */}
        {hoveredPoint && (
          <div style={{
            position: 'absolute',
            top: '20px',
            right: '25px',
            background: '#ffffff',
            border: '1px solid #cbd5e1',
            borderRadius: '8px',
            padding: '0.65rem 0.9rem',
            fontSize: '0.78rem',
            boxShadow: '0 4px 12px rgba(15,23,42,0.08)',
            zIndex: 10,
          }}>
            <div style={{ fontWeight: 750, color: '#0f172a', marginBottom: '0.2rem' }}>
              Period: {hoveredPoint.period}
            </div>
            <div><strong>Observed:</strong> {hoveredPoint.observed?.toFixed(2)}</div>
            {hoveredPoint.low !== null && <div><strong>Expected Low:</strong> {hoveredPoint.low?.toFixed(2)}</div>}
            {hoveredPoint.high !== null && <div><strong>Expected High:</strong> {hoveredPoint.high?.toFixed(2)}</div>}
            <div style={{ color: hoveredPoint.breach ? '#dc2626' : '#059669', fontWeight: 700, marginTop: '0.2rem' }}>
              {hoveredPoint.breach ? '⚠️ Gap Flag (Breached Upper Band)' : '✓ Within Historical Spread'}
            </div>
          </div>
        )}

        {/* Legend */}
        <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', fontSize: '0.8rem', color: '#475569', marginTop: '1rem' }}>
          <span><span style={{ color: '#0284c7', fontWeight: 'bold' }}>■</span> Shaded Band: ±2 MAD Historical Expected Range</span>
          <span><span style={{ color: '#0369a1', fontWeight: 'bold' }}>●</span> Blue Line: Reported Values</span>
          <span><span style={{ color: '#dc2626', fontWeight: 'bold' }}>●</span> Red Marker: Period Range Breached</span>
        </div>
      </div>

      {/* Metric Detail Table */}
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Financial Period</th>
              <th>Observed Value</th>
              <th>Expected Lower</th>
              <th>Expected Upper</th>
              <th>Spread (MAD)</th>
              <th>Screening Flag</th>
            </tr>
          </thead>
          <tbody>
            {points.map((p) => (
              <tr key={p.period}>
                <td style={{ fontWeight: 700, color: '#0f172a' }}>{p.period}</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{p.observed !== null ? p.observed.toFixed(2) : '—'}</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{p.low !== null && p.low !== undefined ? p.low.toFixed(2) : '—'}</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{p.high !== null && p.high !== undefined ? p.high.toFixed(2) : '—'}</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{p.spread !== null && p.spread !== undefined ? p.spread.toFixed(2) : '—'}</td>
                <td>
                  <span className={`tag-badge ${p.breach ? 'status-amber' : 'status-emerald'}`}>
                    {p.breach ? 'BREACH' : 'NORMAL'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
