import styles from "./ModeToggle.module.css"

type Mode = "mood" | "track";

function ModeToggle ({ mode }: { mode:Mode }) {
  return (
    <div>
      <button className = {mode === "mood" ? styles.active : ""}>Mood</button>
      <button className = {mode === "track" ? styles.active : ""}>Track</button>
    </div>
  );
}

export default ModeToggle
