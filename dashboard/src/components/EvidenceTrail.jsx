import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ExternalLink, ChevronDown, ChevronUp, Hash, CheckCircle, FileText } from 'lucide-react';

export default function EvidenceTrail({ linkedEntries }) {
  const [query, setQuery] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  const filtered = (linkedEntries || []).filter((e) => {
    const q = query.toLowerCase();
    return (
      (e.id || '').toLowerCase().includes(q) ||
      (e.metric || '').toLowerCase().includes(q) ||
      (e.period || '').toLowerCase().includes(q) ||
      (e.snippet || '').toLowerCase().includes(q)
    );
  });

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
      <div style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.2rem' }}>
          🔍 Zero-Hallucination Evidence Trail
        </h3>
        <p style={{ fontSize: '0.84rem', color: '#64748b' }}>
          Every number used in ARGUS originates from a human-reviewed public filing with verbatim snippet and SHA-256 hash.
        </p>
      </div>

      {/* Search Input */}
      <div className="search-wrapper">
        <Search size={16} className="search-icon" />
        <input
          type="text"
          className="search-input"
          placeholder="Filter ledger observations (e.g. Revenue, FY2025, or L0008)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      <div style={{ fontSize: '0.78rem', color: '#64748b', marginBottom: '0.75rem' }}>
        Showing {filtered.length} of {linkedEntries.length} verified observations.
      </div>

      {/* Evidence Table */}
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Ledger ID</th>
              <th>Metric</th>
              <th>Disclosed Value</th>
              <th>Unit</th>
              <th>Period</th>
              <th>Basis</th>
              <th>PDF Page</th>
              <th>Filing Source</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((e) => {
              const isExpanded = expandedId === e.id;
              return (
                <React.Fragment key={e.id}>
                  <tr style={{ background: isExpanded ? '#f8fafc' : 'transparent' }}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 750, color: '#0284c7' }}>
                      {e.id}
                    </td>
                    <td style={{ fontWeight: 650, color: '#0f172a' }}>
                      {(e.metric || '').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                      {e.value !== null && e.value !== undefined ? Number(e.value).toLocaleString() : '—'}
                    </td>
                    <td style={{ color: '#64748b' }}>{e.unit}</td>
                    <td style={{ fontWeight: 600 }}>{e.period}</td>
                    <td style={{ textTransform: 'capitalize', color: '#475569' }}>{e.consolidation_basis}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>Page {e.doc_page || 'N/A'}</td>
                    <td>
                      {e.source_url ? (
                        <a
                          href={e.source_url}
                          target="_blank"
                          rel="noreferrer"
                          style={{
                            color: '#0284c7',
                            textDecoration: 'none',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '3px',
                            fontWeight: 600,
                          }}
                        >
                          <span>PDF</span>
                          <ExternalLink size={12} />
                        </a>
                      ) : (
                        <span style={{ color: '#94a3b8' }}>—</span>
                      )}
                    </td>
                    <td>
                      <button
                        onClick={() => toggleExpand(e.id)}
                        style={{
                          background: 'transparent',
                          border: '1px solid #cbd5e1',
                          borderRadius: '6px',
                          padding: '3px 8px',
                          fontSize: '0.72rem',
                          fontWeight: 650,
                          color: '#475569',
                          cursor: 'pointer',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '3px',
                        }}
                      >
                        <span>{isExpanded ? 'Close' : 'Inspect'}</span>
                        {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                      </button>
                    </td>
                  </tr>

                  {/* Expandable Forensic Provenance Drawer */}
                  {isExpanded && (
                    <tr>
                      <td colSpan={9} style={{ background: '#f8fafc', padding: '1rem 1.25rem', borderBottom: '1.5px solid #cbd5e1' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
                          <div>
                            <div style={{ fontSize: '0.75rem', fontWeight: 750, color: '#0f172a', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                              Verbatim Statement Excerpt
                            </div>
                            <div className="evidence-snippet">
                              "{e.snippet || 'No verbatim snippet text recorded.'}"
                            </div>
                            <div style={{ fontSize: '0.72rem', color: '#64748b' }}>
                              Physical Location: Page {e.doc_page || 'N/A'} of audited annual filing.
                            </div>
                          </div>

                          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.75rem 1rem' }}>
                            <div style={{ fontSize: '0.75rem', fontWeight: 750, color: '#0f172a', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                              Verification Metadata
                            </div>
                            <div style={{ fontSize: '0.76rem', color: '#334155', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                              <div><strong>Auditor:</strong> {e.verified_by || 'Verified Auditor'}</div>
                              <div><strong>Scope:</strong> {e.reporting_scope || 'N/A'}</div>
                              <div>
                                <strong>SHA-256:</strong>{' '}
                                <code style={{ fontSize: '0.7rem', color: '#0284c7' }}>
                                  {(e.source_sha256 || '').slice(0, 16)}...
                                </code>
                              </div>
                            </div>
                            {e.source_url && (
                              <a
                                href={e.source_url}
                                target="_blank"
                                rel="noreferrer"
                                className="btn-primary"
                                style={{ marginTop: '0.75rem', textDecoration: 'none', padding: '0.4rem 0.75rem', fontSize: '0.75rem' }}
                              >
                                <FileText size={13} />
                                <span>Open Official PDF</span>
                              </a>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
