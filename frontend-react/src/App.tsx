import { useState } from 'react';
import styles from './App.module.css';
import Heading from './components/Heading';
import ModeToggle, { type Mode } from './components/ModeToggle';
import SearchForm from './components/SearchForm';
import ResultsList from './components/ResultsList';
import { type SongProps } from './components/SongCard';

const API_BASE = 'http://localhost:8000';

function App() {
  const [mode, setMode] = useState<Mode>('mood');
  const [songs, setSongs] = useState<SongProps[]>([]);
  const [strategy, setStrategy] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(query: string) {
    const endpoint = mode === 'mood' ? 'mood' : 'track';
    const url = `${API_BASE}/recommend/${endpoint}`;
    const body = mode === 'mood' ? { mood_string: query } : { spotify_id: query };
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': import.meta.env.VITE_API_KEY },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        setError('Something went wrong. Try again.');
        return;
      }
      const data = await response.json();
      setSongs(data.recommendations);
      setStrategy(data.strategy);
      setHasSearched(true);
    } catch {
      setError("Couldn't reach the server. Is it running?");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <Heading title="Moodify" />

      <section className={styles.console}>
        <ModeToggle mode={mode} setMode={setMode} />
        <SearchForm mode={mode} onSearch={handleSearch} error={error} isLoading={isLoading} />
      </section>

      <ResultsList
        songs={songs}
        strategy={strategy}
        isLoading={isLoading}
        hasSearched={hasSearched}
      />
    </div>
  );
}

export default App;
