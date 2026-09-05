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

  async function handleSearch(mode:Mode, query:string) {
    const endpoint = mode === "mood" ? "mood" : "track";
    const url = `http://localhost:8000/recommend/${endpoint}`;
    const body = mode === "mood" ? { mood_string: query } : { spotify_id: query };
    const response = await fetch(url, { method: "POST", headers: {"Content-Type": "application/json", "X-API-Key": import.meta.env.VITE_API_KEY,}, body:JSON.stringify(body)});
    if (!response.ok) {
      console.error("Search failed:", response.status);
      return;
    }
    const data = await response.json();
    setSongs(data.recommendations);
  }

  return (
    <>
      <Heading title={"Moodify"} />
      <ModeToggle mode = {mode} setMode={setMode} />
      <SearchForm mode = {mode} onSearch={handleSearch}></SearchForm>
      <ResultsList songs={songs}></ResultsList>
    </>
    
  )
}

export default App
