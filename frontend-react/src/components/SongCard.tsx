export type SongProps = {spotify_id: string, name: string, artist: string, similarity_score: number, explanation: string}

function SongCard({ name, artist, similarity_score, explanation }: SongProps) {
  return (<div>
    <h1>{name}</h1>
    <h2>{artist}</h2>
    <h2>{similarity_score}</h2>
    <h2>{explanation}</h2>
  </div>)
}

export default SongCard