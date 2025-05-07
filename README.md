# Kifiya Mini Agent Platform

## Infrastructure Setup Instructions

### Prerequisites

1. **PostgreSQL Installation**
   - Download PostgreSQL from [official website](https://www.postgresql.org/download/windows/)
   - During installation:
     - Note down your superuser (postgres) password
     - Keep default port: 5432
   - After installation, create the following databases:
     ```sql
     CREATE DATABASE kifiya_user_management;
     CREATE DATABASE kifiya_wallet;
     CREATE DATABASE kifiya_transaction;
     CREATE DATABASE kifiya_commission;
     CREATE DATABASE kifiya_notification;
     ```

2. **MongoDB Installation**
   - Download MongoDB Community Edition from [official website](https://www.mongodb.com/try/download/community)
   - Install MongoDB Compass (GUI tool) if needed
   - Keep default port: 27017
   - Create database:
     ```
     use kifiya_kyc_aml
     ```

3. **Redis Installation**
   - Download Redis for Windows from [Github](https://github.com/microsoftarchive/redis/releases)
   - Keep default port: 6379
   - Verify installation:
     ```
     redis-cli ping
     ```
   Should respond with "PONG"

4. **RabbitMQ Installation**
   - Install Erlang first from [official website](https://www.erlang.org/downloads)
   - Download RabbitMQ from [official website](https://www.rabbitmq.com/install-windows.html)
   - Keep default ports: 5672 (AMQP) and 15672 (Management)
   - Enable management plugin:
     ```
     rabbitmq-plugins enable rabbitmq_management
     ```
   - Access management interface at: http://localhost:15672
   - Default credentials: guest/guest

### Project Structure
```
kifiya-mini-agent-platform/
├── services/
│   ├── user_management/    # User authentication and management
│   ├── wallet/            # Agent float management
│   ├── transaction_engine/ # Transaction processing
│   ├── commission_engine/  # Commission calculations
│   ├── notification/      # Email notifications
│   └── kyc_aml/          # KYC document storage
└── frontend/             # React frontend application
```

### Service Ports
Each service will run on a different port:
- User Management Service: 8000
- Wallet Service: 8001
- Transaction Engine Service: 8002
- Commission Engine Service: 8003
- Notification Service: 8004
- KYC/AML Service: 8005
- Frontend: 3000

### Environment Variables
Each service will require its own .env file. Templates will be provided in each service directory.

### Development Setup
Instructions for setting up each service will be provided in their respective directories. 