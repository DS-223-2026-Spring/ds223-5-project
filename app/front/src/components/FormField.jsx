import React from 'react';

export default function FormField({ 
  label, type = 'text', value, onChange, placeholder, options = [], suffix, min, max, step 
}) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <label className="form-lbl">{label}</label>
      
      {type === 'select' ? (
        <select value={value} onChange={e => onChange(e.target.value)}>
          <option value="" disabled>Select...</option>
          {options.map(o => <option key={o} value={o}>{o}</option>)}
        </select>
      ) : type === 'textarea' ? (
        <textarea 
          value={value} 
          onChange={e => onChange(e.target.value)} 
          placeholder={placeholder} 
          rows={4}
        />
      ) : type === 'number' && suffix ? (
        <div className="input-with-suffix">
          <input 
            type="number" 
            value={value} 
            onChange={e => onChange(e.target.value)} 
            placeholder={placeholder}
            min={min} max={max} step={step}
          />
          <div className="suffix">{suffix}</div>
        </div>
      ) : type === 'slider' ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <input 
            type="range" 
            value={value} 
            onChange={e => onChange(e.target.value)} 
            min={min} max={max} step={step}
            style={{ flex: 1, cursor: 'pointer' }}
          />
          <span style={{ fontSize: '13px', fontWeight: '600' }}>{value}{suffix}</span>
        </div>
      ) : (
        <input 
          type={type} 
          value={value} 
          onChange={e => onChange(e.target.value)} 
          placeholder={placeholder}
          min={min} max={max} step={step}
        />
      )}
    </div>
  );
}
