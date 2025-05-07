import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    AppBar,
    Box,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Typography,
    Divider,
    Toolbar,
    IconButton,
    Menu,
    MenuItem,
} from '@mui/material';
import {
    Dashboard as DashboardIcon,
    History as HistoryIcon,
    SwapHoriz as SwapHorizIcon,
    Person as PersonIcon,
    Logout as LogoutIcon,
    AccountCircle as AccountCircleIcon,
} from '@mui/icons-material';
import { logout } from '../store/authSlice';
import { useAppDispatch } from '../store';
import KifiyaLogo from '../assets/images/kifiya-logo.png';

const drawerWidth = 240;

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const dispatch = useAppDispatch();
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    const handleProfile = () => {
        handleMenuClose();
        navigate('/profile');
    };

    const handleLogout = () => {
        handleMenuClose();
        dispatch(logout());
        navigate('/login');
    };

    return (
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            {/* Sidebar */}
            <Box
                sx={{
                    width: drawerWidth,
                    flexShrink: 0,
                    borderRight: 1,
                    borderColor: 'divider',
                    bgcolor: 'background.paper',
                    position: 'fixed',
                    height: '100vh',
                    zIndex: 1000,
                    top: 0,
                    left: 0
                }}
            >
                <Box 
                    sx={{ 
                        height: '64px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        px: 3,
                        cursor: 'pointer',
                        bgcolor: '#fff'
                    }}
                    onClick={() => navigate('/dashboard')}
                >
                    <img 
                        src={KifiyaLogo} 
                        alt="Kifiya Logo" 
                        style={{ 
                            height: '70px',
                            width: 'auto',
                            objectFit: 'contain',
                            marginTop: '10px'
                        }} 
                    />
                </Box>
                <Divider />
                <List>
                    <ListItem disablePadding>
                        <ListItemButton 
                            onClick={() => navigate('/dashboard')}
                            selected={location.pathname === '/dashboard'}
                        >
                            <ListItemIcon>
                                <DashboardIcon />
                            </ListItemIcon>
                            <ListItemText primary="Dashboard" />
                        </ListItemButton>
                    </ListItem>

                    <ListItem disablePadding>
                        <ListItemButton 
                            onClick={() => navigate('/transactions')}
                            selected={location.pathname === '/transactions'}
                        >
                            <ListItemIcon>
                                <HistoryIcon />
                            </ListItemIcon>
                            <ListItemText primary="Transaction History" />
                        </ListItemButton>
                    </ListItem>

                    <ListItem disablePadding>
                        <ListItemButton 
                            onClick={() => navigate('/make-transaction')}
                            selected={location.pathname === '/make-transaction'}
                        >
                            <ListItemIcon>
                                <SwapHorizIcon />
                            </ListItemIcon>
                            <ListItemText primary="Make Transaction" />
                        </ListItemButton>
                    </ListItem>

                    <ListItem disablePadding>
                        <ListItemButton 
                            onClick={() => navigate('/profile')}
                            selected={location.pathname === '/profile'}
                        >
                            <ListItemIcon>
                                <PersonIcon />
                            </ListItemIcon>
                            <ListItemText primary="Profile" />
                        </ListItemButton>
                    </ListItem>

                    <ListItem disablePadding>
                        <ListItemButton onClick={handleLogout}>
                            <ListItemIcon>
                                <LogoutIcon />
                            </ListItemIcon>
                            <ListItemText primary="Logout" />
                        </ListItemButton>
                    </ListItem>
                </List>
            </Box>

            {/* Main content wrapper */}
            <Box 
                sx={{ 
                    flexGrow: 1, 
                    ml: `${drawerWidth}px`,
                    position: 'relative',
                    overflow: 'auto',
                    height: '100vh'
                }}
            >
                {/* Top AppBar */}
                <AppBar 
                    position="sticky" 
                    sx={{ 
                        width: '100%',
                        zIndex: 1200,
                        bgcolor: 'primary.main',
                        boxShadow: theme => `0 2px 4px -1px ${theme.palette.action.active}1f, 0 4px 5px 0 ${theme.palette.action.active}14, 0 1px 10px 0 ${theme.palette.action.active}12`,
                    }}
                >
                    <Toolbar>
                        <Typography 
                            variant="h6" 
                            component="div" 
                            sx={{ 
                                flexGrow: 1,
                                fontSize: '1.158rem'
                            }}
                        >
                            Agent Dashboard
                        </Typography>
                        <Box
                            onMouseEnter={handleMenuOpen}
                            onMouseLeave={handleMenuClose}
                        >
                            <IconButton
                                size="large"
                                edge="end"
                                color="inherit"
                                aria-label="account"
                                onClick={handleMenuOpen}
                            >
                                <AccountCircleIcon />
                            </IconButton>
                            <Menu
                                anchorEl={anchorEl}
                                open={Boolean(anchorEl)}
                                onClose={handleMenuClose}
                                anchorOrigin={{
                                    vertical: 'bottom',
                                    horizontal: 'right',
                                }}
                                transformOrigin={{
                                    vertical: 'top',
                                    horizontal: 'right',
                                }}
                                MenuListProps={{
                                    onMouseLeave: handleMenuClose,
                                    onMouseEnter: () => setAnchorEl(anchorEl || document.activeElement as HTMLElement)
                                }}
                                sx={{
                                    '& .MuiMenuItem-root': {
                                        py: 1,
                                        px: 2,
                                    }
                                }}
                            >
                                <MenuItem onClick={handleProfile}>
                                    Profile
                                </MenuItem>
                                <MenuItem onClick={handleLogout}>
                                    Logout
                                </MenuItem>
                            </Menu>
                        </Box>
                    </Toolbar>
                </AppBar>

                {/* Main Content */}
                <Box component="main" sx={{ p: 3 }}>
                    {children}
                </Box>
            </Box>
        </Box>
    );
};

export default Layout; 