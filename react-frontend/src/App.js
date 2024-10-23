import React, { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [txns, setTxns] = useState([])
  const [ethPrice, setEthPrice] = useState(null)
  const [totalUSDT, setTotalUSDT] = useState(null)
  const [hash, setHash] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [totalTxns, setTotalTxns] = useState(0);

   // Handle fetching txns
   const fetchTransactions = async (page, pageSize) => {
    try {
      const res = await axios.get(`/api/txns`, {
        params: {
          hash: hash,
          startTime: startTime,
          endTime: endTime,
          page: page,
          pageSize: pageSize
        }
      });
      setTxns(JSON.parse(res.data.transactions));
      setTotalTxns(res.data.total);
    } catch (err) {
      console.error('Error fetching transactions:', err);
    }
  };

  // Fetch txns when component mounts/page changes
  useEffect(() => {
    fetchTransactions(page, pageSize);
  }, [page, pageSize]);

  useEffect(() => {
    axios.get('/api/eth-now')
      .then(res => setEthPrice(res.data.price))
      .catch(err => console.error(err));
    axios.get('/api/summary')
      .then(res => setTotalUSDT(res.data.totalusdt))
      .catch(err => console.error(err));
  },[])

  // Handle search form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    fetchTransactions(1, pageSize); // Start from pg 1 after search
  };

  // Pagination controls
  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const handlePageSizeChange = (e) => {
    setPageSize(e.target.value);
    setPage(1); // Reset to pg 1 when page size changes
  };

  return (
    <div>
      <h1>Dashboard for Uniswap WETH-USDC Transactions</h1>
      
      {/* Stats */}
      <div>
        <h2>Current ETH/USDT Price</h2>
        {ethPrice ? <p>{ethPrice}</p> : <p>Loading...</p>}
        <h2>Total Transaction Fee in USDT</h2>
        {totalUSDT ? <p>{totalUSDT}</p> : <p>Loading...</p>}
      </div>

      {/* Search Form */}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Transaction Hash: </label>
          <input
            type="text"
            value={hash}
            onChange={(e) => setHash(e.target.value)}
            placeholder="Enter transaction hash"
          />
        </div>
        <div>
          <label>Start Time: </label>
          <input
            type="datetime-local"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
          />
        </div>
        <div>
          <label>End Time: </label>
          <input
            type="datetime-local"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
          />
        </div>
        <button type="submit">Search</button>
      </form>

      {/* Transaction List */}
      <div>
        <h2>Transaction List</h2>
        <table id="table">
          <thead>
              <tr>
                  <th>S.No</th>
                  <th>Txn Hash</th>
                  <th>Fee</th>
                  <th>Timestamp</th>
              </tr>
          </thead>
          <tbody>
              {txns.map((txn, index) => (
                  <tr key={txn.hash}>
                      <td>{index + 1}</td> {/* S.No column */}
                      <td>{txn.hash}</td> {/* Txn Hash column */}
                      <td>{txn.fee_usdt}</td> {/* Fee column */}
                      <td>{new Date(txn.timestamp * 1000).toLocaleString()}</td> {/* Timestamp column */}
                  </tr>
              ))}
          </tbody>
        </table> 
      </div>

      {/* Pagination Controls */}
      <div>
        <label>Page Size: </label>
        <select value={pageSize} onChange={handlePageSizeChange}>
          <option value={10}>10</option>
          <option value={20}>20</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </select>

        <div>
          <button
            onClick={() => handlePageChange(page - 1)}
            disabled={page === 1}
          >
            Previous
          </button>
          <span> Page {page} </span>
          <button
            onClick={() => handlePageChange(page + 1)}
            disabled={page * pageSize >= totalTxns}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}

export default App