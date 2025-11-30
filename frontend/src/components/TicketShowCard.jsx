import { Link } from 'react-router-dom';

const TICKET_URL = 'https://shop.comedyuo.com';

function formatDate(value) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';

  return new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date);
}

export default function TicketShowCard({ show }) {
  const formattedDate = formatDate(show.start_time);

  return (
    <article className="ticket-card">
      <div className="ticket-card-content">
        <header className="ticket-card-header">
          <h3 className="ticket-card-title">{show.title}</h3>
          <p className="ticket-card-date">{formattedDate}</p>
          <p className="ticket-card-location">{show.location}</p>
        </header>

        {show.description && (
          <p className="ticket-card-description">{show.description}</p>
        )}

        <div className="ticket-card-actions">
          <a
            href={TICKET_URL}
            target="_blank"
            rel="noreferrer"
            className="btn btn-ticket-primary"
          >
            Buy Tickets
          </a>
          <Link to={`/shows/${show.id}`} className="btn btn-ticket-secondary">
            View Details
          </Link>
        </div>
      </div>
    </article>
  );
}

