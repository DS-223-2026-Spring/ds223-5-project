import React, { useState, useEffect, useContext } from 'react';
import { AppContext } from '../context/AppContext';
import { getInfluencers, getBrands } from '../api';
import FilterPanel from '../components/FilterPanel';
import CreatorCard from '../components/CreatorCard';
import BrandCard from '../components/BrandCard';

export default function DiscoverPage() {
  const { state } = useContext(AppContext);
  const isBrand = state.role === 'brand';
  const [results, setResults] = useState([]);
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const fetchResults = async () => {
      setLoading(true);
      const params = isBrand ? { ...filters, brand_id: state.userId } : { ...filters, influencer_id: state.userId };
      const data = isBrand ? await getInfluencers(params) : await getBrands(params);
      if (active) {
        setResults(data);
        setLoading(false);
      }
    };
    fetchResults();
    return () => { active = false; };
  }, [filters, isBrand]);

  return (
    <div style={{ display: 'flex', gap: '24px', padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ flex: '0 0 280px' }}>
        <FilterPanel role={state.role} filters={filters} setFilters={setFilters} onReset={() => setFilters({})} />
      </div>

      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <div>
            <div style={{ fontSize: '20px', fontWeight: '700' }}>
              {isBrand ? 'Matched creators' : 'Brands seeking creators'}
            </div>
            <div style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>
              {results.length} results
            </div>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-muted)' }}>Loading...</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {results.map(r => isBrand ? (
              <CreatorCard key={r.id} influencer={r} />
            ) : (
              <BrandCard key={r.id} brand={r} />
            ))}
            {results.length === 0 && (
              <div style={{ gridColumn: '1 / -1', padding: '40px', textAlign: 'center', background: '#fff', borderRadius: '12px', border: '1px solid var(--color-border)' }}>
                No results found. Try clearing your filters.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
