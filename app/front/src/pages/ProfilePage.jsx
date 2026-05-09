import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppContext } from '../context/AppContext';
import { getInfluencer, getBrand, updateInfluencer, updateBrand, getPastCollaborations, createInfluencer, createBrand } from '../api';
import FormField from '../components/FormField';
import ScoreBadge from '../components/ScoreBadge';
import ScoreBars from '../components/ScoreBars';
import CollabModal from '../components/CollabModal';
import { NICHES, FORMATS, INDUSTRIES, GENDERS } from '../constants';

export default function ProfilePage() {
  const { type, id } = useParams();
  const { state, dispatch } = useContext(AppContext);
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [pastCollabs, setPastCollabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editData, setEditData] = useState(null);

  const isOwnProfile = !type || !id;
  const isBrandView = (isOwnProfile && state.role === 'brand') || type === 'brand';
  const profileId = isOwnProfile ? state.userId : parseInt(id, 10);

  useEffect(() => {
    let active = true;
    const fetchProfile = async () => {
      setLoading(true);
      const data = isBrandView 
        ? await getBrand(profileId, !isOwnProfile ? state.userId : null) 
        : await getInfluencer(profileId, !isOwnProfile ? state.userId : null);
      if (active) {
        if (data) {
          setProfile(data);
          setEditData(data);
        } else if (isOwnProfile) {
          // Mock own profile
          const mock = isBrandView 
            ? { id: profileId, name: 'Your Brand', industry: 'General', size: 'SMB', budget_min: 0, budget_max: 0, target: '', location: '', preferences: [], email: '', website: '', instagram: '' }
            : { id: profileId, name: '@yourhandle', email: 'contact@creator.com', niche: 'General', followers: 0, engagement: 0, age: '18-24', gender: 'female', formats: [], rate_min: 0, rate_max: 0, bio: '' };
          setProfile(mock);
          setEditData(mock);
        }
        
        if (!isBrandView && active) {
          const collabs = await getPastCollaborations(profileId);
          setPastCollabs(collabs || []);
        }
        setLoading(false);
      }
    };
    fetchProfile();
    return () => { active = false; };
  }, [type, id, state.role, state.userId, isBrandView, profileId, isOwnProfile]);

  const handleSaveOwnProfile = async () => {
    let success = true;
    if (isBrandView) {
      // If we're mocking the profile (no existing data), create it. Otherwise, update.
      // But how do we know if it was mocked? We can check if `profile.name` is 'Your Brand' or just rely on the API response.
      // Alternatively, we can always try to create if it fails to update.
      const res = await updateBrand(profileId, editData);
      if (!res) {
        // If update failed (likely 404), create it
        const createRes = await createBrand(editData);
        if (createRes && createRes.id) {
          dispatch({ type: 'SET_USER_ID', payload: createRes.id });
        } else {
          success = false;
        }
      }
    } else {
      const payload = {
        name: editData.name,
        niche: editData.niche,
        location: editData.location,
        follower_count: editData.followers,
        engagement_rate: editData.engagement,
        audience_age_group: editData.age,
        audience_gender: editData.gender,
        content_formats: editData.formats,
        email: editData.email,
        bio: editData.bio,
        rate_min: editData.rate_min,
        rate_max: editData.rate_max,
      };
      const res = await updateInfluencer(profileId, payload);
      if (!res) {
        // Create if update fails
        const createRes = await createInfluencer(payload);
        if (createRes && createRes.id) {
          dispatch({ type: 'SET_USER_ID', payload: createRes.id });
        } else {
          success = false;
        }
      }
    }

    if (success) {
      setProfile(editData);
      alert('Profile saved successfully!');
    } else {
      alert('Failed to save profile. Please make sure all required fields are filled.');
    }
  };

  if (loading) return <div style={{ padding: '40px', textAlign: 'center' }}>Loading...</div>;
  if (!profile) return <div style={{ padding: '40px', textAlign: 'center' }}>Profile not found.</div>;

  if (isOwnProfile) {
    return (
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '24px' }}>
        <h1 style={{ margin: '0 0 4px', fontSize: '26px', fontWeight: '800' }}>My profile</h1>
        <p style={{ margin: '0 0 24px', color: 'var(--color-text-muted)' }}>Your {state.role} profile visible on PairUp</p>

        <div className="sec-title">PROFILE DETAILS</div>
        {state.role === 'brand' ? (
          <>
            <div style={{ display: 'flex', gap: '16px' }}>
              <div style={{ flex: 1 }}>
                <FormField label="BRAND NAME" value={editData.name} onChange={v => setEditData({...editData, name: v})} />
                <FormField label="MIN BUDGET" type="number" value={editData.budget_min} onChange={v => setEditData({...editData, budget_min: parseInt(v)})} />
                <FormField label="MAX BUDGET" type="number" value={editData.budget_max} onChange={v => setEditData({...editData, budget_max: parseInt(v)})} />
              </div>
              <div style={{ flex: 1 }}>
                <FormField label="INDUSTRY" type="select" options={INDUSTRIES} value={editData.industry} onChange={v => setEditData({...editData, industry: v})} />
                <FormField label="LOCATION" value={editData.location} onChange={v => setEditData({...editData, location: v})} />
              </div>
            </div>
            <FormField label="TARGET AUDIENCE" value={editData.target} onChange={v => setEditData({...editData, target: v})} />
            <FormField label="CREATOR PREFERENCES" value={editData.preferences.join(', ')} onChange={v => setEditData({...editData, preferences: v.split(',').map(s=>s.trim())})} placeholder="Comma separated..." />
          </>
        ) : (
          <>
            <div style={{ display: 'flex', gap: '16px' }}>
              <div style={{ flex: 1 }}>
                <FormField label="HANDLE" value={editData.name} onChange={v => setEditData({...editData, name: v})} />
                <FormField label="EMAIL" type="email" value={editData.email} onChange={v => setEditData({...editData, email: v})} />
                <FormField label="FOLLOWERS" type="number" value={editData.followers} onChange={v => setEditData({...editData, followers: parseInt(v)})} />
                <FormField label="LOCATION" value={editData.location} onChange={v => setEditData({...editData, location: v})} />
              </div>
              <div style={{ flex: 1 }}>
                <FormField label="NICHE" type="select" options={NICHES} value={editData.niche} onChange={v => setEditData({...editData, niche: v})} />
                <FormField label="ENGAGEMENT RATE" type="number" step="0.1" suffix="%" value={editData.engagement} onChange={v => setEditData({...editData, engagement: parseFloat(v)})} />
                <FormField label="GENDER" type="select" options={GENDERS} value={editData.gender} onChange={v => setEditData({...editData, gender: v})} />
              </div>
            </div>
            <FormField label="BIO" type="textarea" value={editData.bio} onChange={v => setEditData({...editData, bio: v})} />
          </>
        )}

        <button className="stButton-primary" onClick={handleSaveOwnProfile} style={{ marginTop: '16px' }}>Save Profile</button>
      </div>
    );
  }

  // View someone else's profile
  const alreadySaved = state.saved.has(profile.id);
  const alreadyContacted = state.contacted.has(profile.id);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '24px' }}>
      <button className="stButton-secondary" onClick={() => navigate(-1)} style={{ marginBottom: '24px' }}>&larr; Back to results</button>

      <div style={{
        background: isBrandView ? 'linear-gradient(135deg,#E0FBF4,#D0F5EB)' : 'linear-gradient(135deg,#F0EFFE,#E8E6FF)',
        border: '1px solid var(--color-border)', borderRadius: '14px', padding: '24px 28px', marginBottom: '20px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '52px', height: '52px', borderRadius: '50%', 
            background: isBrandView ? '#E0FBF4' : '#F0EFFE', 
            color: isBrandView ? '#00A87D' : '#6C63FF', 
            fontSize: '17px', fontWeight: '700', display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            {isBrandView ? profile.name.slice(0, 2).toUpperCase() : profile.name.replace('@','').slice(0,2).toUpperCase()}
          </div>
          <div>
            <div style={{ fontSize: '22px', fontWeight: '800' }}>{profile.name}</div>
            <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>{isBrandView ? profile.industry : profile.niche} · {profile.location}</div>
          </div>
        </div>
        <ScoreBadge score={profile.total_score} style={{ fontSize: '15px', padding: '8px 18px' }} />
      </div>

      <div className="sec-title">MATCH SCORE BREAKDOWN</div>
      <ScoreBars niche={profile.niche_score} audience={profile.audience_score} engagement={profile.engagement_score} history={profile.history_score} />

      <div style={{ display: 'flex', gap: '16px', marginTop: '32px' }}>
        <button 
          className="stButton-secondary" 
          style={{ flex: 1 }} 
          onClick={() => dispatch({ type: alreadySaved ? 'REMOVE_SAVED' : 'ADD_SAVED', payload: profile.id })}
        >
          {alreadySaved ? '★ Saved' : '☆ Save profile'}
        </button>
        <button 
          className={alreadyContacted ? "stButton-secondary" : "stButton-primary"} 
          style={{ flex: 1 }} 
          disabled={alreadyContacted}
          onClick={() => !alreadyContacted && setShowModal(true)}
        >
          {alreadyContacted ? '✅ Request sent' : 'Send collab request'}
        </button>
      </div>

      {showModal && (
        <CollabModal profile={profile} isBrandProfile={isBrandView} onClose={() => setShowModal(false)} />
      )}
    </div>
  );
}
