import React, { useState, useEffect } from 'react'

function App() {
  const [data1, setData1] = useState([])
  useEffect(() => {
    fetch('/api')
      .then(res => res.json())
      .then(data => {
        setData1(data)
        console.log(data)
      })
  },[])
  return (
    <div>

    </div>
  )
}

export default App