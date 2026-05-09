import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../context/AppContext';
import { getContactRequests, getInfluencer, getBrand, updateContactRequest } from '../api';
import ScoreBadge from '../components/ScoreBadge';

export default function MatchesPage() {
  const { state, dispatch } = useContext(AppContext);
  const navigate = useNavigate();
  const [incomingRequests, setIncomingRequests] = useState([]);
  const [sentRequests, setSentRequests] = useState([]);
  const [savedProfiles, setSavedProfiles] = useState([]);
  const [updatingId, setUpdatingId] = useState(null);

  useEffect(() => {
    getContactRequests(state.userId).then(allRequests => {
      const incoming = [];
      const sent = [];
      for (const r of allRequests) {
        const iAmSender =
          (state.role === 'brand' && r.direction === 'brand_to_influencer' && r.brand_id === state.userId) ||
          (state.role === 'influencer' && r.direction === 'influencer_to_brand' && r.influencer_id === state.userId);
        if (iAmSender) {
          sent.push(r);
        } else {
          incoming.push(r);
        }
      }
      setIncomingRequests(incoming);
      setSentRequests(sent);
    });
  }, [state.userId, state.role]);

  useEffect(() => {
    const fetchSaved = async () => {
      const arr = Array.from(state.saved);
      const profiles = await Promise.all(arr.map(id => state.role === 'brand' ? getInfluencer(id, state.userId) : getBrand(id, state.userId)));
      setSavedProfiles(profiles.filter(Boolean));
    };
    fetchSaved();
  }, [state.saved, state.role]);

  const handleStatusUpdate = async (requestId, newStatus) => {
    setUpdatingId(requestId);
    const res = await updateContactRequest(requestId, newStatus);
    if (res) {
      setIncomingRequests(prev => prev.map(r => r.id === requestId ? { ...r, status: newStatus } : r));
    }
    setUpdatingId(null);
  };

  const statusBadge = (status) => {
    const styles = {
      pending: { bg: '#FFF8E1', color: '#F9A825', label: '⏳ Pending' },
      accepted: { bg: '#E8F5E9', color: '#2E7D32', label: '✅ Accepted' },
      rejected: { bg: '#FFEBEE', color: '#C62828', label: '✕ Rejected' },
      closed: { bg: '#ECEFF1', color: '#546E7A', label: '🔒 Closed' },
    };
    const s = styles[status] || styles.pending;
    return (
      <span style={{
        background: s.bg, color: s.color, fontSize: '11px', fontWeight: '700',
        padding: '3px 10px', borderRadius: '10px', whiteSpace: 'nowrap',
      }}>{s.label}</span>
    );
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '24px' }}>
      <h1 style={{ margin: '0 0 4px', fontSize: '26px', fontWeight: '800' }}>My matches</h1>
      <p style={{ margin: '0 0 28px', color: 'var(--color-text-muted)' }}>Your saved profiles, incoming requests, and sent collaboration requests</p>

      {/* ---- INCOMING REQUESTS ---- */}
      <div className="sec-title">INCOMING REQUESTS &nbsp; {incomingRequests.length}</div>
      {incomingRequests.length === 0 ? (
        <div style={{ background: '#fff', border: '1px solid var(--color-border)', borderRadius: '14px', padding: '48px', textAlign: 'center', marginBottom: '24px' }}>
          <div style={{ fontSize: '28px', marginBottom: '10px' }}>📥</div>
          <div style={{ fontSize: '14px', color: 'var(--color-text-muted)' }}>No incoming requests yet. When someone reaches out to you, it'll show up here.</div>
        </div>
      ) : (
        <div style={{ marginBottom: '24px' }}>
          {incomingRequests.map(r => (
            <div key={`in-${r.id}`} className="creator-card" style={{
              borderLeft: `3px solid ${r.status === 'pending' ? '#F9A825' : r.status === 'accepted' ? '#2E7D32' : '#C62828'}`,
              marginBottom: '8px', padding: '16px 20px',
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ fontWeight: '700', fontSize: '15px' }}>{r.sender_name}</span>
                    {statusBadge(r.status)}
                  </div>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '12px', marginBottom: '6px' }}>
                    {r.direction === 'brand_to_influencer' ? 'Brand wants to collaborate' : 'Creator pitching to you'} · {new Date(r.created_at).toLocaleDateString()}
                  </div>
                  {r.message && (
                    <div style={{
                      fontSize: '13px', color: 'var(--color-text-secondary)',
                      background: '#F8F9FA', borderRadius: '8px', padding: '8px 12px', marginTop: '4px',
                      maxHeight: '60px', overflow: 'hidden',
                    }}>
                      "{r.message}"
                    </div>
                  )}
                  {r.budget && <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '4px' }}>💰 Budget: {r.budget}</div>}
                </div>

                <div style={{ display: 'flex', gap: '8px', marginLeft: '16px', alignItems: 'center', flexShrink: 0 }}>
                  {r.status === 'pending' ? (
                    <>
                      <button
                        className="stButton-primary"
                        style={{ padding: '6px 16px', fontSize: '13px' }}
                        disabled={updatingId === r.id}
                        onClick={() => handleStatusUpdate(r.id, 'accepted')}
                      >
                        Accept
                      </button>
                      <button
                        className="stButton-secondary"
                        style={{ padding: '6px 16px', fontSize: '13px', color: 'var(--color-danger)' }}
                        disabled={updatingId === r.id}
                        onClick={() => handleStatusUpdate(r.id, 'rejected')}
                      >
                        Reject
                      </button>
                    </>
                  ) : (
                    <button
                      className="stButton-secondary"
                      style={{ padding: '6px 16px', fontSize: '13px' }}
                      onClick={() => {
                        const profileType = r.direction === 'brand_to_influencer' ? 'brand' : 'influencer';
                        const profileId = r.direction === 'brand_to_influencer' ? r.brand_id : r.influencer_id;
                        navigate(`/profile/${profileType}/${profileId}`);
                      }}
                    >
                      View &rarr;
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ---- SAVED PROFILES ---- */}
      <div className="sec-title">SAVED &nbsp; {state.saved.size}</div>
      {savedProfiles.length === 0 ? (
        <div style={{ background: '#fff', border: '1px solid var(--color-border)', borderRadius: '14px', padding: '48px', textAlign: 'center', marginBottom: '24px' }}>
          <div style={{ fontSize: '28px', marginBottom: '10px' }}>☆</div>
          <div style={{ fontSize: '14px', color: 'var(--color-text-muted)' }}>No saved profiles yet. Browse the marketplace and save your favourites.</div>
        </div>
      ) : (
        savedProfiles.map(p => (
          <div key={p.id} className="creator-card" style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: '700', fontSize: '15px' }}>{p.name}</div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: '12px', marginTop: '4px' }}>{p.niche || p.industry}</div>
            </div>
            <ScoreBadge score={p.total_score} style={{ marginRight: '16px' }} />
            <button className="stButton-secondary" onClick={() => navigate(`/profile/${state.role === 'brand' ? 'influencer' : 'brand'}/${p.id}`)}>View &rarr;</button>
            <button className="stButton-secondary" style={{ marginLeft: '8px', padding: '8px', color: 'var(--color-danger)' }} onClick={() => dispatch({ type: 'REMOVE_SAVED', payload: p.id })}>✕</button>
          </div>
        ))
      )}

      {/* ---- SENT REQUESTS ---- */}
      <div style={{ height: '24px' }}></div>
      <div className="sec-title">REQUESTS SENT &nbsp; {sentRequests.length + state.contacted.size}</div>

      {sentRequests.length === 0 && state.contacted.size === 0 ? (
        <div style={{ background: '#fff', border: '1px solid var(--color-border)', borderRadius: '14px', padding: '48px', textAlign: 'center' }}>
          <div style={{ fontSize: '28px', marginBottom: '10px' }}>✉</div>
          <div style={{ fontSize: '14px', color: 'var(--color-text-muted)' }}>No requests sent yet. Open a profile and reach out directly.</div>
        </div>
      ) : (
        <>
          {sentRequests.map(r => (
            <div key={`sent-${r.id}`} className="creator-card" style={{ borderLeft: '3px solid var(--color-primary)', marginBottom: '8px', display: 'flex', alignItems: 'center', padding: '14px 20px' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontWeight: '700', fontSize: '15px' }}>To: {r.receiver_name}</span>
                  {statusBadge(r.status)}
                </div>
                <div style={{ color: 'var(--color-text-muted)', fontSize: '12px', marginTop: '4px' }}>
                  {new Date(r.created_at).toLocaleDateString()}
                  {r.budget && ` · Budget: ${r.budget}`}
                </div>
              </div>
              <button className="stButton-secondary" onClick={() => {
                const profileType = r.direction === 'brand_to_influencer' ? 'influencer' : 'brand';
                const profileId = r.direction === 'brand_to_influencer' ? r.influencer_id : r.brand_id;
                navigate(`/profile/${profileType}/${profileId}`);
              }}>View &rarr;</button>
            </div>
          ))}
          {Array.from(state.contacted)
            .filter(cid => !sentRequests.some(r => (r.direction === 'brand_to_influencer' ? r.influencer_id : r.brand_id) === cid))
            .map(id => (
              <div key={`contacted-${id}`} className="creator-card" style={{ borderLeft: '3px solid var(--color-primary)', marginBottom: '8px', display: 'flex', alignItems: 'center' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: '700', fontSize: '15px' }}>Profile #{id} {statusBadge('pending')}</div>
                  <div style={{ color: 'var(--color-text-muted)', fontSize: '12px', marginTop: '4px' }}>Awaiting response</div>
                </div>
                <button className="stButton-secondary" onClick={() => navigate(`/profile/${state.role === 'brand' ? 'influencer' : 'brand'}/${id}`)}>View &rarr;</button>
              </div>
            ))}
        </>
      )}
    </div>
  );
}
