import React, { useEffect, useState } from 'react';
import {
    Container,
    Grid,
    Paper,
    Typography,
    Box,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Card,
    CardContent,
    IconButton,
    Tooltip,
    CircularProgress,
    Divider,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
} from '@mui/material';
import {
    AccountBalance as AccountBalanceIcon,
    Assessment as AssessmentIcon,
    Upload as UploadIcon,
    Refresh as RefreshIcon,
    TrendingUp as TrendingUpIcon,
    AttachMoney as AttachMoneyIcon,
    History as HistoryIcon,
    SwapHoriz as SwapHorizIcon,
    Dashboard as DashboardIcon,
    Person as PersonIcon,
    Logout as LogoutIcon,
} from '@mui/icons-material';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { Agent, AgentDocument, TransactionStats, Transaction } from '../types';
import * as api from '../services/api';
import { useNavigate } from 'react-router-dom';

const Sidebar: React.FC = () => {
    const navigate = useNavigate();
    
    return (
        <Box sx={{ width: 240, flexShrink: 0, zIndex: 10000 }}>
            <List>
                <ListItem disablePadding>
                    <ListItemButton onClick={() => navigate('/dashboard')}>
                        <ListItemIcon>
                            <DashboardIcon />
                        </ListItemIcon>
                        <ListItemText primary="Dashboard" />
                    </ListItemButton>
                </ListItem>
                
                <ListItem disablePadding>
                    <ListItemButton onClick={() => navigate('/transactions')}>
                        <ListItemIcon>
                            <HistoryIcon />
                        </ListItemIcon>
                        <ListItemText primary="Transaction History" />
                    </ListItemButton>
                </ListItem>

                <ListItem disablePadding>
                    <ListItemButton onClick={() => navigate('/make-transaction')}>
                        <ListItemIcon>
                            <SwapHorizIcon />
                        </ListItemIcon>
                        <ListItemText primary="Make Transaction" />
                    </ListItemButton>
                </ListItem>

                <ListItem disablePadding>
                    <ListItemButton onClick={() => navigate('/profile')}>
                        <ListItemIcon>
                            <PersonIcon />
                        </ListItemIcon>
                        <ListItemText primary="Profile" />
                    </ListItemButton>
                </ListItem>

                <ListItem disablePadding>
                    <ListItemButton onClick={() => navigate('/logout')}>
                        <ListItemIcon>
                            <LogoutIcon />
                        </ListItemIcon>
                        <ListItemText primary="Logout" />
                    </ListItemButton>
                </ListItem>
            </List>
        </Box>
    );
};

const AgentDashboard: React.FC = () => {
    const [agentData, setAgentData] = useState<Agent | null>(null);
    const [walletBalance, setWalletBalance] = useState<string>('0.00');
    const [transactionStats, setTransactionStats] = useState<TransactionStats | null>(null);
    const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useSelector((state: RootState) => state.auth);
    const navigate = useNavigate();

    const fetchData = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const [agentResponse, walletResponse, statsResponse, transactionsResponse] = await Promise.all([
                api.getAgentProfile(),
                api.getWalletBalance(),
                api.getTransactionStats(),
                api.getRecentTransactions(5)
            ]);
            setAgentData(agentResponse);
            setWalletBalance(walletResponse.balance);
            setTransactionStats(statsResponse);
            setRecentTransactions(transactionsResponse.results);
        } catch (err) {
            setError('Failed to fetch data');
            console.error('Error fetching data:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleDocumentUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file || !agentData) return;

        const formData = new FormData();
        formData.append('document_file', file);
        formData.append('document_type', 'BUSINESS_LICENSE'); // You can make this dynamic
        formData.append('agent', agentData.id.toString());

        try {
            await api.uploadDocument(agentData.id, formData);
            fetchData(); // Refresh data to show new document
        } catch (err) {
            setError('Failed to upload document');
        }
    };

    const handleRefresh = () => {
        fetchData();
    };

    if (isLoading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
                <CircularProgress />
            </Box>
        );
    }

    if (error || !agentData) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
                <Typography color="error">{error || 'No agent data available'}</Typography>
            </Box>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Grid container spacing={3}>
                {/* Welcome Message */}
                <Grid item xs={12}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="h6" sx={{ fontSize: '1.11rem' }} gutterBottom>
                            Welcome, {user?.first_name ? user.first_name.charAt(0).toUpperCase() + user.first_name.slice(1) : user?.username}!
                        </Typography>
                        <Button
                            startIcon={<RefreshIcon />}
                            onClick={handleRefresh}
                            variant="outlined"
                            sx={{ minWidth: '120px' }}
                        >
                            Refresh
                        </Button>
                    </Box>
                </Grid>

                {/* Key Metrics */}
                <Grid item xs={12} md={4}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent>
                            <Box display="flex" alignItems="center" minHeight={100}>
                                <AccountBalanceIcon 
                                    sx={{ fontSize: 40 }}
                                    className="card-icon"
                                />
                                <Box>
                                    <Typography color="textSecondary" gutterBottom>
                                        Float Balance
                                    </Typography>
                                    <Typography variant="h5">
                                        ETB {parseFloat(walletBalance).toFixed(2)}
                                    </Typography>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent>
                            <Box display="flex" alignItems="center" minHeight={100}>
                                <TrendingUpIcon 
                                    sx={{ fontSize: 40 }}
                                    className="card-icon"
                                />
                                <Box>
                                    <Typography color="textSecondary" gutterBottom>
                                        Total Transactions
                                    </Typography>
                                    <Typography variant="h5">
                                        {transactionStats?.successful_transactions || 0}
                                    </Typography>
                                    <Typography variant="body2" color="textSecondary">
                                        Amount: ETB {parseFloat(transactionStats?.successful_amount || '0').toFixed(2)}
                                    </Typography>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent>
                            <Box display="flex" alignItems="center" minHeight={100}>
                                <AttachMoneyIcon 
                                    sx={{ fontSize: 40 }}
                                    className="card-icon"
                                />
                                <Box>
                                    <Typography color="textSecondary" gutterBottom>
                                        Commission Earned
                                    </Typography>
                                    <Typography variant="h5">
                                        ETB {parseFloat(transactionStats?.total_commission_earned || '0').toFixed(2)}
                                    </Typography>
                                    <Typography variant="body2" color="textSecondary">
                                        Rate: {(agentData?.commission_rate * 100).toFixed(1)}%
                                    </Typography>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Business Information */}
                <Grid item xs={12}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Business Information
                        </Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                                <Typography variant="body1">
                                    <strong>Business Name:</strong> {agentData.business_name}
                                </Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Typography variant="body1">
                                    <strong>Business Address:</strong> {agentData.business_address}
                                </Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Typography variant="body1">
                                    <strong>Agent ID:</strong> {agentData.agent_id}
                                </Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Typography variant="body1">
                                    <strong>Status:</strong>{' '}
                                    <Box
                                        component="span"
                                        sx={{
                                            color: agentData.status === 'ACTIVE' ? 'success.main' : 'error.main',
                                        }}
                                    >
                                        {agentData.status}
                                    </Box>
                                </Typography>
                            </Grid>
                        </Grid>
                    </Paper>
                </Grid>

                {/* Transaction Stats */}
                <Grid item xs={12}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={2}>
                                <TrendingUpIcon fontSize="large" color="primary" />
                                <Typography variant="h6" component="div" ml={1}>
                                    Transaction Statistics
                                </Typography>
                            </Box>
                            <Grid container spacing={2}>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper elevation={0} sx={{ p: 2, textAlign: 'center' }}>
                                        <Typography variant="subtitle1" color="textSecondary">
                                            Total Transactions
                                        </Typography>
                                        <Typography variant="h5">
                                            {transactionStats?.total_transactions || 0}
                                        </Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper elevation={0} sx={{ p: 2, textAlign: 'center' }}>
                                        <Typography variant="subtitle1" color="textSecondary">
                                            Successful
                                        </Typography>
                                        <Typography variant="h5" color="success.main">
                                            {transactionStats?.successful_transactions || 0}
                                        </Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper elevation={0} sx={{ p: 2, textAlign: 'center' }}>
                                        <Typography variant="subtitle1" color="textSecondary">
                                            Failed
                                        </Typography>
                                        <Typography variant="h5" color="error.main">
                                            {transactionStats?.failed_transactions || 0}
                                        </Typography>
                                    </Paper>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Paper elevation={0} sx={{ p: 2, textAlign: 'center' }}>
                                        <Typography variant="subtitle1" color="textSecondary">
                                            Pending
                                        </Typography>
                                        <Typography variant="h5" color="warning.main">
                                            {transactionStats?.pending_transactions || 0}
                                        </Typography>
                                    </Paper>
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Recent Transactions */}
                <Grid item xs={12}>
                    <Paper sx={{ p: 3 }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                            <Typography variant="h6">
                                Recent Transactions
                            </Typography>
                            <Button
                                color="primary"
                                onClick={() => navigate('/transactions')}
                                endIcon={<HistoryIcon />}
                                variant="outlined"
                            >
                                View All
                            </Button>
                        </Box>
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Transaction ID</TableCell>
                                        <TableCell>Type</TableCell>
                                        <TableCell>Amount</TableCell>
                                        <TableCell>Status</TableCell>
                                        <TableCell>Commission</TableCell>
                                        <TableCell>Date</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {recentTransactions.slice(0, 5).map((transaction) => (
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
                                        </TableRow>
                                    ))}
                                    {recentTransactions.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={6} align="center">
                                                No recent transactions
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                </Grid>

                {/* Documents Section */}
                <Grid item xs={12}>
                    <Paper sx={{ p: 3 }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                            <Typography variant="h6">Documents</Typography>
                            <Button
                                variant="contained"
                                startIcon={<UploadIcon />}
                                component="label"
                            >
                                Upload Document
                                <input
                                    type="file"
                                    hidden
                                    onChange={handleDocumentUpload}
                                    accept=".pdf,.jpg,.jpeg,.png"
                                />
                            </Button>
                        </Box>
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Type</TableCell>
                                        <TableCell>Document Number</TableCell>
                                        <TableCell>Status</TableCell>
                                        <TableCell>Uploaded Date</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {agentData.documents.map((doc: AgentDocument) => (
                                        <TableRow key={doc.id}>
                                            <TableCell>{doc.document_type}</TableCell>
                                            <TableCell>{doc.document_number}</TableCell>
                                            <TableCell>
                                                <Box
                                                    component="span"
                                                    sx={{
                                                        color: doc.is_verified ? 'success.main' : 'warning.main',
                                                    }}
                                                >
                                                    {doc.is_verified ? 'Verified' : 'Pending'}
                                                </Box>
                                            </TableCell>
                                            <TableCell>
                                                {new Date(doc.uploaded_at).toLocaleDateString()}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                    {agentData.documents.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={4} align="center">
                                                No documents uploaded yet
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default AgentDashboard; 