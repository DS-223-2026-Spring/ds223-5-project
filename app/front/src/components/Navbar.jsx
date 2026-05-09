import React, { useContext } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { AppContext } from '../context/AppContext';

export default function Navbar() {
  const { state, dispatch } = useContext(AppContext);
  const navigate = useNavigate();
  const location = useLocation();

  if (location.pathname === '/' || location.pathname === '/onboarding') {
    return null; // Do not show navbar on landing and onboarding
  }

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '16px 24px', background: '#fff', borderBottom: '1px solid var(--color-border)'
    }}>
      <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
        <div 
          onClick={() => navigate('/')}
          style={{ cursor: 'pointer', fontSize: '18px', fontWeight: '800', color: 'var(--color-text-primary)' }}
        >
          🔗 PairUp
        </div>
        
        <NavLink 
          to="/discover"
          style={({ isActive }) => ({
            fontWeight: '600', fontSize: '14px', padding: '8px 12px', borderRadius: '8px',
            background: isActive ? 'var(--color-primary-light)' : 'transparent',
            color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            textDecoration: 'none'
          })}
        >
          Discover
        </NavLink>
        <NavLink 
          to="/matches"
          style={({ isActive }) => ({
            fontWeight: '600', fontSize: '14px', padding: '8px 12px', borderRadius: '8px',
            background: isActive ? 'var(--color-primary-light)' : 'transparent',
            color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            textDecoration: 'none'
          })}
        >
          My matches
        </NavLink>
        <NavLink 
          to="/profile"
          end
          style={({ isActive }) => ({
            fontWeight: '600', fontSize: '14px', padding: '8px 12px', borderRadius: '8px',
            background: isActive ? 'var(--color-primary-light)' : 'transparent',
            color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
            textDecoration: 'none'
          })}
        >
          My profile
        </NavLink>
      </div>

      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <button
          className={state.role === 'brand' ? 'stButton-primary' : 'stButton-secondary'}
          onClick={() => {
            dispatch({ type: 'SET_ROLE', payload: 'brand' });
            navigate('/discover');
          }}
        >
          Brand
        </button>
        <button
          className={state.role === 'creator' ? 'stButton-primary' : 'stButton-secondary'}
          onClick={() => {
            dispatch({ type: 'SET_ROLE', payload: 'creator' });
            navigate('/discover');
          }}
        >
          Creator
        </button>
        <div style={{
          width: '32px', height: '32px', borderRadius: '50%', background: 'var(--color-primary-light)',
          border: '2px solid var(--color-primary-border)', display: 'flex', alignItems: 'center',
          justifyContent: 'center', fontSize: '14px'
        }}>
          👤
        </div>
      </div>
    </div>
  );
}
