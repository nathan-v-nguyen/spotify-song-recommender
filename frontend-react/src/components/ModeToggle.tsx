import styles from './ModeToggle.module.css';

export type Mode = 'mood' | 'track';
type ModeToggleProps = { mode: Mode; setMode: (m: Mode) => void };

const OPTIONS: { value: Mode; title: string; hint: string }[] = [
  { value: 'mood', title: 'Mood', hint: 'describe a feeling' },
  { value: 'track', title: 'Track', hint: 'name a song' },
];

function ModeToggle({ mode, setMode }: ModeToggleProps) {
  return (
    <div className={styles.toggle} data-mode={mode} role="group" aria-label="Search mode">
      <span className={styles.thumb} aria-hidden="true" />
      {OPTIONS.map((option) => (
        <button
          key={option.value}
          type="button"
          aria-pressed={mode === option.value}
          className={`${styles.option} ${mode === option.value ? styles.active : ''}`}
          onClick={() => setMode(option.value)}
        >
          {option.title}
          <span className={styles.label}>{option.hint}</span>
        </button>
      ))}
    </div>
  );
}

export default ModeToggle;
