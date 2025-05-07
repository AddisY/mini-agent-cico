import axios, { AxiosError } from 'axios';
import { LoginCredentials, RegisterData, AgentRegistrationData, User } from '../types';

const API_URL = 'http://localhost:8000/api';
const WALLET_SERVICE_URL = 'http://localhost:8002/api';
const TRANSACTION_SERVICE_URL = 'http://localhost:8001/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

// Token management functions
export const setAuthToken = (token: string) => {
    if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        localStorage.setItem('token', token);
    }
};

export const removeAuthToken = () => {
    delete api.defaults.headers.common['Authorization'];
    localStorage.removeItem('token');
};

// Initialize token from localStorage
const token = localStorage.getItem('token');
if (token) {
    setAuthToken(token);
}

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        // Handle rate limiting errors
        if (error.response?.status === 429) {
            const errorData = error.response.data as { detail?: string };
            const customError = new Error(errorData?.detail || 'Too many attempts. Please try again in a few minutes.');
            customError.name = 'RateLimitError';
            const retryAfter = error.response.headers['retry-after'];
            if (retryAfter) {
                (customError as any).retryAfter = parseInt(retryAfter);
            }
            return Promise.reject(customError);
        }

        // Handle authentication errors
        if (error.response?.status === 401) {
            // Only remove token and redirect for actual auth failures
            // Don't redirect on login page or token refresh attempts
            const isLoginRequest = error.config?.url?.includes('/token/');
            if (!isLoginRequest) {
                removeAuthToken();
                // Use window.location.pathname to check current route
                if (!window.location.pathname.includes('/login')) {
                    window.location.href = '/login';
                }
            }
        }
        return Promise.reject(error);
    }
);

// Auth API calls
export const login = async (credentials: LoginCredentials) => {
    try {
        // Check if we're in a rate-limited state
        const rateLimitKey = 'login_rate_limit';
        const rateLimitData = localStorage.getItem(rateLimitKey);
        if (rateLimitData) {
            const { expiresAt } = JSON.parse(rateLimitData);
            if (Date.now() < expiresAt) {
                throw new Error('Too many login attempts. Please try again later.');
            } else {
                localStorage.removeItem(rateLimitKey);
            }
        }

        console.log('Attempting login with:', { email: credentials.email });
        const response = await api.post('/token/', credentials);
        console.log('Login response:', response.data);
        const { access } = response.data;
        setAuthToken(access);
        // Clear any rate limit data on successful login
        localStorage.removeItem(rateLimitKey);
        return response.data;
    } catch (error: any) {
        console.error('Login error:', error.response?.data || error.message);
        removeAuthToken();

        // Handle rate limiting
        if (error.response?.status === 429) {
            const retryAfter = error.response.headers['retry-after'] || '300'; // Default to 5 minutes
            const expiresAt = Date.now() + (parseInt(retryAfter) * 1000);
            localStorage.setItem('login_rate_limit', JSON.stringify({
                expiresAt,
                retryAfter: parseInt(retryAfter)
            }));
        }

        throw error;
    }
};

export const register = async (data: RegisterData) => {
    const response = await api.post('/users/register/', data);
    return response.data;
};

export const registerAgent = async (data: AgentRegistrationData) => {
    const response = await api.post('/agents/', data);
    return response.data;
};

export const verifyEmail = async (email: string) => {
    const response = await api.post('/users/verify_email/', { email });
    return response.data;
};

export const resetPassword = async (email: string) => {
    const response = await api.post('/users/reset_password/', { email });
    return response.data;
};

// User API calls
export const getCurrentUser = async (): Promise<User> => {
    const response = await api.get('/users/me/');
    return response.data;
};

export const updateUser = async (id: number, data: Partial<RegisterData>) => {
    const response = await api.patch(`/users/${id}/`, data);
    return response.data;
};

// Agent API calls
export const getAgentProfile = async () => {
    const response = await api.get('/agents/me/');
    return response.data;
};

export const updateAgentProfile = async (id: number, data: Partial<AgentRegistrationData>) => {
    const response = await api.patch(`/agents/${id}/`, data);
    return response.data;
};

export const uploadDocument = async (agentId: number, data: FormData) => {
    const response = await api.post('/documents/', data);
    return response.data;
};

// Admin API calls
export const getAllUsers = async () => {
    const response = await api.get('/users/');
    return response.data;
};

export const getAllAgents = async () => {
    const response = await api.get('/agents/');
    return response.data;
};

export const verifyUser = async (id: number) => {
    const response = await api.post(`/users/${id}/verify/`);
    return response.data;
};

export const activateAgent = async (id: number) => {
    const response = await api.post(`/agents/${id}/activate/`);
    return response.data;
};

export const suspendAgent = async (id: number) => {
    const response = await api.post(`/agents/${id}/suspend/`);
    return response.data;
};

export const verifyDocument = async (id: number) => {
    const response = await api.post(`/documents/${id}/verify_document/`);
    return response.data;
};

// Field validation
export const validateField = async (field: 'email' | 'username', value: string) => {
    try {
        console.log(`Validating ${field} with value:`, value);
        const response = await api.post('/validate-field/', { field, value });
        console.log(`Validation response for ${field}:`, response.data);
        return null; // Field is valid
    } catch (error: any) {
        console.log(`Validation error for ${field}:`, error.response?.data);
        if (error.response?.status === 400 && error.response?.data?.error) {
            throw error.response.data.error;
        }
        throw error;
    }
};

// Wallet API calls
export const getWalletBalance = async () => {
    const response = await axios.get(`${WALLET_SERVICE_URL}/wallets/balance/`, {
        headers: {
            'Authorization': api.defaults.headers.common['Authorization']
        }
    });
    return response.data;
};

// Transaction API calls
export const getTransactionStats = async () => {
    const response = await axios.get(`${TRANSACTION_SERVICE_URL}/transactions/stats/`, {
        headers: {
            'Authorization': api.defaults.headers.common['Authorization']
        }
    });
    return response.data;
};

export const getTransactions = async (page: number = 1, limit: number = 10) => {
    const response = await axios.get(`${TRANSACTION_SERVICE_URL}/transactions/?page=${page}&limit=${limit}`, {
        headers: {
            'Authorization': api.defaults.headers.common['Authorization']
        }
    });
    return response.data;
};

export const getRecentTransactions = async (limit: number = 5) => {
    const response = await axios.get(`${TRANSACTION_SERVICE_URL}/transactions/?limit=${limit}`, {
        headers: {
            'Authorization': api.defaults.headers.common['Authorization']
        }
    });
    return response.data;
};

type CreateTransactionData = {
    transaction_type: string;
    amount: string;
    customer_identifier: string;
} & (
    | { wallet_provider: string; bank_provider?: never }
    | { bank_provider: string; wallet_provider?: never }
);

export const createTransaction = async (data: CreateTransactionData) => {
    const response = await axios.post(`${TRANSACTION_SERVICE_URL}/transactions/`, data, {
        headers: {
            'Authorization': api.defaults.headers.common['Authorization']
        }
    });
    return response.data;
};

export default api; 