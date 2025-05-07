# Transaction Engine Service

This service handles all transaction-related operations in the Kifiya Mini Agent Platform. It supports various transaction types including wallet loads, bank deposits, and bank withdrawals.

## Features

- Transaction creation and management
- Support for multiple wallet providers (TeleBirr, M-Pesa)
- Support for multiple bank providers (CBE, Dashen, etc.)
- Event-driven architecture using RabbitMQ
- Redis caching for improved performance
- RESTful API endpoints
- Retry mechanism for failed transactions

## Prerequisites

- Python 3.9+
- PostgreSQL
- Redis
- RabbitMQ

## Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following content:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database
   DB_NAME=transaction_engine_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432

   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0

   # RabbitMQ
   RABBITMQ_HOST=localhost
   RABBITMQ_PORT=5672
   RABBITMQ_USER=guest
   RABBITMQ_PASSWORD=guest
   RABBITMQ_VHOST=/

   # Service URLs
   USER_MANAGEMENT_SERVICE_URL=http://localhost:8000
   WALLET_SERVICE_URL=http://localhost:8002
   COMMISSION_SERVICE_URL=http://localhost:8003
   NOTIFICATION_SERVICE_URL=http://localhost:8004

   # Service Port
   PORT=8001
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

## Running the Service

1. Start the Django development server:
   ```bash
   python manage.py runserver 8001
   ```

2. Start the RabbitMQ consumers (in a separate terminal):
   ```bash
   python manage.py start_consumers
   ```

## API Endpoints

### Transactions

- `GET /api/transactions/` - List all transactions
- `POST /api/transactions/` - Create a new transaction
- `GET /api/transactions/{id}/` - Get transaction details
- `GET /api/transactions/providers/?type={type}` - Get available providers for transaction type
- `GET /api/transactions/transaction_types/` - Get available transaction types

### Request/Response Examples

#### Create Transaction
```json
POST /api/transactions/
{
    "transaction_type": "Wallet Load",
    "wallet_provider": "TeleBirr",
    "amount": "1000.00",
    "customer_identifier": "+251912345678"
}
```

#### List Transactions
```json
GET /api/transactions/
{
    "count": 10,
    "next": "http://localhost:8001/api/transactions/?page=2",
    "previous": null,
    "results": [
        {
            "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
            "transaction_type": "Wallet Load",
            "provider_name": "TeleBirr",
            "amount": "1000.00",
            "customer_identifier": "+251912345678",
            "status": "Initiated",
            "created_at": "2024-05-05T12:00:00Z"
        }
    ]
}
```

## Error Handling

The service includes comprehensive error handling:

- Input validation errors (400 Bad Request)
- Authentication errors (401 Unauthorized)
- Not found errors (404 Not Found)
- Server errors (500 Internal Server Error)

## Transaction Flow

1. Client creates a transaction through the API
2. Service validates the request and creates a transaction record
3. Service publishes a transaction.initiated event
4. Other services process the transaction
5. Service receives transaction.completed or transaction.failed event
6. Transaction status is updated accordingly

## Retry Mechanism

The service implements a retry mechanism for failed transactions:

- Maximum 3 retry attempts
- 5-second delay between retries
- Failed status after all retries are exhausted
- Notification sent to agent on final failure 