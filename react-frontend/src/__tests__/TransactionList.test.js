import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App'; 

describe('TransactionList Component', () => {
    const mockTxns = [
        { hash: '0x123', gasUsed: 21000, timeStamp: 1622548800 },
        { hash: '0x456', gasUsed: 30000, timeStamp: 1622548900 },
    ];

    test('renders transaction table with data', () => {
        render(<App txns={mockTxns} />); 

        expect(screen.getByText(/Txn Hash/i)).toBeInTheDocument();
        expect(screen.getByText(/0x123/i)).toBeInTheDocument();
        expect(screen.getByText(/0x456/i)).toBeInTheDocument();
    });

    test('displays correct fee and timestamp', () => {
        render(<App txns={mockTxns} />);

        expect(screen.getByText(/21000/i)).toBeInTheDocument();
        expect(screen.getByText(/6\/1\/2021, 8:00:00 AM/i)).toBeInTheDocument();
    });
});