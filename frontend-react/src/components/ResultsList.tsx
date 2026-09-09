import styles from './ResultsList.module.css';
import SongCard, { type SongProps } from './SongCard';

type ResultsListProps = {
  songs: SongProps[];
  strategy: string | null;
  isLoading: boolean;
  hasSearched: boolean;
};

const SKELETON_ROWS = [0, 1, 2, 3, 4];

function ResultsList({ songs, strategy, isLoading, hasSearched }: ResultsListProps) {
  if (isLoading) {
    return (
      <section className={styles.section}>
        <div className={styles.header}>
          <span>Tracklist</span>
          <span className={styles.meta}>Searching</span>
        </div>
        <div className={styles.panel}>
          {SKELETON_ROWS.map((i) => (
            <div
              key={i}
              className={styles.skeletonRow}
              style={{ '--i': i } as React.CSSProperties}
            >
              <div className={`${styles.bar} ${styles.barRank}`} />
              <div className={`${styles.bar} ${styles.barTitle}`} />
              <div className={`${styles.bar} ${styles.barMeter}`} />
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (songs.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>
          {hasSearched ? 'Nothing came back' : 'Your tracklist is empty'}
        </p>
        <p className={styles.emptyBody}>
          {hasSearched
            ? 'Try a different mood, or pick another song to match against.'
            : 'Search a mood or a song above and ten recommendations will land here.'}
        </p>
      </div>
    );
  }

  return (
    <section className={styles.section}>
      <div className={styles.header}>
        <span>Tracklist</span>
        <span className={styles.meta}>
          {songs.length} tracks{strategy ? ` · ${strategy.replace(/_/g, ' ')}` : ''}
        </span>
      </div>
      <ol className={styles.panel}>
        {songs.map((song, index) => (
          <SongCard key={song.spotify_id} index={index} {...song} />
        ))}
      </ol>
    </section>
  );
}

export default ResultsList;
