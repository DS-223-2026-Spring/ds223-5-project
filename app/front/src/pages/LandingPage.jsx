import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../context/AppContext';

export default function LandingPage() {
  const { dispatch } = useContext(AppContext);
  const navigate = useNavigate();

  const handleRoleSelect = (role) => {
    dispatch({ type: 'SET_ROLE', payload: role });
    navigate('/onboarding');
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 24px' }}>
        <div style={{ fontSize: '18px', fontWeight: '800' }}>🔗 PairUp</div>
      </div>

      <div style={{ maxWidth: '800px', margin: '40px auto 0', textAlign: 'center' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'var(--color-primary-light)',
          color: 'var(--color-primary)', fontSize: '13px', fontWeight: '600', padding: '6px 18px',
          borderRadius: '20px', border: '1px solid var(--color-primary-border)', marginBottom: '24px'
        }}>
          <span style={{ width: '7px', height: '7px', background: 'var(--color-primary)', borderRadius: '50%' }}></span>
          Smart matching · No agencies needed
        </div>

        <h1 style={{ fontSize: '44px', fontWeight: '800', lineHeight: 1.15, letterSpacing: '-1px', marginBottom: '16px' }}>
          Where brands meet<br/><span style={{ color: 'var(--color-primary)' }}>the right creators</span>
        </h1>

        <p style={{ fontSize: '16px', color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: '36px', maxWidth: '600px', margin: '0 auto 36px' }}>
          PairUp connects small businesses with micro-influencers using
          data-driven match scores — not guesswork. Find your perfect creative partner in minutes.
        </p>

        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
          <button className="stButton-primary" onClick={() => handleRoleSelect('brand')} style={{ padding: '12px 24px', fontSize: '15px' }}>
            🏢 I'm a brand
          </button>
          <button className="stButton-secondary" onClick={() => handleRoleSelect('influencer')} style={{ padding: '12px 24px', fontSize: '15px' }}>
            ✨ I'm a creator
          </button>
          <button className="stButton-secondary" onClick={() => navigate('/discover')} style={{ padding: '12px 24px', fontSize: '15px' }}>
            🔍 Browse marketplace
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '24px', marginTop: '64px' }}>
        {[
          { val: '50', lbl: 'Creators listed' },
          { val: '20', lbl: 'Brands seeking' },
          { val: '$5.78', lbl: 'Avg ROI per $1 spent' },
        ].map((s, i) => (
          <div key={i} style={{ background: '#fff', border: '1px solid var(--color-border)', borderRadius: '14px', padding: '24px', textAlign: 'center', minWidth: '200px' }}>
            <div style={{ fontSize: '30px', fontWeight: '800', color: 'var(--color-primary)', marginBottom: '4px' }}>{s.val}</div>
            <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>{s.lbl}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
