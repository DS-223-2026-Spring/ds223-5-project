import React from 'react';
import FormField from './FormField';
import { NICHES, FORMATS, INDUSTRIES, SIZES, BUDGETS } from '../constants';

export default function FilterPanel({ role, filters, setFilters, onReset }) {
  const isBrand = role === 'brand';

  return (
    <div>
      <div style={{ fontSize: '15px', fontWeight: '700', marginBottom: '4px' }}>
        Filter {isBrand ? 'creators' : 'brands'}
      </div>
      <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginBottom: '16px' }}>
        Narrow down your perfect match
      </div>

      {isBrand ? (
        <>
          <FormField label="CREATOR NICHE" type="select" options={NICHES} 
            value={filters.niche || ''} onChange={v => setFilters({...filters, niche: v})} />
          <FormField label="CREATOR LOCATION" 
            value={filters.location || ''} onChange={v => setFilters({...filters, location: v})} placeholder="e.g. New York" />
          <FormField label="MIN ENGAGEMENT RATE" type="slider" min="0" max="10" step="0.1" suffix="%"
            value={filters.min_engagement || 0} onChange={v => setFilters({...filters, min_engagement: v})} />
          <FormField label="MAX FOLLOWERS" type="slider" min="5000" max="100000" step="1000"
            value={filters.max_followers || 100000} onChange={v => setFilters({...filters, max_followers: v})} />
          <FormField label="MIN MATCH SCORE" type="slider" min="0" max="100" step="1" suffix="%"
            value={filters.min_match_score || 0} onChange={v => setFilters({...filters, min_match_score: v})} />
          <FormField label="CONTENT FORMAT" type="select" options={FORMATS}
            value={filters.format || ''} onChange={v => setFilters({...filters, format: v})} />
        </>
      ) : (
        <>
          <FormField label="BRAND INDUSTRY" type="select" options={INDUSTRIES} 
            value={filters.industry || ''} onChange={v => setFilters({...filters, industry: v})} />
          <FormField label="COMPANY SIZE" type="select" options={SIZES} 
            value={filters.size || ''} onChange={v => setFilters({...filters, size: v})} />
          <FormField label="BRAND LOCATION"
            value={filters.location || ''} onChange={v => setFilters({...filters, location: v})} placeholder="e.g. San Francisco" />
          <FormField label="MIN BUDGET" type="slider" min="0" max="50000" step="500" suffix="$"
            value={filters.budget_min || 0} onChange={v => setFilters({...filters, budget_min: v})} />
          <FormField label="MAX BUDGET" type="slider" min="0" max="50000" step="500" suffix="$"
            value={filters.budget_max || 50000} onChange={v => setFilters({...filters, budget_max: v})} />
          <FormField label="PREFERRED NICHE" type="select" options={NICHES}
            value={filters.preferred_niche || ''} onChange={v => setFilters({...filters, preferred_niche: v})} />
          <FormField label="MIN MATCH SCORE" type="slider" min="0" max="100" step="1" suffix="%"
            value={filters.min_match_score || 0} onChange={v => setFilters({...filters, min_match_score: v})} />
        </>
      )}

      <button className="stButton-secondary" style={{ width: '100%', marginTop: '8px' }} onClick={onReset}>
        Reset filters
      </button>
    </div>
  );
}
