import React, { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [txns, setTxns] = useState([])
  const [ethPrice, setEthPrice] = useState(null)

  useEffect(() => {
    axios.get('/api/txns')
      .then(res => setTxns(res.data.result))
      .catch(err => console.error(err));

    axios.get('/api/eth-now')
      .then(res => setEthPrice(res.data.price))
      .catch(err => console.error(err));
  },[])
  return (
    <div>

    </div>
  )
}

export default App