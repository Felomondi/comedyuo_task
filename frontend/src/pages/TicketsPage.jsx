import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { fetchShows } from '../api.js';
import TicketShowCard from '../components/TicketShowCard.jsx';

export default function TicketsPage() {
  const [shows, setShows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError('');
      try {
        // Only fetch upcoming shows for tickets page
        const data = await fetchShows('upcoming');
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
  }, []);

  return (
    <div className="page tickets-page">
      {/* Hero Section */}
      <section className="tickets-hero">
        <img
          src="https://cuo-email-photos.s3.us-east-1.amazonaws.com/cuo-white-logo.png"
          alt="ComedyUO logo"
          className="tickets-logo"
        />
        <h1 className="tickets-hero-title">Get Your Tickets</h1>
        <p className="tickets-hero-subtitle">
          Don't miss out on the best comedy shows in town. Secure your spot for an unforgettable night of laughs.
        </p>
      </section>

      {/* Loading State */}
      {loading && (
        <section className="state state-loading">
          <p>Loading upcoming shows…</p>
        </section>
      )}

      {/* Error State */}
      {!loading && error && (
        <section className="state state-error">
          <p className="error">{error}</p>
        </section>
      )}

      {/* Shows Grid */}
      {!loading && !error && (
        <section className="tickets-shows-section">
          {shows.length > 0 ? (
            <>
              <h2 className="tickets-section-title">Upcoming Shows</h2>
              <div className="tickets-grid">
                {shows.map((show) => (
                  <TicketShowCard key={show.id} show={show} />
                ))}
              </div>
            </>
          ) : (
            <div className="state state-empty">
              <h2>No upcoming shows at the moment</h2>
              <p>
                Check back soon for new dates, or{' '}
                <a
                  href="https://app.comedyuo.com/waitlist"
                  target="_blank"
                  rel="noreferrer"
                  className="link"
                >
                  join the waitlist
                </a>{' '}
                to be notified when tickets go on sale.
              </p>
              <Link to="/" className="btn btn-outline" style={{ marginTop: '1rem' }}>
                View All Shows
              </Link>
            </div>
          )}
        </section>
      )}

      {/* Footer CTA */}
      {!loading && !error && shows.length > 0 && (
        <section className="tickets-footer-cta">
          <p className="tickets-footer-text">
            Want to see past shows or browse the full calendar?{' '}
            <Link to="/" className="link">
              View all shows
            </Link>
          </p>
        </section>
      )}
    </div>
  );
}

