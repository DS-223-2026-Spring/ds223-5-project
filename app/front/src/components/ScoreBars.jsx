import React from 'react';

export default function ScoreBars({ niche, audience, engagement, history }) {
  const bars = [
    { label: 'Niche 35%', val: niche, color: '#6C63FF' },
    { label: 'Audience 30%', val: audience, color: '#00C896' },
    { label: 'Engagement 25%', val: engagement, color: '#F5A623' },
    { label: 'History 10%', val: history, color: '#FF5C5C' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
      {bars.map((b, i) => (
        <div key={i}>
          <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            {b.label}
          </div>
          <div style={{ background: 'var(--color-border)', borderRadius: '4px', height: '7px', overflow: 'hidden' }}>
            <div style={{ width: `${b.val}%`, background: b.color, height: '100%', borderRadius: '4px' }}></div>
          </div>
          <div style={{ fontSize: '13px', fontWeight: '700', color: b.color, marginTop: '4px' }}>
            {b.val}
          </div>
        </div>
      ))}
    </div>
  );
}
