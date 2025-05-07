import React, { useState, FormEvent, useEffect } from 'react';
import { useNavigate, Link as RouterLink, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
    Container,
    Paper,
    Typography,
    TextField,
    Button,
    Box,
    CircularProgress,
    Alert,
    Fade,
} from '@mui/material';
import { login } from '../store/authSlice';
import { RootState, AppDispatch } from '../store';
import { LoginCredentials, LoginFormData } from '../types';
import KifiyaLogo from '../assets/images/kifiya-logo.png';

const Login: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const dispatch = useDispatch<AppDispatch>();
    const { isLoading, error: authError } = useSelector((state: RootState) => state.auth);
    const [formData, setFormData] = useState<LoginFormData>({
        email: '',
        password: '',
    });
    const [errors, setErrors] = useState<Partial<LoginFormData>>({});
    const [loginError, setLoginError] = useState<string | null>(null);
    const [showSuccessMessage, setShowSuccessMessage] = useState(false);
    const [timeLeft, setTimeLeft] = useState<number | null>(null);

    useEffect(() => {
        // Check if user was redirected from registration
        const justRegistered = location.state?.from === 'register';
        if (justRegistered) {
            setShowSuccessMessage(true);
            // Clear the success message after 5 seconds
            const timer = setTimeout(() => {
                setShowSuccessMessage(false);
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [location]);

    useEffect(() => {
        // Check for rate limit on component mount
        const rateLimitData = localStorage.getItem('login_rate_limit');
        if (rateLimitData) {
            const { expiresAt } = JSON.parse(rateLimitData);
            const remaining = Math.ceil((expiresAt - Date.now()) / 1000);
            if (remaining > 0) {
                setTimeLeft(remaining);
            } else {
                localStorage.removeItem('login_rate_limit');
            }
        }

        // Set up countdown timer if needed
        if (timeLeft !== null && timeLeft > 0) {
            const intervalId = setInterval(() => {
                setTimeLeft(current => {
                    if (current === null || current <= 1) {
                        clearInterval(intervalId);
                        localStorage.removeItem('login_rate_limit');
                        return null;
                    }
                    return current - 1;
                });
            }, 1000);

            return () => clearInterval(intervalId);
        }
    }, [timeLeft]);

    const validateForm = () => {
        const newErrors: Partial<LoginFormData> = {};
        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Invalid email address';
        }
        if (!formData.password) {
            newErrors.password = 'Password is required';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        setLoginError(null);
        setErrors(prev => ({ ...prev, [name]: '' }));
    };

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        // Check if we're rate limited
        const rateLimitData = localStorage.getItem('login_rate_limit');
        if (rateLimitData) {
            const { expiresAt } = JSON.parse(rateLimitData);
            if (Date.now() < expiresAt) {
                const remaining = Math.ceil((expiresAt - Date.now()) / 1000);
                setTimeLeft(remaining);
                setLoginError(`Too many login attempts. Please try again in ${Math.ceil(remaining / 60)} minutes.`);
                return;
            } else {
                localStorage.removeItem('login_rate_limit');
            }
        }

        try {
            setLoginError(null);
            const credentials: LoginCredentials = {
                email: formData.email,
                password: formData.password
            };
            const result = await dispatch(login(credentials)).unwrap();
            if (result?.user && result?.token) {
                navigate('/dashboard');
            }
        } catch (err: any) {
            if (err.name === 'RateLimitError') {
                // Update the countdown timer
                const rateLimitData = localStorage.getItem('login_rate_limit');
                if (rateLimitData) {
                    const { expiresAt } = JSON.parse(rateLimitData);
                    const remaining = Math.ceil((expiresAt - Date.now()) / 1000);
                    setTimeLeft(remaining);
                    setLoginError(`Too many login attempts. Please try again in ${Math.ceil(remaining / 60)} minutes.`);
                } else {
                    setLoginError('Too many login attempts. Please try again later.');
                }
            } else {
                setLoginError(err.message || 'Login failed. Please check your credentials and try again.');
            }
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <Box
                sx={{
                    marginTop: 4,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
            >
                <Box sx={{ mb: 0.25, display: 'flex', justifyContent: 'center' }}>
                    <img
                        src={KifiyaLogo}
                        alt="Kifiya Logo"
                        style={{
                            height: '80px',
                            width: 'auto',
                            objectFit: 'contain'
                        }}
                    />
                </Box>
                <Paper
                    elevation={3}
                    sx={{
                        p: 4,
                        width: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                    }}
                >
                    <Typography component="h1" variant="h5" align="center">
                        Sign in
                    </Typography>
                    
                    {showSuccessMessage && (
                        <Fade in={showSuccessMessage}>
                            <Alert 
                                severity="success" 
                                sx={{ 
                                    mt: 2, 
                                    mb: 2,
                                    backgroundColor: '#e8f5e9',
                                    color: '#1b5e20',
                                    '& .MuiAlert-icon': {
                                        color: '#2e7d32'
                                    },
                                    border: '1px solid #a5d6a7',
                                    borderRadius: '8px',
                                }}
                            >
                                Registration successful! Please sign in with your credentials.
                            </Alert>
                        </Fade>
                    )}

                    <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="email"
                            label="Email Address"
                            name="email"
                            autoComplete="email"
                            autoFocus
                            value={formData.email}
                            onChange={handleChange}
                            error={Boolean(errors.email)}
                            helperText={errors.email}
                            disabled={isLoading}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="password"
                            label="Password"
                            type="password"
                            id="password"
                            autoComplete="current-password"
                            value={formData.password}
                            onChange={handleChange}
                            error={Boolean(errors.password)}
                            helperText={errors.password}
                            disabled={isLoading}
                        />
                        {(loginError || authError) && (
                            <Alert severity="error" sx={{ mt: 2 }}>
                                {loginError || authError}
                            </Alert>
                        )}
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2 }}
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <CircularProgress size={24} color="inherit" />
                            ) : (
                                'Sign In'
                            )}
                        </Button>
                        <Box sx={{ mt: 2, textAlign: 'center' }}>
                            <RouterLink
                                to="/forgot-password"
                                style={{ 
                                    display: 'block', 
                                    marginBottom: '8px', 
                                    textDecoration: 'none'
                                }}
                                className="forgot-password-link"
                            >
                                <Box 
                                    component="span" 
                                    sx={{ 
                                        color: '#ffa033',
                                        '&:hover': {
                                            color: '#ff8a00'
                                        }
                                    }}
                                >
                                    Forgot password?
                                </Box>
                            </RouterLink>
                            <Box sx={{ display: 'inline' }}>
                                Don't have an account?{' '}
                                <RouterLink
                                    to="/register"
                                    style={{ 
                                        textDecoration: 'underline',
                                        color: '#ff8a00',
                                        transition: 'color 0.2s',
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.color = '#ffb866';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.color = '#ff8a00';
                                    }}
                                >
                                    Sign Up
                                </RouterLink>
                            </Box>
                        </Box>
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default Login; 