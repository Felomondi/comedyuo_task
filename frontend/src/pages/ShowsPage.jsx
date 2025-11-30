import { useEffect, useState } from 'react';

import { fetchShows } from '../api.js';
import Filters from '../components/Filters.jsx';
import ShowCard from '../components/ShowCard.jsx';

export default function ShowsPage() {
  const [filter, setFilter] = useState('upcoming');
  const [shows, setShows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError('');
      try {
        const data = await fetchShows(filter);
        if (!cancelled) {
          setShows(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err?.message || 'Something went wrong while loading shows.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [filter]);

  const hasShows = shows.length > 0;

  return (
    <div className="page shows-page">
      <header className="page-header">
        <div>
          {/* Logo at the top */}
          <img
            src="https://cuo-email-photos.s3.us-east-1.amazonaws.com/cuo-white-logo.png"
            alt="ComedyUO logo"
            className="cuo-logo"
          />

          <p className="brand-title">COMEDYUO</p>
          <h1>Show calendar</h1>
          <p className="page-subtitle">
            Browse upcoming residencies or revisit past pop ups.
          </p>
        </div>

        <div className="page-filters">
          <Filters active={filter} onChange={setFilter} />
        </div>
      </header>

      {loading && (
        <section className="state state-loading">
          <p>Loading shows…</p>
        </section>
      )}

      {!loading && error && (
        <section className="state state-error">
          <p className="error">
            {error}
          </p>
        </section>
      )}

      {!loading && !error && (
        <section className="show-list-section">
          {hasShows ? (
            <div className="show-list">
              {shows.map((show) => (
                <ShowCard key={show.id} show={show} />
              ))}
            </div>
          ) : (
            <div className="state state-empty">
              <h2>No shows for this filter</h2>
              <p>
                Try switching between upcoming and past shows. New dates will appear here as they are announced.
              </p>
            </div>
          )}
        </section>
      )}
    </div>
  );
}