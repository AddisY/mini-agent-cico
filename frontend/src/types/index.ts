export interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    phone_number: string;
    role: 'ADMIN' | 'AGENT' | 'MERCHANT';
    is_active: boolean;
    is_staff: boolean;
    is_superuser: boolean;
    date_joined: string;
    last_login: string;
}

export interface Agent {
    id: number;
    user: User;
    agent_id: string;
    business_name: string;
    business_address: string;
    status: 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';
    commission_rate: number;
    total_transactions: number;
    created_at: string;
    updated_at: string;
    documents: AgentDocument[];
}

export interface AgentDocument {
    id: number;
    document_type: string;
    document_number: string;
    file_url: string;
    status: 'PENDING' | 'APPROVED' | 'REJECTED';
    is_verified: boolean;
    uploaded_at: string;
    reviewed_at: string | null;
    reviewer_comments: string | null;
}

export interface AuthState {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    error: string | null;
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface LoginFormData {
    email: string;
    password: string;
}

export interface RegisterData {
    username: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone_number: string;
    role?: 'ADMIN' | 'AGENT' | 'MERCHANT';
}

export interface TransactionStats {
    total_transactions: number;
    total_amount: string;
    successful_transactions: number;
    successful_amount: string;
    failed_transactions: number;
    pending_transactions: number;
    total_commission_earned: string;
}

export interface Transaction {
    transaction_id: string;
    transaction_type: 'WALLET_LOAD' | 'BANK_DEPOSIT' | 'BANK_WITHDRAWAL';
    amount: string;
    status: 'INITIATED' | 'SUCCESSFUL' | 'FAILED' | 'PENDING';
    commission_amount: string;
    commission_status: 'PENDING' | 'PAID' | 'FAILED';
    created_at: string;
    updated_at: string;
    error_message?: string;
    provider_name: string;
}

export interface AgentRegistrationData {
    user: RegisterData;
    business_name: string;
    business_address: string;
    commission_rate: number;
} 