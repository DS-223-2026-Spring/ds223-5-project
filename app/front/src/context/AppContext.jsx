import React, { createContext, useReducer, useEffect } from 'react';

const initialState = {
  role: localStorage.getItem('pairup_role') || 'brand',
  userId: parseInt(localStorage.getItem('pairup_userId') || '1', 10),
  saved: new Set(JSON.parse(localStorage.getItem('pairup_saved') || '[]')),
  contacted: new Set(JSON.parse(localStorage.getItem('pairup_contacted') || '[]')),
};

export const AppContext = createContext();

function reducer(state, action) {
  switch (action.type) {
    case 'SET_ROLE':
      localStorage.setItem('pairup_role', action.payload);
      return { ...state, role: action.payload };
    case 'SET_USER_ID':
      localStorage.setItem('pairup_userId', action.payload);
      return { ...state, userId: action.payload };
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

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}
