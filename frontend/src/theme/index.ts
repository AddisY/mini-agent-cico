import { createTheme } from '@mui/material/styles';

// Kifiya brand colors
const kifiyaNavy = '#364957';
const kifiyaOrange = '#ff8a00';

const theme = createTheme({
  palette: {
    primary: {
      main: kifiyaNavy,
      contrastText: '#fff',
    },
    secondary: {
      main: kifiyaOrange,
      contrastText: '#fff',
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: kifiyaNavy,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          '&.MuiButton-outlined': {
            color: kifiyaOrange,
            borderColor: kifiyaOrange,
            '&:hover': {
              borderColor: '#e67c00',
              backgroundColor: 'rgba(255, 138, 0, 0.04)',
            },
            '& .MuiSvgIcon-root': {
              color: kifiyaOrange,
            },
          },
        },
        containedPrimary: {
          backgroundColor: kifiyaOrange,
          '&:hover': {
            backgroundColor: '#e67c00',
          },
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          '&:hover': {
            backgroundColor: 'rgba(255, 138, 0, 0.04)',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(255, 138, 0, 0.06)',
            '&:hover': {
              backgroundColor: 'rgba(255, 138, 0, 0.09)',
            },
          },
        },
      },
    },
    MuiSvgIcon: {
      styleOverrides: {
        root: {
          '&.card-icon': {
            color: kifiyaOrange,
            marginRight: '16px',
          },
        },
      },
    },
  },
});

export default theme; 