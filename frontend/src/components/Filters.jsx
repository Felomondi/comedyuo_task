const FILTERS = [
  { value: 'upcoming', label: 'Upcoming' },
  { value: 'past', label: 'Past' },
  { value: 'all', label: 'All' },
];

export default function Filters({ active, onChange }) {
  return (
    <div className="filters">
      {FILTERS.map((filter) => (
        <button
          key={filter.value}
          className={`filters-chip ${filter.value === active ? 'is-active' : ''}`}
          onClick={() => onChange(filter.value)}
          type="button"
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}