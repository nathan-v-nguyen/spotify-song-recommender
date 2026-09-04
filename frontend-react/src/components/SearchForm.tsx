import { useState } from 'react';
import styles from "./SearchForm.module.css"
import { type Mode } from "./ModeToggle"

function SearchForm ({ mode }: { mode: Mode }){
  const [query, setQuery] = useState<string>("");

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    console.log(mode, query)
  }

  return (
    <form 
      className = {styles.form}
      onSubmit={handleSubmit}>
      <input type="text" placeholder="Describe how you're feeling or what you're doing..."
      value={query}
      onChange={(e) => setQuery(e.target.value)}/>
      <button type="submit">Find Music</button>
    </form>
  )
}

export default SearchForm