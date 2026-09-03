export type SongProps = {spotify_id: string, name: string, artist: string, similarityScore: number, explanation: string}

function SongCard({ name, artist, similarityScore, explanation }: SongProps) {
  return (<div>
    <h1>{name}</h1>
    <h2>{artist}</h2>
    <h2>{similarityScore}</h2>
    <h2>{explanation}</h2>
  </div>)
}

export default SongCard