import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from '../components/Layout';
import AgentDashboard from '../pages/AgentDashboard';
import TransactionHistory from '../pages/TransactionHistory';
import MakeTransaction from '../pages/MakeTransaction';
import Profile from '../pages/Profile';
import Login from '../pages/Login';
import Register from '../pages/Register';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

const AppRoutes: React.FC = () => {
    const { token, user } = useSelector((state: RootState) => state.auth);
    const isAuthenticated = !!token;

    if (!isAuthenticated) {
        return (
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
        );
    }

    return (
        <Layout>
            <Routes>
                <Route path="/dashboard" element={<AgentDashboard />} />
                <Route path="/transactions" element={<TransactionHistory />} />
                <Route path="/make-transaction" element={<MakeTransaction />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/logout" element={<Navigate to="/login" />} />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </Layout>
    );
};

export default AppRoutes; 