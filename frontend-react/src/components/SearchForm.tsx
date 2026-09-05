import { useState } from 'react';
import styles from "./SearchForm.module.css"
import { type Mode } from "./ModeToggle"

type SearchFormProps = { mode: Mode, onSearch: (mode:Mode, query:string) => void };

function SearchForm ({ mode, onSearch }: SearchFormProps){
  const [query, setQuery] = useState<string>("");

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    onSearch(mode, query);
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