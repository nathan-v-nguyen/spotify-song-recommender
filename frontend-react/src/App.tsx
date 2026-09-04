import { useState } from 'react';
import Heading from "./components/Heading"
import ModeToggle, {type Mode} from "./components/ModeToggle"
import SearchForm from "./components/SearchForm"
import ResultsList from "./components/ResultsList"
import SongCard, { type SongProps } from "./components/SongCard"

const fakeSongs: SongProps[] = [
  { spotify_id: "1", name: "Holocene", artist: "Bon Iver", similarityScore: 0.87, explanation: "Slow tempo, warm tone" },
  { spotify_id: "2", name: "Skinny Love", artist: "Bon Iver", similarityScore: 0.81, explanation: "Sparse, reflective" },
];


function App() {
  const [mode, setMode] = useState<Mode>("mood");
  return (
    <>
      <Heading title={"Moodify"} />
      <ModeToggle mode = {mode} setMode={setMode} />
      <SearchForm mode = {mode}></SearchForm>
      <ResultsList songs={fakeSongs}></ResultsList>
    </>
    
  )
}

export default App
