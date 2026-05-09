import React, { useState, useContext } from 'react';
import { AppContext } from '../context/AppContext';
import { sendContact, getBrand, getInfluencer } from '../api';
import FormField from './FormField';

export default function CollabModal({ profile, isBrandProfile, onClose }) {
  const { state, dispatch } = useContext(AppContext);
  const [formData, setFormData] = useState({
    handle: '', niche: '', rate: '', email: '',
    brandName: 'Your Brand', idea: '', budget: '',
  });

  React.useEffect(() => {
    let active = true;
    const fetchMyProfile = async () => {
      // If we are viewing a brand profile, we are an influencer pitching to a brand.
      // If we are viewing an influencer profile, we are a brand requesting a collab.
      const myProfile = isBrandProfile ? await getInfluencer(state.userId) : await getBrand(state.userId);
      if (active && myProfile) {
        setFormData(prev => ({
          ...prev,
          handle: isBrandProfile ? myProfile.name || '' : prev.handle,
          niche: isBrandProfile ? myProfile.niche || '' : prev.niche,
          rate: isBrandProfile ? myProfile.rate || '' : prev.rate,
          email: myProfile.email || prev.email,
          brandName: !isBrandProfile ? myProfile.name || 'Your Brand' : prev.brandName,
          budget: (!isBrandProfile && myProfile.budget_min && myProfile.budget_max) 
            ? `$${myProfile.budget_min}–$${myProfile.budget_max}` 
            : prev.budget,
        }));
      }
    };
    fetchMyProfile();
    return () => { active = false; };
  }, [state.userId, isBrandProfile]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const isBrandToInf = !isBrandProfile;
    
    const payload = {
      brand_id: isBrandToInf ? state.userId : profile.id,
      influencer_id: isBrandToInf ? profile.id : state.userId,
      direction: isBrandToInf ? 'brand_to_influencer' : 'influencer_to_brand',
      message: isBrandToInf ? formData.idea : `Handle: ${formData.handle}, Niche: ${formData.niche}, Rate: ${formData.rate}`,
      budget: isBrandToInf ? formData.budget : '',
      email: formData.email,
    };

    const res = await sendContact(payload);
    if (res) {
      dispatch({ type: 'ADD_CONTACTED', payload: profile.id });
      onClose();
    }
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: '#fff', borderRadius: '16px', padding: '32px',
        width: '100%', maxWidth: '480px', boxShadow: 'var(--shadow-modal)'
      }}>
        <div style={{ fontSize: '18px', fontWeight: '800', marginBottom: '4px' }}>
          {isBrandProfile ? `Send pitch to ${profile.name}` : `Collab request to ${profile.name}`}
        </div>
        <div style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginBottom: '24px' }}>
          {isBrandProfile ? `Tell ${profile.name} about yourself.` : `Tell ${profile.name} about your brand.`}
        </div>

        <form onSubmit={handleSubmit}>
          {isBrandProfile ? (
            <>
              <FormField label="YOUR HANDLE" value={formData.handle} onChange={v => setFormData({...formData, handle: v})} placeholder="@yourhandle" />
              <FormField label="NICHE / CONTENT STYLE" value={formData.niche} onChange={v => setFormData({...formData, niche: v})} placeholder="e.g. Fitness" />
              <FormField label="RATE PER POST" value={formData.rate} onChange={v => setFormData({...formData, rate: v})} placeholder="e.g. $800–$1,500" />
              <FormField label="YOUR CONTACT EMAIL" type="email" value={formData.email} onChange={v => setFormData({...formData, email: v})} placeholder="you@email.com" />
            </>
          ) : (
            <>
              <FormField label="YOUR BRAND NAME" value={formData.brandName} onChange={v => setFormData({...formData, brandName: v})} />
              <FormField label="CAMPAIGN / COLLAB IDEA" type="textarea" value={formData.idea} onChange={v => setFormData({...formData, idea: v})} placeholder="Describe your idea..." />
              <FormField label="BUDGET RANGE" value={formData.budget} onChange={v => setFormData({...formData, budget: v})} placeholder="e.g. $2,000–$5,000" />
              <FormField label="YOUR CONTACT EMAIL" type="email" value={formData.email} onChange={v => setFormData({...formData, email: v})} placeholder="you@brand.com" />
            </>
          )}

          <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
            <button type="button" className="stButton-secondary" style={{ flex: 1 }} onClick={onClose}>Cancel</button>
            <button type="submit" className="stButton-primary" style={{ flex: 1 }}>Send request</button>
          </div>
        </form>
      </div>
    </div>
  );
}
