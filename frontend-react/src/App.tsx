import { useState } from 'react';
import Heading from "./components/Heading"
import ModeToggle, {type Mode} from "./components/ModeToggle"
import SearchForm from "./components/SearchForm"
import ResultsList from "./components/ResultsList"
import { type SongProps } from "./components/SongCard"

const fakeSongs: SongProps[] = [
  { spotify_id: "1", name: "Holocene", artist: "Bon Iver", similarity_score: 0.87, explanation: "Slow tempo, warm tone" },
  { spotify_id: "2", name: "Skinny Love", artist: "Bon Iver", similarity_score: 0.81, explanation: "Sparse, reflective" },
];


function App() {
  const [mode, setMode] = useState<Mode>("mood");
  const [songs, setSongs] = useState<SongProps[]>(fakeSongs);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(query:string) {
    const endpoint = mode === "mood" ? "mood" : "track";
    const url = `http://localhost:8000/recommend/${endpoint}`;
    const body = mode === "mood" ? { mood_string: query } : { spotify_id: query };
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(url, { method: "POST", headers: {"Content-Type": "application/json", "X-API-Key": import.meta.env.VITE_API_KEY,}, body:JSON.stringify(body)});
      if (!response.ok) {
        setError("Something went wrong. Try again.");
        return;
      }
      const data = await response.json();
      setSongs(data.recommendations);
    } catch {
      setError("Couldn't reach the server. Is it running?");
    } finally {
      setIsLoading(false);
    }
    
  }

  return (
    <>
      <Heading title={"Moodify"} />
      <ModeToggle mode = {mode} setMode={setMode} />
      <SearchForm onSearch={handleSearch} error={error} isLoading={isLoading}></SearchForm>
      <ResultsList songs={songs}></ResultsList>
    </>
    
  )
}

export default App
