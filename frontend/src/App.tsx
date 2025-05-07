import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ToastContainer } from 'react-toastify';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import 'react-toastify/dist/ReactToastify.css';
import AppRoutes from './routes';
import { RootState, useAppDispatch } from './store';
import { getCurrentUser } from './store/authSlice';
import * as api from './services/api';
import theme from './theme';

import Login from './pages/Login';
import Register from './pages/Register';
import AgentDashboard from './pages/AgentDashboard';
import Profile from './pages/Profile';
import Layout from './components/Layout';

const LoadingScreen = () => (
    <Box
        sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh',
            backgroundColor: '#fff'
        }}
    >
        <CircularProgress size={60} />
    </Box>
);

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { token, isLoading } = useSelector((state: RootState) => state.auth);
    
    if (isLoading) return <LoadingScreen />;
    return token ? <Layout>{children}</Layout> : <Navigate to="/login" />;
};

const AgentRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { user, token, isLoading } = useSelector((state: RootState) => state.auth);
    
    if (isLoading) return <LoadingScreen />;
    if (!token) return <Navigate to="/login" />;
    if (user?.role !== 'AGENT') return <Navigate to="/dashboard" />;
    return <Layout>{children}</Layout>;
};

const AppContent: React.FC = () => {
    const dispatch = useAppDispatch();
    const { token, user, isLoading } = useSelector((state: RootState) => state.auth);
    const [isInitialized, setIsInitialized] = useState(false);
    
    useEffect(() => {
        const initializeAuth = async () => {
            try {
                if (token) {
                    // Set the token in axios defaults
                    api.setAuthToken(token);
                    if (!user) {
                        const resultAction = await dispatch(getCurrentUser());
                        if (getCurrentUser.fulfilled.match(resultAction)) {
                            // User data fetched successfully
                        }
                    }
                }
            } catch (error) {
                console.error('Failed to initialize auth:', error);
            } finally {
                setIsInitialized(true);
            }
        };
        
        initializeAuth();
    }, [dispatch, token, user]);

    if (!isInitialized || isLoading) {
        return <LoadingScreen />;
    }

    return (
        <>
            <AppRoutes />
            <ToastContainer position="top-right" autoClose={3000} />
        </>
    );
};

const App: React.FC = () => {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Router>
                <AppContent />
            </Router>
        </ThemeProvider>
    );
};

export default App; 