import styles from './Heading.module.css';

type HeadingProps = { title: string };

const Heading = ({ title }: HeadingProps) => {
  return (
    <header className={styles.header}>
      <p className={styles.kicker}>Mood &rarr; Music</p>
      <h1 className={styles.wordmark}>
        {title}
        <span className={styles.dot} aria-hidden="true" />
      </h1>
      <p className={styles.tagline}>
        Describe a feeling or name a song you love. Get ten tracks back &mdash; and{' '}
        <em>the reason each one fits</em>.
      </p>
    </header>
  );
};

export default Heading;
