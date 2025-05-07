# Wallet Service API Documentation

## Base URL
```
http://localhost:8002/api/
```

## Authentication
All endpoints require JWT authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

The token is validated against the User Management Service. Invalid or expired tokens will receive a 401 Unauthorized response.

## Endpoints

### 1. List Agent's Wallet
Get the authenticated agent's wallet details.

**Endpoint:** `GET /api/wallets/`

**Authentication Required:** Yes

**Response Format:**
```json
{
    "id": "uuid",
    "agent_id": "uuid",
    "balance": "0.00",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "is_active": true
}
```

**Response Fields:**
- `id` (UUID): Unique identifier of the wallet
- `agent_id` (UUID): ID of the agent who owns the wallet
- `balance` (Decimal): Current wallet balance
- `created_at` (DateTime): Timestamp when the wallet was created
- `updated_at` (DateTime): Timestamp of last wallet update
- `is_active` (Boolean): Wallet status

**Possible Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Wallet not found

### 2. Get Wallet Balance
Get the current balance of the authenticated agent's wallet.

**Endpoint:** `GET /api/wallets/balance/`

**Authentication Required:** Yes

**Response Format:**
```json
{
    "balance": "0.00"
}
```

**Response Fields:**
- `balance` (Decimal): Current wallet balance with 2 decimal places

**Possible Status Codes:**
- 200: Success
- 401: Unauthorized
- 404: Wallet not found

## Event-Based Operations

The Wallet Service handles the following operations through RabbitMQ events:

### 1. Automatic Wallet Creation
- Triggered by: `agent.created` event
- Creates a new wallet automatically when a new agent is registered
- Initial balance: 0.00

### 2. Balance Updates
- Triggered by: Transaction events
- Updates wallet balance based on successful transactions
- Supported transaction types:
  - WALLET_LOAD (Credit)
  - BANK_DEPOSIT (Credit)
  - Other transaction types (Debit)

## Error Responses

**401 Unauthorized:**
```json
{
    "detail": "Invalid token"
}
```

**404 Not Found:**
```json
{
    "detail": "Not found."
}
```

## Notes
- All monetary values are handled with 15 digits and 2 decimal places
- Balance updates are performed atomically with proper database locking
- The service maintains a single wallet per agent
- Only successful transactions trigger balance updates 