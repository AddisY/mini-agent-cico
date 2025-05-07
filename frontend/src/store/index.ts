import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';

export const store = configureStore({
    reducer: {
        auth: authReducer,
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Create a pre-typed useDispatch hook
import { useDispatch } from 'react-redux';
export const useAppDispatch = () => useDispatch<AppDispatch>(); 