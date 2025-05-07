import React, { useState } from 'react';
import {
    Container,
    Paper,
    Typography,
    Box,
    Button,
    TextField,
    MenuItem,
    Grid,
    CircularProgress,
    Alert,
} from '@mui/material';
import * as api from '../services/api';

const WALLET_PROVIDERS = [
    { id: 'TELEBIRR', name: 'TeleBirr' },
    { id: 'MPESA', name: 'M-Pesa' },
];

const BANK_PROVIDERS = [
    { id: 'CBE', name: 'Commercial Bank of Ethiopia' },
    { id: 'DASHEN', name: 'Dashen Bank' },
    { id: 'AWASH', name: 'Awash Bank' },
    { id: 'ABYSSINIA', name: 'Bank of Abyssinia' },
    { id: 'WEGAGEN', name: 'Wegagen Bank' },
    { id: 'UNITED', name: 'United Bank' },
    { id: 'NIB', name: 'Nib International Bank' },
    { id: 'ZEMEN', name: 'Zemen Bank' },
    { id: 'OROMIA', name: 'Oromia International Bank' },
    { id: 'COOP', name: 'Cooperative Bank of Oromia' },
];

type TransactionType = 'WALLET_LOAD' | 'BANK_DEPOSIT' | 'BANK_WITHDRAWAL';

const MakeTransaction: React.FC = () => {
    const [transactionType, setTransactionType] = useState<TransactionType | ''>('');
    const [provider, setProvider] = useState('');
    const [amount, setAmount] = useState('');
    const [identifier, setIdentifier] = useState(''); // phone number or account number
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setIsLoading(true);

        try {
            const transactionData = {
                transaction_type: transactionType,
                amount: Number(amount).toFixed(2),
                customer_identifier: identifier,
                ...(transactionType === 'WALLET_LOAD' 
                    ? { wallet_provider: provider }
                    : { bank_provider: provider }
                )
            };

            const response = await api.createTransaction(transactionData);

            setSuccess('Transaction initiated successfully!');
            // Reset form
            setTransactionType('');
            setProvider('');
            setAmount('');
            setIdentifier('');
        } catch (err: any) {
            setError(err.response?.data?.non_field_errors?.[0] || err.response?.data?.error || 'Failed to create transaction');
        } finally {
            setIsLoading(false);
        }
    };

    const getProviderList = () => {
        if (transactionType === 'WALLET_LOAD') {
            return WALLET_PROVIDERS;
        }
        return BANK_PROVIDERS;
    };

    const getIdentifierLabel = () => {
        if (transactionType === 'WALLET_LOAD') {
            return 'Phone Number';
        }
        return 'Account Number';
    };

    const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        // Allow empty string or valid numbers
        if (value === '' || /^\d*\.?\d*$/.test(value)) {
            setAmount(value);
        }
    };

    return (
        <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
            <Typography 
                variant="h6" 
                sx={{ 
                    fontSize: '1.3rem',
                    mb: 3
                }}
            >
                Make Transaction
            </Typography>
            <Paper sx={{ p: 3 }}>
                <form onSubmit={handleSubmit}>
                    <Grid container spacing={3}>
                        <Grid item xs={12}>
                            <TextField
                                select
                                fullWidth
                                label="Transaction Type"
                                value={transactionType}
                                onChange={(e) => {
                                    setTransactionType(e.target.value as TransactionType);
                                    setProvider('');
                                    setIdentifier('');
                                }}
                                required
                            >
                                <MenuItem value="WALLET_LOAD">Load into Wallet</MenuItem>
                                <MenuItem value="BANK_DEPOSIT">Deposit into Bank</MenuItem>
                                <MenuItem value="BANK_WITHDRAWAL">Withdraw from Bank</MenuItem>
                            </TextField>
                        </Grid>

                        {transactionType && (
                            <>
                                <Grid item xs={12}>
                                    <TextField
                                        select
                                        fullWidth
                                        label="Provider"
                                        value={provider}
                                        onChange={(e) => setProvider(e.target.value)}
                                        required
                                    >
                                        {getProviderList().map((p) => (
                                            <MenuItem key={p.id} value={p.id}>
                                                {p.name}
                                            </MenuItem>
                                        ))}
                                    </TextField>
                                </Grid>

                                <Grid item xs={12}>
                                    <TextField
                                        fullWidth
                                        label={getIdentifierLabel()}
                                        value={identifier}
                                        onChange={(e) => setIdentifier(e.target.value)}
                                        required
                                    />
                                </Grid>

                                <Grid item xs={12}>
                                    <TextField
                                        fullWidth
                                        label="Amount (ETB)"
                                        type="text"
                                        value={amount}
                                        onChange={handleAmountChange}
                                        required
                                        inputProps={{
                                            inputMode: 'decimal',
                                            pattern: '\\d*\\.?\\d*'
                                        }}
                                    />
                                </Grid>

                                <Grid item xs={12}>
                                    <Button
                                        type="submit"
                                        variant="contained"
                                        size="large"
                                        fullWidth
                                        disabled={isLoading}
                                    >
                                        {isLoading ? (
                                            <CircularProgress size={24} />
                                        ) : (
                                            'Process Transaction'
                                        )}
                                    </Button>
                                </Grid>
                            </>
                        )}

                        {error && (
                            <Grid item xs={12}>
                                <Alert severity="error">{error}</Alert>
                            </Grid>
                        )}

                        {success && (
                            <Grid item xs={12}>
                                <Alert severity="success">{success}</Alert>
                            </Grid>
                        )}
                    </Grid>
                </form>
            </Paper>
        </Container>
    );
};

export default MakeTransaction; 