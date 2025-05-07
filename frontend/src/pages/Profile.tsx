import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import {
    Container,
    Grid,
    Paper,
    Typography,
    TextField,
    Button,
    Box,
    CircularProgress,
    Divider,
    Alert,
} from '@mui/material';
import { RootState, AppDispatch } from '../store';
import * as api from '../services/api';
import { Navigate } from 'react-router-dom';
import { User } from '../types';

const profileValidationSchema = Yup.object({
    username: Yup.string()
        .min(3, 'Username must be at least 3 characters')
        .required('Username is required'),
    phone_number: Yup.string()
        .matches(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number')
        .required('Phone number is required'),
});

const passwordValidationSchema = Yup.object({
    current_password: Yup.string()
        .required('Current password is required'),
    new_password: Yup.string()
        .min(8, 'Password must be at least 8 characters')
        .required('New password is required'),
    confirm_password: Yup.string()
        .oneOf([Yup.ref('new_password')], 'Passwords must match')
        .required('Confirm password is required'),
});

const Profile: React.FC = () => {
    const { user } = useSelector((state: RootState) => state.auth);
    const [updateSuccess, setUpdateSuccess] = useState(false);
    const [updateError, setUpdateError] = useState<string | null>(null);

    const handleProfileUpdate = async (values: Partial<User>) => {
        try {
            if (!user) return;
            await api.updateUser(user.id, values);
            setUpdateSuccess(true);
            setUpdateError(null);
        } catch (err: any) {
            setUpdateError(err.message || 'Failed to update profile');
            setUpdateSuccess(false);
        }
    };

    if (!user) {
        return <Navigate to="/login" />;
    }

    return (
        <Container maxWidth="sm">
            <Box sx={{ mt: 4, mb: 4 }}>
                <Typography 
                    variant="h6" 
                    sx={{ 
                        fontSize: '1.3rem',
                        mb: 3
                    }}
                >
                    Profile Settings
                </Typography>
                {updateSuccess && (
                    <Alert severity="success" sx={{ mb: 2 }}>
                        Profile updated successfully!
                    </Alert>
                )}
                {updateError && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {updateError}
                    </Alert>
                )}
                <Paper sx={{ p: 3 }}>
                    <Formik
                        initialValues={{
                            username: user.username,
                            email: user.email,
                            first_name: user.first_name,
                            last_name: user.last_name,
                            phone_number: user.phone_number,
                        }}
                        validationSchema={Yup.object({
                            username: Yup.string().required('Username is required'),
                            email: Yup.string().email('Invalid email address').required('Email is required'),
                            first_name: Yup.string().required('First name is required'),
                            last_name: Yup.string().required('Last name is required'),
                            phone_number: Yup.string().required('Phone number is required'),
                        })}
                        onSubmit={handleProfileUpdate}
                    >
                        {({ values, errors, touched, handleChange, handleBlur, handleSubmit }) => (
                            <form onSubmit={handleSubmit}>
                                <Grid container spacing={2}>
                                    <Grid item xs={12}>
                                        <TextField
                                            fullWidth
                                            id="username"
                                            name="username"
                                            label="Username"
                                            value={values.username}
                                            onChange={handleChange}
                                            onBlur={handleBlur}
                                            error={touched.username && Boolean(errors.username)}
                                            helperText={touched.username && errors.username}
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <TextField
                                            fullWidth
                                            id="email"
                                            name="email"
                                            label="Email"
                                            value={values.email}
                                            onChange={handleChange}
                                            onBlur={handleBlur}
                                            error={touched.email && Boolean(errors.email)}
                                            helperText={touched.email && errors.email}
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
                                            value={values.phone_number}
                                            onChange={handleChange}
                                            onBlur={handleBlur}
                                            error={touched.phone_number && Boolean(errors.phone_number)}
                                            helperText={touched.phone_number && errors.phone_number}
                                        />
                                    </Grid>
                                </Grid>
                                <Box sx={{ mt: 3 }}>
                                    <Button
                                        type="submit"
                                        fullWidth
                                        variant="contained"
                                        color="primary"
                                    >
                                        Update Profile
                                    </Button>
                                </Box>
                            </form>
                        )}
                    </Formik>
                </Paper>
            </Box>
        </Container>
    );
};

export default Profile; 