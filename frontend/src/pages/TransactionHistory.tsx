import React, { useState, useEffect } from 'react';
import {
    Container,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Box,
    TablePagination,
    CircularProgress,
} from '@mui/material';
import { Transaction } from '../types';
import * as api from '../services/api';

const TransactionHistory: React.FC = () => {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [totalCount, setTotalCount] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchTransactions = async () => {
        try {
            setIsLoading(true);
            const response = await api.getTransactions(page + 1, rowsPerPage);
            setTransactions(response.results);
            setTotalCount(response.count);
        } catch (err) {
            setError('Failed to fetch transactions');
            console.error('Error fetching transactions:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchTransactions();
    }, [page, rowsPerPage]);

    const handleChangePage = (event: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    if (isLoading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
                <Typography color="error">{error}</Typography>
            </Box>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography 
                variant="h6" 
                sx={{ 
                    fontSize: '1.3rem',
                    mb: 3
                }}
            >
                Transaction History
            </Typography>
            <Paper sx={{ width: '100%', overflow: 'hidden' }}>
                <TableContainer>
                    <Table stickyHeader>
                        <TableHead>
                            <TableRow>
                                <TableCell>Transaction ID</TableCell>
                                <TableCell>Type</TableCell>
                                <TableCell>Amount</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Commission</TableCell>
                                <TableCell>Date</TableCell>
                                <TableCell>Provider</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {transactions.map((transaction) => (
                                <TableRow key={transaction.transaction_id}>
                                    <TableCell>{transaction.transaction_id}</TableCell>
                                    <TableCell>{transaction.transaction_type}</TableCell>
                                    <TableCell>ETB {parseFloat(transaction.amount).toFixed(2)}</TableCell>
                                    <TableCell>
                                        <Box
                                            component="span"
                                            sx={{
                                                color: transaction.status === 'SUCCESSFUL' 
                                                    ? 'success.main' 
                                                    : transaction.status === 'FAILED'
                                                    ? 'error.main'
                                                    : 'warning.main',
                                            }}
                                        >
                                            {transaction.status}
                                        </Box>
                                    </TableCell>
                                    <TableCell>ETB {parseFloat(transaction.commission_amount).toFixed(2)}</TableCell>
                                    <TableCell>
                                        {new Date(transaction.created_at).toLocaleDateString()}
                                    </TableCell>
                                    <TableCell>{transaction.provider_name}</TableCell>
                                </TableRow>
                            ))}
                            {transactions.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={7} align="center">
                                        No transactions found
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
                <TablePagination
                    rowsPerPageOptions={[5, 10, 25, 50]}
                    component="div"
                    count={totalCount}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                />
            </Paper>
        </Container>
    );
};

export default TransactionHistory; 