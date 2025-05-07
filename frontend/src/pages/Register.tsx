import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import { debounce } from 'lodash';
import {
    Container,
    Paper,
    Typography,
    TextField,
    Button,
    Box,
    Link,
    CircularProgress,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Stepper,
    Step,
    StepLabel,
    Alert,
    Grid,
} from '@mui/material';
import { register } from '../store/authSlice';
import { RootState, AppDispatch } from '../store';
import { RegisterData, AgentRegistrationData } from '../types';
import * as api from '../services/api';
import KifiyaLogo from '../assets/images/kifiya-logo.png';

// Simple validation state to prevent too many API calls
const validationState = {
    isCheckingEmail: false,
    isCheckingUsername: false,
    lastCheckedEmail: '',
    lastCheckedUsername: '',
    emailError: '',
    usernameError: '',
    isRateLimited: false
};

const validateField = debounce(async (
    field: 'email' | 'username',
    value: string,
    setFieldError: (field: string, message: string) => void
) => {
    // If we're rate limited, skip validation but don't show error
    if (validationState.isRateLimited) {
        return;
    }

    // Don't check if already checking or if value hasn't changed
    if (field === 'email') {
        if (validationState.isCheckingEmail || value === validationState.lastCheckedEmail) {
            return;
        }
        validationState.isCheckingEmail = true;
        validationState.lastCheckedEmail = value;
    } else {
        if (validationState.isCheckingUsername || value === validationState.lastCheckedUsername) {
            return;
        }
        validationState.isCheckingUsername = true;
        validationState.lastCheckedUsername = value;
    }

    try {
        await api.validateField(field, value);
        setFieldError(field, '');
    } catch (error: any) {
        // Handle rate limiting
        if (error?.response?.status === 429) {
            validationState.isRateLimited = true;
            // Don't show rate limit errors to user
            return;
        }

        // Only show "already taken" errors, not technical errors
        const errorMessage = field === 'email' ? 
            'This email is already registered' : 
            'This username is already taken';
        setFieldError(field, errorMessage);
    } finally {
        if (field === 'email') {
            validationState.isCheckingEmail = false;
        } else {
            validationState.isCheckingUsername = false;
        }
    }
}, 1000);

// Reset rate limit state periodically
setInterval(() => {
    validationState.isRateLimited = false;
}, 5000); // Check every 5 seconds

const userValidationSchema = Yup.object({
    email: Yup.string()
        .email('Invalid email address')
        .required('Email is required'),
    username: Yup.string()
        .min(3, 'Username must be at least 3 characters')
        .matches(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores')
        .required('Username is required'),
    first_name: Yup.string()
        .required('First name is required')
        .min(2, 'First name must be at least 2 characters'),
    last_name: Yup.string()
        .required('Last name is required')
        .min(2, 'Last name must be at least 2 characters'),
    phone_number: Yup.string()
        .matches(/^\+?\d{9,}$/, 'Phone number must contain at least 9 digits and may start with +')
        .required('Phone number is required'),
    password: Yup.string()
        .required('Password is required'),
    role: Yup.string()
        .oneOf(['AGENT', 'MERCHANT'], 'Please select a valid role')
        .required('Role is required'),
});

const agentValidationSchema = Yup.object({
    business_name: Yup.string()
        .min(3, 'Business name must be at least 3 characters')
        .required('Business name is required'),
    business_address: Yup.string()
        .min(5, 'Business address must be at least 5 characters')
        .required('Business address is required'),
});

const initialValues: RegisterData = {
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    role: 'AGENT'
};

const Register: React.FC = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch<AppDispatch>();
    const { isLoading, error } = useSelector((state: RootState) => state.auth);
    const [activeStep, setActiveStep] = useState(0);
    const [userFormData, setUserFormData] = useState<RegisterData | null>(null);
    const [registrationError, setRegistrationError] = useState<string | null>(null);

    const handleSubmit = async (values: RegisterData) => {
        try {
            setRegistrationError(null);
            if (values.role === 'MERCHANT') {
                await dispatch(register(values)).unwrap();
                navigate('/login', { state: { from: 'register' } });
            } else {
                setActiveStep(1);
                setUserFormData(values);
            }
        } catch (err: any) {
            setRegistrationError(err.message || 'Registration failed');
        }
    };

    const handleAgentSubmit = async (values: { business_name: string; business_address: string }, { setFieldError }: any) => {
        try {
            setRegistrationError(null);
            if (!userFormData) return;

            const agentData: AgentRegistrationData = {
                user: userFormData,
                business_name: values.business_name,
                business_address: values.business_address,
                commission_rate: 0.0,
            };

            await api.registerAgent(agentData);
            navigate('/login', { state: { from: 'register' } });
        } catch (err: any) {
            if (err.response?.data) {
                const backendErrors = err.response.data;
                Object.keys(backendErrors).forEach((field) => {
                    const fieldPath = field.startsWith('user.') ? field.split('.')[1] : field;
                    if (Array.isArray(backendErrors[field])) {
                        setFieldError(fieldPath, backendErrors[field][0]);
                    }
                });
            } else {
                setRegistrationError(err.message || 'Agent registration failed');
            }
        }
    };

    const handleBack = () => {
        setActiveStep(0);
        setRegistrationError(null);
    };

    return (
        <Container component="main" maxWidth="sm">
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
                        maxWidth: '600px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                    }}
                >
                    <Typography 
                        component="h1" 
                        variant="h5" 
                        align="center" 
                        gutterBottom
                        sx={{ width: '100%' }}
                    >
                        Sign up
                    </Typography>

                    <Stepper 
                        activeStep={activeStep} 
                        sx={{ 
                            width: '100%',
                            paddingLeft: '30px',
                            margin: '20px auto 16px',
                            '& .MuiStepLabel-root': {
                                flexDirection: 'row',
                                alignItems: 'center',
                                justifyContent: 'center'
                            },
                            '& .MuiStepLabel-labelContainer': {
                                textAlign: 'left',
                                marginLeft: 2
                            },
                            '& .MuiStepLabel-label': {
                                color: '#ff8a00',
                                '&.Mui-active': {
                                    color: '#ff8a00'
                                },
                                '&.Mui-completed': {
                                    color: '#ff8a00'
                                }
                            },
                            '& .MuiStep-root': {
                                flex: 1,
                                textAlign: 'center',
                                px: 1,
                                alignItems: 'center',
                                '& .MuiStepLabel-label': {
                                    marginRight: 3
                                }
                            },
                            '& .MuiStepLabel-iconContainer': {
                                paddingRight: 0,
                                display: 'flex',
                                alignItems: 'center',
                                height: '24px'
                            },
                            '& .MuiStepIcon-root': {
                                display: 'flex',
                                alignItems: 'center',
                                color: '#ffb866',
                                '&.Mui-active': {
                                    color: '#ff8a00'
                                },
                                '&.Mui-completed': {
                                    color: '#ff8a00'
                                },
                                '& .MuiStepIcon-text': {
                                    fill: '#fff'
                                }
                            },
                            '& .MuiStepConnector-root': {
                                marginLeft: -2,
                                marginRight: 2,
                                '& .MuiStepConnector-line': {
                                    borderColor: '#ffb866'
                                },
                                '&.Mui-active, &.Mui-completed': {
                                    '& .MuiStepConnector-line': {
                                        borderColor: '#ff8a00'
                                    }
                                }
                            }
                        }}
                    >
                        <Step>
                            <StepLabel>User Information</StepLabel>
                        </Step>
                        <Step>
                            <StepLabel>Business Information</StepLabel>
                        </Step>
                    </Stepper>

                    {registrationError && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {registrationError}
                        </Alert>
                    )}

                    <Box sx={{ mt: 2 }}>
                        {activeStep === 0 ? (
                            <Formik
                                initialValues={initialValues}
                                validationSchema={userValidationSchema}
                                onSubmit={handleSubmit}
                            >
                                {({
                                    values,
                                    errors,
                                    touched,
                                    handleChange,
                                    handleBlur,
                                    handleSubmit,
                                    setFieldError
                                }) => (
                                    <form onSubmit={handleSubmit}>
                                        <Grid container spacing={2}>
                                            <Grid item xs={12}>
                                                <TextField
                                                    fullWidth
                                                    id="email"
                                                    name="email"
                                                    label="Email Address"
                                                    value={values.email}
                                                    onChange={(e) => {
                                                        handleChange(e);
                                                        if (e.target.value.includes('@')) {
                                                            validateField('email', e.target.value, setFieldError);
                                                        }
                                                    }}
                                                    onBlur={handleBlur}
                                                    error={touched.email && Boolean(errors.email)}
                                                    helperText={touched.email && errors.email}
                                                />
                                            </Grid>
                                            <Grid item xs={12}>
                                                <TextField
                                                    fullWidth
                                                    id="username"
                                                    name="username"
                                                    label="Username"
                                                    value={values.username}
                                                    onChange={(e) => {
                                                        handleChange(e);
                                                        if (e.target.value.length >= 3) {
                                                            validateField('username', e.target.value, setFieldError);
                                                        }
                                                    }}
                                                    onBlur={handleBlur}
                                                    error={touched.username && Boolean(errors.username)}
                                                    helperText={touched.username && errors.username}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6}>
                                                <TextField
                                                    fullWidth
                                                    id="first_name"
                                                    name="first_name"
                                                    label="First Name"
                                                    value={values.first_name}
                                                    onChange={handleChange}
                                                    onBlur={handleBlur}
                                                    error={touched.first_name && Boolean(errors.first_name)}
                                                    helperText={touched.first_name && errors.first_name}
                                                />
                                            </Grid>
                                            <Grid item xs={12} sm={6}>
                                                <TextField
                                                    fullWidth
                                                    id="last_name"
                                                    name="last_name"
                                                    label="Last Name"
                                                    value={values.last_name}
                                                    onChange={handleChange}
                                                    onBlur={handleBlur}
                                                    error={touched.last_name && Boolean(errors.last_name)}
                                                    helperText={touched.last_name && errors.last_name}
                                                />
                                            </Grid>
                                            <Grid item xs={12}>
                                                <TextField
                                                    fullWidth
                                                    id="phone_number"
                                                    name="phone_number"
                                                    label="Phone Number"
                                                    placeholder="+251912345678"
                                                    value={values.phone_number}
                                                    onChange={handleChange}
                                                    onBlur={handleBlur}
                                                    error={touched.phone_number && Boolean(errors.phone_number)}
                                                    helperText={touched.phone_number && errors.phone_number}
                                                />
                                            </Grid>
                                            <Grid item xs={12}>
                                                <TextField
                                                    fullWidth
                                                    id="password"
                                                    name="password"
                                                    label="Password"
                                                    type="password"
                                                    value={values.password}
                                                    onChange={handleChange}
                                                    onBlur={handleBlur}
                                                    error={touched.password && Boolean(errors.password)}
                                                    helperText={touched.password && errors.password}
                                                />
                                            </Grid>
                                            <Grid item xs={12}>
                                                <FormControl fullWidth>
                                                    <InputLabel id="role-label">Role</InputLabel>
                                                    <Select
                                                        labelId="role-label"
                                                        id="role"
                                                        name="role"
                                                        value={values.role}
                                                        label="Role"
                                                        onChange={handleChange}
                                                    >
                                                        <MenuItem value="AGENT">Agent</MenuItem>
                                                        <MenuItem value="MERCHANT">Merchant</MenuItem>
                                                    </Select>
                                                </FormControl>
                                            </Grid>
                                        </Grid>
                                        <Button
                                            type="submit"
                                            fullWidth
                                            variant="contained"
                                            sx={{ mt: 3, mb: 2 }}
                                            disabled={isLoading}
                                        >
                                            {isLoading ? <CircularProgress size={24} /> : 'Continue'}
                                        </Button>

                                        <Box sx={{ textAlign: 'center' }}>
                                            Already have an account?{' '}
                                            <Link
                                                href="/login"
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
                                                Sign in
                                            </Link>
                                        </Box>
                                    </form>
                                )}
                            </Formik>
                        ) : (
                            <Formik
                                initialValues={{
                                    business_name: '',
                                    business_address: '',
                                }}
                                validationSchema={agentValidationSchema}
                                onSubmit={handleAgentSubmit}
                            >
                                {({ values, handleChange, handleBlur, touched, errors, isValid, dirty }) => (
                                    <Form>
                                        <TextField
                                            fullWidth
                                            id="business_name"
                                            name="business_name"
                                            label="Business Name"
                                            value={values.business_name}
                                            onChange={handleChange}
                                            onBlur={handleBlur}
                                            error={touched.business_name && Boolean(errors.business_name)}
                                            helperText={touched.business_name && errors.business_name}
                                            margin="normal"
                                        />
                                        <TextField
                                            fullWidth
                                            id="business_address"
                                            name="business_address"
                                            label="Business Address"
                                            value={values.business_address}
                                            onChange={handleChange}
                                            onBlur={handleBlur}
                                            error={touched.business_address && Boolean(errors.business_address)}
                                            helperText={touched.business_address && errors.business_address}
                                            margin="normal"
                                            multiline
                                            rows={3}
                                        />

                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3, mb: 2 }}>
                                            <Button onClick={handleBack}>
                                                Back
                                            </Button>
                                            <Button
                                                type="submit"
                                                variant="contained"
                                                disabled={isLoading || !isValid || !dirty}
                                            >
                                                {isLoading ? <CircularProgress size={24} /> : 'Register'}
                                            </Button>
                                        </Box>
                                    </Form>
                                )}
                            </Formik>
                        )}
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default Register; 