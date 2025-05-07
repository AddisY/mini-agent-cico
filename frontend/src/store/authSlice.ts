import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { AuthState, LoginCredentials, RegisterData } from '../types';
import * as api from '../services/api';

const initialState: AuthState = {
    user: null,
    token: localStorage.getItem('token'),
    isLoading: false,
    error: null,
};

export const login = createAsyncThunk(
    'auth/login',
    async (credentials: LoginCredentials, { rejectWithValue }) => {
        try {
            const response = await api.login(credentials);
            const token = response.access;
            
            // Set token in localStorage and axios defaults immediately
            localStorage.setItem('token', token);
            api.setAuthToken(token);
            
            // Get user data
            try {
                const user = await api.getCurrentUser();
                return { token, user };
            } catch (error: any) {
                // If user data fetch fails, remove token and throw error
                localStorage.removeItem('token');
                api.removeAuthToken();
                throw error;
            }
        } catch (error: any) {
            // Remove any existing token on login failure
            localStorage.removeItem('token');
            api.removeAuthToken();
            // Use the custom error message from the backend
            return rejectWithValue(error?.response?.data?.detail || 'Incorrect email or password');
        }
    }
);

export const register = createAsyncThunk(
    'auth/register',
    async (data: RegisterData, { rejectWithValue }) => {
        try {
            await api.register(data);
            return true;
        } catch (error: any) {
            return rejectWithValue(error?.response?.data?.detail || 'Registration failed');
        }
    }
);

export const logout = createAsyncThunk(
    'auth/logout',
    async () => {
        localStorage.removeItem('token');
        api.removeAuthToken();
        return true;
    }
);

export const getCurrentUser = createAsyncThunk(
    'auth/getCurrentUser',
    async (_, { rejectWithValue }) => {
        try {
            return await api.getCurrentUser();
        } catch (error: any) {
            return rejectWithValue(error?.response?.data?.detail || 'Failed to get user data');
        }
    }
);

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        clearError: (state) => {
            state.error = null;
        }
    },
    extraReducers: (builder) => {
        builder
            // Login
            .addCase(login.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(login.fulfilled, (state, action) => {
                state.isLoading = false;
                state.error = null;
                state.user = action.payload.user;
                state.token = action.payload.token;
            })
            .addCase(login.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string || 'Login failed';
                state.user = null;
                state.token = null;
            })
            // Register
            .addCase(register.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(register.fulfilled, (state) => {
                state.isLoading = false;
                state.error = null;
            })
            .addCase(register.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string || 'Registration failed';
            })
            // Logout
            .addCase(logout.fulfilled, (state) => {
                state.user = null;
                state.token = null;
                state.error = null;
            })
            // Get Current User
            .addCase(getCurrentUser.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(getCurrentUser.fulfilled, (state, action) => {
                state.isLoading = false;
                state.error = null;
                state.user = action.payload;
            })
            .addCase(getCurrentUser.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string || 'Failed to get user data';
                state.user = null;
                state.token = null;
            });
    },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer; 