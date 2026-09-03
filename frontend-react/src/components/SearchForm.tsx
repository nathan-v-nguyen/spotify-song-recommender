import styles from "./SearchForm.module.css"

function searchForm (){
  return (
    <form className = {styles.form}>
      <input type="text" placeholder="Describe how you're feeling or what you're doing..."/>
      <button type="submit">Find Music</button>
    </form>
  )
}

export default searchForm