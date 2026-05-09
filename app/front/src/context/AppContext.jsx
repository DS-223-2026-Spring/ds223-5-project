import React, { createContext, useReducer } from 'react';

const initialState = {
  role: localStorage.getItem('pairup_role') || 'brand',
  brandId: parseInt(localStorage.getItem('pairup_brandId') || '0', 10),
  influencerId: parseInt(localStorage.getItem('pairup_influencerId') || '0', 10),
  saved: new Set(JSON.parse(localStorage.getItem('pairup_saved') || '[]')),
  contacted: new Set(JSON.parse(localStorage.getItem('pairup_contacted') || '[]')),
};

// Compute userId based on the current role
function getUserId(state) {
  return state.role === 'brand' ? state.brandId : state.influencerId;
}

export const AppContext = createContext();

function reducer(state, action) {
  switch (action.type) {
    case 'SET_ROLE':
      localStorage.setItem('pairup_role', action.payload);
      return { ...state, role: action.payload };
    case 'SET_BRAND_ID':
      localStorage.setItem('pairup_brandId', action.payload);
      return { ...state, brandId: parseInt(action.payload, 10) };
    case 'SET_INFLUENCER_ID':
      localStorage.setItem('pairup_influencerId', action.payload);
      return { ...state, influencerId: parseInt(action.payload, 10) };
    // Legacy action — route to the correct role-specific ID
    case 'SET_USER_ID': {
      const id = parseInt(action.payload, 10);
      if (state.role === 'brand') {
        localStorage.setItem('pairup_brandId', id);
        return { ...state, brandId: id };
      } else {
        localStorage.setItem('pairup_influencerId', id);
        return { ...state, influencerId: id };
      }
    }
    case 'ADD_SAVED': {
      const newSaved = new Set(state.saved);
      newSaved.add(action.payload);
      localStorage.setItem('pairup_saved', JSON.stringify([...newSaved]));
      return { ...state, saved: newSaved };
    }
    case 'REMOVE_SAVED': {
      const newSaved = new Set(state.saved);
      newSaved.delete(action.payload);
      localStorage.setItem('pairup_saved', JSON.stringify([...newSaved]));
      return { ...state, saved: newSaved };
    }
    case 'ADD_CONTACTED': {
      const newContacted = new Set(state.contacted);
      newContacted.add(action.payload);
      localStorage.setItem('pairup_contacted', JSON.stringify([...newContacted]));
      return { ...state, contacted: newContacted };
    }
    default:
      return state;
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  // Expose userId as a computed getter so all components get the right ID for the current role
  const enrichedState = {
    ...state,
    get userId() {
      return getUserId(state);
    },
  };

  return (
    <AppContext.Provider value={{ state: enrichedState, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}
