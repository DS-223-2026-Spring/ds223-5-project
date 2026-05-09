import React from 'react';
import { useNavigate } from 'react-router-dom';
import ScoreBadge from './ScoreBadge';

function getInitials(name) {
  if (!name) return '??';
  const clean = name.replace('@', '');
  const parts = clean.split('.');
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return clean.slice(0, 2).toUpperCase();
}

export default function CreatorCard({ influencer }) {
  const navigate = useNavigate();

  return (
    <div className="creator-card">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '44px', height: '44px', borderRadius: '50%', background: 'var(--color-primary-light)',
            color: 'var(--color-primary)', fontSize: '14px', fontWeight: '700',
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
          }}>
            {getInitials(influencer.name)}
          </div>
          <div>
            <div style={{ fontSize: '14px', fontWeight: '700' }}>{influencer.name}</div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>{influencer.niche} · {influencer.location}</div>
          </div>
        </div>
        <ScoreBadge score={influencer.total_score} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginBottom: '12px' }}>
        <div><div className="stat-lbl">followers</div><div className="stat-val">{(influencer.followers / 1000).toFixed(1)}K</div></div>
        <div><div className="stat-lbl">engagement</div><div className="stat-val">{influencer.engagement}%</div></div>
        <div><div className="stat-lbl">audience</div><div className="stat-val">{influencer.age}</div></div>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginBottom: '3px' }}>
          ● Niche &nbsp; ● Audience &nbsp; ● Engagement &nbsp; ● History
        </div>
        <div style={{ display: 'flex', gap: '3px', height: '5px' }}>
          <div style={{ flex: 35, background: '#6C63FF', borderRadius: '2px', opacity: Math.max(0.1, influencer.niche_score / 100) }}></div>
          <div style={{ flex: 30, background: '#00C896', borderRadius: '2px', opacity: Math.max(0.1, influencer.audience_score / 100) }}></div>
          <div style={{ flex: 25, background: '#F5A623', borderRadius: '2px', opacity: Math.max(0.1, influencer.engagement_score / 100) }}></div>
          <div style={{ flex: 10, background: '#FF5C5C', borderRadius: '2px', opacity: Math.max(0.1, influencer.history_score / 100) }}></div>
        </div>
      </div>

      <div>
        {influencer.formats.map(f => (
          <span key={f} className="fmt-chip">{f}</span>
        ))}
        <span className="fmt-chip">{influencer.rate}</span>
      </div>

      <button 
        className="stButton-secondary" 
        style={{ width: '100%', marginTop: '16px' }}
        onClick={() => navigate(`/profile/influencer/${influencer.id}`)}
      >
        View profile &rarr;
      </button>
    </div>
  );
}
