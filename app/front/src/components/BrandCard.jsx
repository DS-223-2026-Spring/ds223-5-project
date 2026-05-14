import React from 'react';
import { useNavigate } from 'react-router-dom';
import ScoreBadge from './ScoreBadge';

export default function BrandCard({ brand }) {
  const navigate = useNavigate();

  const formats = brand.preferences.filter(p => ["Reels", "Stories", "Long-form", "Posts"].includes(p));
  const niches = brand.preferences.filter(p => !["Reels", "Stories", "Long-form", "Posts"].includes(p));

  return (
    <div className="creator-card">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '44px', height: '44px', borderRadius: '50%', background: 'var(--color-success-light)',
            color: 'var(--color-success)', fontSize: '14px', fontWeight: '700',
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
          }}>
            {brand.name.slice(0, 2).toUpperCase()}
          </div>
          <div>
            <div style={{ fontSize: '14px', fontWeight: '700' }}>{brand.name}</div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>{brand.industry} · {brand.location}</div>
          </div>
        </div>
        <ScoreBadge score={brand.total_score} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginBottom: '12px' }}>
        <div><div className="stat-lbl">company</div><div className="stat-val" style={{ fontSize: '13px' }}>{brand.size}</div></div>
        <div><div className="stat-lbl">niches</div><div className="stat-val" style={{ fontSize: '13px' }}>{niches.length}</div></div>
        <div><div className="stat-lbl">formats</div><div className="stat-val" style={{ fontSize: '13px' }}>{formats.length}</div></div>
      </div>

      <div style={{ marginBottom: '8px' }}>
        <span style={{
          background: 'var(--color-success-light)', color: 'var(--color-success)', fontSize: '11px', 
          fontWeight: '700', padding: '3px 10px', borderRadius: '6px'
        }}>
          ${brand.budget_min.toLocaleString()}–${brand.budget_max.toLocaleString()}
        </span>
      </div>

      <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '8px', lineHeight: 1.4 }}>
        {(brand.age || '—')} · {(brand.gender || '').replace(/_/g, ' ') || '—'}
      </div>

      <div>
        {brand.preferences.slice(0, 4).map(p => (
          <span key={p} className="fmt-chip">{p}</span>
        ))}
      </div>

      <button 
        className="stButton-secondary" 
        style={{ width: '100%', marginTop: '16px' }}
        onClick={() => navigate(`/profile/brand/${brand.id}`)}
      >
        View brand &rarr;
      </button>
    </div>
  );
}
