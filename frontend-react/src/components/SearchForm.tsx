import { useState, useEffect } from 'react';
import styles from "./SearchForm.module.css"
import { type Mode } from './ModeToggle';

type SearchFormProps = { mode: Mode, onSearch: (query:string) => void, error: string | null, isLoading: boolean };
type TrackSuggestion = { spotify_id: string; name: string; artist: string; album: string | null };

function SearchForm ({ mode, onSearch, error, isLoading }: SearchFormProps){
  const [query, setQuery] = useState<string>("");
  const [suggestions, setSuggestions] = useState<TrackSuggestion[]>([]);
  const [selectedTrackId, setSelectedTrackId] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setValidationError(null);

    if (mode === "track" && selectedTrackId === "") {
      setValidationError(suggestions.length > 0 ? "Please choose from the dropdown" : "Song not found");
      return;
    }

    if (mode === "track") {
      onSearch(selectedTrackId);
    } else {
      onSearch(query);
    }
    setQuery("");
    setSelectedTrackId("")
  }

  function handleSelectSuggestion(track: TrackSuggestion) {
    setQuery(`${track.name} — ${track.artist}`);
    setSelectedTrackId(track.spotify_id);
    setSuggestions([]);
    setValidationError(null);
  }

  
  useEffect(() => {
    if (mode !== "track" || query.trim() === "") {
      setSuggestions([]);
      return;
    }


    const timeoutId = setTimeout(async () => {
      try {
        const response = await fetch(`http://localhost:8000/search/tracks?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
          setSuggestions([]);
          return;
        } 
        const data = await response.json();
        setSuggestions(data.results);
      } catch {
        setSuggestions([])
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, mode]);

  return (
    <form 
      className = {styles.form}
      onSubmit={handleSubmit}>
      <input type="text" placeholder={mode==="mood" ? "Describe how you're feeling or what you're doing...": "Search for a song..."}
      value={query}
      onChange={(e) => {
        setQuery(e.target.value);
        setValidationError(null);
      }}/>
      {isLoading && <p>Loading...</p>}
      {validationError && <p>{validationError}</p>}
      
      <button type="submit" disabled={isLoading}>Find Music</button>
      {error && <p>{error}</p>}
      {mode === "track" && suggestions.length > 0 && (
        <ul>
          {suggestions.map((track) => (
            <li key={track.spotify_id} onClick={() => handleSelectSuggestion(track)}>
              {track.name} — {track.artist}
            </li>
          ))}
        </ul>
      )}
    </form>
  )
}

export default SearchForm