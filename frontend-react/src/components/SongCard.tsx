import styles from './SongCard.module.css';

export type SongProps = {
  spotify_id: string;
  name: string;
  artist: string;
  album: string | null;
  similarity_score: number;
  explanation: string | null;
};

type SongCardProps = SongProps & { index: number };

function SongCard({
  spotify_id,
  name,
  artist,
  album,
  similarity_score,
  explanation,
  index,
}: SongCardProps) {
  const percent = Math.min(100, Math.round(similarity_score * 100));

  return (
    // --i drives the staggered entrance; --pct drives the meter width. Passing
    // them as custom properties keeps the animation itself in the stylesheet.
    <li className={styles.row} style={{ '--i': index, '--pct': `${percent}%` } as React.CSSProperties}>
      <span className={styles.rank}>{String(index + 1).padStart(2, '0')}</span>

      <div>
        <h3 className={styles.name}>{name}</h3>
        <p className={styles.artist}>{artist}</p>

        <div className={styles.meter}>
          <div
            className={styles.track}
            role="meter"
            aria-valuenow={percent}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Similarity ${percent} percent`}
          >
            <div className={styles.fill} />
          </div>
          <span className={styles.score}>{percent}%</span>
        </div>

        {explanation && <p className={styles.note}>{explanation}</p>}

        <div className={styles.reveal}>
          <div className={styles.revealInner}>
            <span className={styles.album}>{album ?? ''}</span>
            <a
              className={styles.link}
              href={`https://open.spotify.com/track/${spotify_id}`}
              target="_blank"
              rel="noreferrer"
            >
              Open in Spotify &rarr;
            </a>
          </div>
        </div>
      </div>
    </li>
  );
}

export default SongCard;
