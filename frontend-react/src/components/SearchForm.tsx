import { useState } from 'react';
import styles from "./SearchForm.module.css"

type SearchFormProps = { onSearch: (query:string) => void, error: string | null, isLoading: boolean };

function SearchForm ({ onSearch, error, isLoading }: SearchFormProps){
  const [query, setQuery] = useState<string>("");

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    onSearch(query);
    setQuery("");
  }

  return (
    <form 
      className = {styles.form}
      onSubmit={handleSubmit}>
      <input type="text" placeholder="Describe how you're feeling or what you're doing..."
      value={query}
      onChange={(e) => setQuery(e.target.value)}/>
      {isLoading && <p>Loading...</p>}
      <button type="submit" disabled={isLoading}>Find Music</button>
      {error && <p>{error}</p>}
    </form>
  )
}

export default SearchForm