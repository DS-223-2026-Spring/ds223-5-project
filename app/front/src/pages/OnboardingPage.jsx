import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../context/AppContext';
import FormField from '../components/FormField';
import { NICHES, FORMATS, AGE_GROUPS, GENDERS, INDUSTRIES } from '../constants';
import { createBrand, createInfluencer } from '../api';

export default function OnboardingPage() {
  const { dispatch } = useContext(AppContext);
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [role, setRole] = useState('brand');
  
  const [brandData, setBrandData] = useState({
    name: '', industry: INDUSTRIES[0], location: '', size: 'Startup', budget_min: 1000, budget_max: 5000,
    audience_age_group: '18-24', audience_gender: 'female',
    preferences: [], email: 'contact@brand.com', website: '', instagram: ''
  });

  const [creatorData, setCreatorData] = useState({
    name: '', email: '', niche: NICHES[0], location: '', follower_count: 10000, engagement_rate: 3.5, audience_age_group: '18-24',
    audience_gender: 'female', content_formats: [], rate_min: 500, rate_max: 1500, bio: ''
  });

  const finishOnboarding = async () => {
    // Basic validation
    if (role === 'brand' && (!brandData.name || !brandData.email)) {
      alert("Please fill in the required fields (Name and Email).");
      return;
    }
    if (role === 'influencer' && (!creatorData.name || !creatorData.email)) {
      alert("Please fill in the required fields (Handle and Email).");
      return;
    }

    if (role === 'brand' && brandData.preferences.length === 0) {
      alert('Choose at least one creator niche you want to work with.');
      return;
    }
    if (role === 'influencer' && creatorData.content_formats.length === 0) {
      alert('Choose at least one content format you create.');
      return;
    }

    dispatch({ type: 'SET_ROLE', payload: role });
    let res;
    if (role === 'brand') {
      res = await createBrand(brandData);
      if (res && res.id) {
        dispatch({ type: 'SET_BRAND_ID', payload: res.id });
      }
    } else {
      res = await createInfluencer(creatorData);
      if (res && res.id) {
        dispatch({ type: 'SET_INFLUENCER_ID', payload: res.id });
      }
    }
    setStep(3);
  };

  const renderStepContent = () => {
    if (step === 0) {
      return (
        <div>
          <div className="sec-title">STEP 1 OF 4</div>
          <h2 style={{ margin: '0 0 6px', fontSize: '22px' }}>Welcome to PairUp</h2>
          <p style={{ color: 'var(--color-text-secondary)', marginBottom: '24px' }}>Who are you?</p>
          <div style={{ display: 'flex', gap: '16px' }}>
            <div 
              style={{ flex: 1, border: `2px solid ${role === 'brand' ? 'var(--color-primary)' : 'var(--color-border)'}`, borderRadius: '14px', padding: '24px', cursor: 'pointer', background: role === 'brand' ? 'var(--color-primary-light)' : '#fff' }}
              onClick={() => setRole('brand')}
            >
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>🏢</div>
              <div style={{ fontWeight: '700', marginBottom: '4px' }}>Brand / Business</div>
            </div>
            <div 
              style={{ flex: 1, border: `2px solid ${role === 'influencer' ? 'var(--color-primary)' : 'var(--color-border)'}`, borderRadius: '14px', padding: '24px', cursor: 'pointer', background: role === 'influencer' ? 'var(--color-primary-light)' : '#fff' }}
              onClick={() => setRole('influencer')}
            >
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>✨</div>
              <div style={{ fontWeight: '700', marginBottom: '4px' }}>Creator / Influencer</div>
            </div>
          </div>
          <button className="stButton-primary" style={{ width: '100%', marginTop: '24px' }} onClick={() => setStep(1)}>Continue &rarr;</button>
        </div>
      );
    }
    
    if (step === 1) {
      return (
        <div>
          <div className="sec-title">STEP 2 OF 4</div>
          <h2 style={{ margin: '0 0 6px', fontSize: '22px' }}>{role === 'brand' ? 'Tell us about your brand' : 'Tell us about yourself'}</h2>
          
          {role === 'brand' ? (
            <div style={{ display: 'flex', gap: '16px', marginTop: '24px' }}>
              <div style={{ flex: 1 }}>
                <FormField label="BRAND NAME" value={brandData.name} onChange={v => setBrandData({...brandData, name: v})} />
                <FormField label="LOCATION" value={brandData.location} onChange={v => setBrandData({...brandData, location: v})} />
                <FormField label="MIN BUDGET" type="number" value={brandData.budget_min} onChange={v => setBrandData({...brandData, budget_min: parseInt(v) || 0})} />
                <FormField label="MAX BUDGET" type="number" value={brandData.budget_max} onChange={v => setBrandData({...brandData, budget_max: parseInt(v) || 0})} />
              </div>
              <div style={{ flex: 1 }}>
                <FormField label="INDUSTRY" type="select" options={INDUSTRIES} value={brandData.industry} onChange={v => setBrandData({...brandData, industry: v})} />
                <FormField label="TARGET AGE GROUP" type="select" options={AGE_GROUPS} value={brandData.audience_age_group} onChange={v => setBrandData({...brandData, audience_age_group: v})} />
                <FormField label="TARGET GENDER" type="select" options={GENDERS} value={brandData.audience_gender} onChange={v => setBrandData({...brandData, audience_gender: v})} />
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '16px', marginTop: '24px' }}>
              <div style={{ flex: 1 }}>
                <FormField label="YOUR HANDLE" value={creatorData.name} onChange={v => setCreatorData({...creatorData, name: v})} placeholder="@handle" />
                <FormField label="EMAIL" type="email" value={creatorData.email} onChange={v => setCreatorData({...creatorData, email: v})} placeholder="contact@creator.com" />
                <FormField label="FOLLOWERS" type="number" value={creatorData.follower_count} onChange={v => setCreatorData({...creatorData, follower_count: parseInt(v) || 0})} />
                <FormField label="AGE GROUP" type="select" options={AGE_GROUPS} value={creatorData.audience_age_group} onChange={v => setCreatorData({...creatorData, audience_age_group: v})} />
                <FormField label="LOCATION" value={creatorData.location} onChange={v => setCreatorData({...creatorData, location: v})} />
              </div>
              <div style={{ flex: 1 }}>
                <FormField label="NICHE" type="select" options={NICHES} value={creatorData.niche} onChange={v => setCreatorData({...creatorData, niche: v})} />
                <FormField label="ENGAGEMENT RATE" type="number" step="0.1" suffix="%" value={creatorData.engagement_rate} onChange={v => setCreatorData({...creatorData, engagement_rate: parseFloat(v) || 0})} />
                <FormField label="GENDER" type="select" options={GENDERS} value={creatorData.audience_gender} onChange={v => setCreatorData({...creatorData, audience_gender: v})} />
              </div>
            </div>
          )}
          
          <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
            <button className="stButton-secondary" style={{ flex: 1 }} onClick={() => setStep(0)}>&larr; Back</button>
            <button className="stButton-primary" style={{ flex: 2 }} onClick={() => setStep(2)}>Continue &rarr;</button>
          </div>
        </div>
      );
    }
    
    if (step === 2) {
      return (
        <div>
          <div className="sec-title">STEP 3 OF 4</div>
          <h2 style={{ margin: '0 0 6px', fontSize: '22px' }}>Define your ideal match</h2>
          {role === 'brand' ? (
            <div style={{ marginTop: '24px' }}>
              <FormField
                label="CREATOR NICHES WANTED"
                type="multi-checkbox"
                options={NICHES}
                value={brandData.preferences}
                onChange={(next) => setBrandData({ ...brandData, preferences: next })}
              />
            </div>
          ) : (
            <div style={{ marginTop: '24px' }}>
              <FormField
                label="FORMATS YOU CREATE"
                type="multi-checkbox"
                options={FORMATS}
                value={creatorData.content_formats}
                onChange={(next) => setCreatorData({ ...creatorData, content_formats: next })}
              />
              <FormField label="SHORT BIO" type="textarea" value={creatorData.bio} onChange={v => setCreatorData({...creatorData, bio: v})} />
            </div>
          )}
          
          <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
            <button className="stButton-secondary" style={{ flex: 1 }} onClick={() => setStep(1)}>&larr; Back</button>
            <button className="stButton-primary" style={{ flex: 2 }} onClick={finishOnboarding}>Finish &rarr;</button>
          </div>
        </div>
      );
    }

    if (step === 3) {
      return (
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <div style={{ fontSize: '48px', color: 'var(--color-success)', marginBottom: '16px' }}>✓</div>
          <h2 style={{ margin: '0 0 8px' }}>You're all set!</h2>
          <p style={{ color: 'var(--color-text-secondary)', marginBottom: '32px' }}>We've processed your profile and found matches.</p>
          <button className="stButton-primary" onClick={() => navigate('/discover')} style={{ width: '100%' }}>Go to marketplace</button>
        </div>
      );
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '40px auto', background: '#fff', padding: '40px', borderRadius: '16px', border: '1px solid var(--color-border)', boxShadow: 'var(--shadow-card)' }}>
      {renderStepContent()}
    </div>
  );
}
