import { Link } from 'react-router-dom';

function formatDate(value) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';

  return new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date);
}

export default function ShowCard({ show }) {
  const isPast = show.status === 'past';

  return (
    <article className="show-card">
      <div className="show-card-main">
        <header className="show-card-header">
          <p className="show-date">{formatDate(show.start_time)}</p>
          <h3 className="show-title">{show.title}</h3>
        </header>

        <p className="show-location">
          <span className="show-location-label">Where</span>
          <span className="show-location-value">{show.location}</span>
        </p>

        {show.description && (
          <p className="show-description">{show.description}</p>
        )}
      </div>

      <footer className="show-card-footer">
        <span
          className={`status-pill status-${show.status}`}
          aria-label={`Show status: ${show.status}`}
        >
          {isPast ? 'Past show' : 'Upcoming'}
        </span>

        <Link className="btn btn-outline" to={`/shows/${show.id}`}>
          View details
        </Link>
      </footer>
    </article>
  );
}