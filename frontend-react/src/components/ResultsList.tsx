import SongCard, { type SongProps } from "./SongCard"


type ResultsListProps = {songs: SongProps[]}

function ResultsList({songs}: ResultsListProps) { 
  return (
    <div>
      {songs.map((song) => (
        <SongCard key={song.spotify_id} {...song} />
      ))}
    </div>
  )
}

export default ResultsList