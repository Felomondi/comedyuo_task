import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import { fetchShow, sendEmail } from '../api.js';

const initialForm = { guest_name: '', guest_email: '', message: '' };

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

export default function ShowDetail() {
  const { id } = useParams();
  const [show, setShow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(initialForm);
  const [statusMsg, setStatusMsg] = useState('');
  const [statusType, setStatusType] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchShow(id);
        if (!cancelled) {
          setShow(data);
        }
      } catch (err) {
        if (!cancelled) {
          setStatusMsg(err.message || 'Could not load show.');
          setStatusType('error');
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
  }, [id]);

  const onChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setSending(true);
    setStatusMsg('');
    setStatusType('');
    try {
      await sendEmail({ show_id: Number(id), ...form });
      setStatusMsg('Email sent! Check the guest inbox for details.');
      setStatusType('success');
      setForm(initialForm);
    } catch (err) {
      setStatusMsg(err.message || 'Failed to send email.');
      setStatusType('error');
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="page page-detail">
        <p>Loading…</p>
      </div>
    );
  }

  if (!show) {
    return (
      <div className="page page-detail">
        <p>Show not found.</p>
        <Link to="/" className="btn ghost">
          Back to shows
        </Link>
      </div>
    );
  }

  const isPast = show.status === 'past';

  return (
    <div className="page page-detail">
      <Link to="/" className="link-button">
        ← Back to shows
      </Link>

      <section className="detail-card">
        <p className="eyebrow detail-status">
          {isPast ? 'Past show' : 'Upcoming show'}
        </p>
        <h1 className="detail-title">{show.title}</h1>
        <p className="detail-date">{formatDate(show.start_time)}</p>
        <p className="detail-location">{show.location}</p>
        <p className="detail-description">{show.description}</p>
      </section>

      <section className="detail-sidebar">
        <form className="email-form" onSubmit={onSubmit}>
          <h2 className="email-form-title">Email the show details</h2>
          <p className="email-form-subtitle">
            Send a confirmation email with this show information to a guest inbox.
          </p>

          <label className="field">
            <span className="field-label">Guest name</span>
            <input
              name="guest_name"
              value={form.guest_name}
              onChange={onChange}
              required
            />
          </label>

          <label className="field">
            <span className="field-label">Guest email</span>
            <input
              type="email"
              name="guest_email"
              value={form.guest_email}
              onChange={onChange}
              required
            />
          </label>

          <label className="field">
            <span className="field-label">Message (optional)</span>
            <textarea
              name="message"
              rows="4"
              placeholder="Share preferences or questions for ComedyUO"
              value={form.message}
              onChange={onChange}
            />
          </label>

          <button className="btn" disabled={sending}>
            {sending ? 'Sending…' : 'Send email'}
          </button>

          {statusMsg && (
            <p className={statusType === 'error' ? 'status status-error' : 'status status-success'}>
              {statusMsg}
            </p>
          )}
        </form>
      </section>
    </div>
  );
}