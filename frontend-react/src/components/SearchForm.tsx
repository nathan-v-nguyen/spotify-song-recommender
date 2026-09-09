import { useState, useEffect } from 'react';
import styles from './SearchForm.module.css';
import { type Mode } from './ModeToggle';

type SearchFormProps = {
  mode: Mode;
  onSearch: (query: string) => void;
  error: string | null;
  isLoading: boolean;
};
type TrackSuggestion = { spotify_id: string; name: string; artist: string; album: string | null };

const PLACEHOLDER: Record<Mode, string> = {
  mood: "Describe how you're feeling or what you're doing...",
  track: 'Search for a song you already love...',
};

function SearchForm({ mode, onSearch, error, isLoading }: SearchFormProps) {
  const [query, setQuery] = useState<string>('');
  const [suggestions, setSuggestions] = useState<TrackSuggestion[]>([]);
  const [selectedTrackId, setSelectedTrackId] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setValidationError(null);

    if (mode === 'track' && selectedTrackId === '') {
      setValidationError(
        showSuggestions ? 'Please choose from the dropdown' : 'Song not found',
      );
      return;
    }

    if (mode === 'track') {
      onSearch(selectedTrackId);
    } else {
      onSearch(query);
    }
    setQuery('');
    setSelectedTrackId('');
  }

  function handleSelectSuggestion(track: TrackSuggestion) {
    setQuery(`${track.name} — ${track.artist}`);
    setSelectedTrackId(track.spotify_id);
    setValidationError(null);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setQuery(e.target.value);
    // Editing the text invalidates any track picked earlier — otherwise the form
    // would still submit the old spotify_id while showing different text.
    setSelectedTrackId('');
    setValidationError(null);
  }

  // A non-empty selectedTrackId means the text in the box *is* an already-chosen
  // track, so there is nothing to look up. Deciding visibility here at render
  // time rather than clearing state inside the effect keeps the effect to a
  // single job — fetching — and avoids a cascading re-render.
  const showSuggestions =
    mode === 'track' && selectedTrackId === '' && query.trim() !== '' && suggestions.length > 0;

  useEffect(() => {
    if (mode !== 'track' || query.trim() === '' || selectedTrackId !== '') return;

    const timeoutId = setTimeout(async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/search/tracks?q=${encodeURIComponent(query)}`,
        );
        if (!response.ok) {
          setSuggestions([]);
          return;
        }
        const data = await response.json();
        setSuggestions(data.results);
      } catch {
        setSuggestions([]);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, mode, selectedTrackId]);

  const message = validationError ?? error;

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.fieldWrap}>
        <div className={styles.field}>
          <input
            type="text"
            className={styles.input}
            placeholder={PLACEHOLDER[mode]}
            value={query}
            onChange={handleChange}
            aria-label={mode === 'mood' ? 'Describe your mood' : 'Search for a song'}
          />
          <button type="submit" className={styles.submit} disabled={isLoading}>
            {isLoading && <span className={styles.spinner} aria-hidden="true" />}
            {isLoading ? 'Finding' : 'Find Music'}
          </button>
        </div>

        {showSuggestions && (
          <ul className={styles.suggestions}>
            {suggestions.map((track) => (
              <li key={track.spotify_id}>
                <button
                  type="button"
                  className={styles.suggestion}
                  onClick={() => handleSelectSuggestion(track)}
                >
                  <span className={styles.suggestionName}>{track.name}</span>
                  <span className={styles.suggestionArtist}>{track.artist}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <p className={styles.status} role="status">
        {message ? (
          <span className={styles.error}>{message}</span>
        ) : (
          <span className={styles.hint}>
            {mode === 'mood'
              ? 'e.g. "late night drive, feeling nostalgic"'
              : 'Type a song name, then pick a match from the list.'}
          </span>
        )}
      </p>
    </form>
  );
}

export default SearchForm;
