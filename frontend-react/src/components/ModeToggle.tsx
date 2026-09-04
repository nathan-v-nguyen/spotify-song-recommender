import styles from "./ModeToggle.module.css"

export type Mode = "mood" | "track";
type ModeToggleProps = {mode: Mode; setMode: (m: Mode) => void};

function ModeToggle ({ mode, setMode}: ModeToggleProps) {
  return (
    <div>
      <button className = {mode === "mood" ? styles.active : ""}
      onClick={() => setMode("mood")}
      >Mood</button>
      <button className = {mode === "track" ? styles.active : ""}
      onClick={() => setMode("track")}>Track</button>
    </div>
  );
}

export default ModeToggle
