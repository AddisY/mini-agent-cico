@echo off

REM User Management Service .env template
echo # Django Settings > services\user_management\.env.template
echo DEBUG=True >> services\user_management\.env.template
echo SECRET_KEY=your_secret_key_here >> services\user_management\.env.template
echo ALLOWED_HOSTS=localhost,127.0.0.1 >> services\user_management\.env.template
echo. >> services\user_management\.env.template
echo # Database >> services\user_management\.env.template
echo DB_NAME=kifiya_user_management >> services\user_management\.env.template
echo DB_USER=postgres >> services\user_management\.env.template
echo DB_PASSWORD=your_password_here >> services\user_management\.env.template
echo DB_HOST=localhost >> services\user_management\.env.template
echo DB_PORT=5432 >> services\user_management\.env.template
echo. >> services\user_management\.env.template
echo # Redis >> services\user_management\.env.template
echo REDIS_HOST=localhost >> services\user_management\.env.template
echo REDIS_PORT=6379 >> services\user_management\.env.template
echo REDIS_DB=0 >> services\user_management\.env.template
echo. >> services\user_management\.env.template
echo # RabbitMQ >> services\user_management\.env.template
echo RABBITMQ_HOST=localhost >> services\user_management\.env.template
echo RABBITMQ_PORT=5672 >> services\user_management\.env.template
echo RABBITMQ_USER=guest >> services\user_management\.env.template
echo RABBITMQ_PASSWORD=guest >> services\user_management\.env.template
echo. >> services\user_management\.env.template
echo # JWT Settings >> services\user_management\.env.template
echo JWT_SECRET_KEY=your_jwt_secret_key_here >> services\user_management\.env.template
echo JWT_ACCESS_TOKEN_LIFETIME=5 >> services\user_management\.env.template
echo JWT_REFRESH_TOKEN_LIFETIME=1 >> services\user_management\.env.template
echo. >> services\user_management\.env.template
echo # CORS >> services\user_management\.env.template
echo CORS_ALLOWED_ORIGINS=http://localhost:3000 >> services\user_management\.env.template

REM Wallet Service .env template
echo # Django Settings > services\wallet\.env.template
echo DEBUG=True >> services\wallet\.env.template
echo SECRET_KEY=your_secret_key_here >> services\wallet\.env.template
echo ALLOWED_HOSTS=localhost,127.0.0.1 >> services\wallet\.env.template
echo. >> services\wallet\.env.template
echo # Database >> services\wallet\.env.template
echo DB_NAME=kifiya_wallet >> services\wallet\.env.template
echo DB_USER=postgres >> services\wallet\.env.template
echo DB_PASSWORD=your_password_here >> services\wallet\.env.template
echo DB_HOST=localhost >> services\wallet\.env.template
echo DB_PORT=5432 >> services\wallet\.env.template
echo. >> services\wallet\.env.template
echo # Redis >> services\wallet\.env.template
echo REDIS_HOST=localhost >> services\wallet\.env.template
echo REDIS_PORT=6379 >> services\wallet\.env.template
echo REDIS_DB=1 >> services\wallet\.env.template
echo. >> services\wallet\.env.template
echo # RabbitMQ >> services\wallet\.env.template
echo RABBITMQ_HOST=localhost >> services\wallet\.env.template
echo RABBITMQ_PORT=5672 >> services\wallet\.env.template
echo RABBITMQ_USER=guest >> services\wallet\.env.template
echo RABBITMQ_PASSWORD=guest >> services\wallet\.env.template
echo. >> services\wallet\.env.template
echo # CORS >> services\wallet\.env.template
echo CORS_ALLOWED_ORIGINS=http://localhost:3000 >> services\wallet\.env.template

REM Transaction Engine Service .env template
echo # Django Settings > services\transaction_engine\.env.template
echo DEBUG=True >> services\transaction_engine\.env.template
echo SECRET_KEY=your_secret_key_here >> services\transaction_engine\.env.template
echo ALLOWED_HOSTS=localhost,127.0.0.1 >> services\transaction_engine\.env.template
echo. >> services\transaction_engine\.env.template
echo # Database >> services\transaction_engine\.env.template
echo DB_NAME=kifiya_transaction >> services\transaction_engine\.env.template
echo DB_USER=postgres >> services\transaction_engine\.env.template
echo DB_PASSWORD=your_password_here >> services\transaction_engine\.env.template
echo DB_HOST=localhost >> services\transaction_engine\.env.template
echo DB_PORT=5432 >> services\transaction_engine\.env.template
echo. >> services\transaction_engine\.env.template
echo # Redis >> services\transaction_engine\.env.template
echo REDIS_HOST=localhost >> services\transaction_engine\.env.template
echo REDIS_PORT=6379 >> services\transaction_engine\.env.template
echo REDIS_DB=2 >> services\transaction_engine\.env.template
echo. >> services\transaction_engine\.env.template
echo # RabbitMQ >> services\transaction_engine\.env.template
echo RABBITMQ_HOST=localhost >> services\transaction_engine\.env.template
echo RABBITMQ_PORT=5672 >> services\transaction_engine\.env.template
echo RABBITMQ_USER=guest >> services\transaction_engine\.env.template
echo RABBITMQ_PASSWORD=guest >> services\transaction_engine\.env.template
echo. >> services\transaction_engine\.env.template
echo # CORS >> services\transaction_engine\.env.template
echo CORS_ALLOWED_ORIGINS=http://localhost:3000 >> services\transaction_engine\.env.template

REM Commission Engine Service .env template
echo # Django Settings > services\commission_engine\.env.template
echo DEBUG=True >> services\commission_engine\.env.template
echo SECRET_KEY=your_secret_key_here >> services\commission_engine\.env.template
echo ALLOWED_HOSTS=localhost,127.0.0.1 >> services\commission_engine\.env.template
echo. >> services\commission_engine\.env.template
echo # Database >> services\commission_engine\.env.template
echo DB_NAME=kifiya_commission >> services\commission_engine\.env.template
echo DB_USER=postgres >> services\commission_engine\.env.template
echo DB_PASSWORD=your_password_here >> services\commission_engine\.env.template
echo DB_HOST=localhost >> services\commission_engine\.env.template
echo DB_PORT=5432 >> services\commission_engine\.env.template
echo. >> services\commission_engine\.env.template
echo # Redis >> services\commission_engine\.env.template
echo REDIS_HOST=localhost >> services\commission_engine\.env.template
echo REDIS_PORT=6379 >> services\commission_engine\.env.template
echo REDIS_DB=3 >> services\commission_engine\.env.template
echo. >> services\commission_engine\.env.template
echo # RabbitMQ >> services\commission_engine\.env.template
echo RABBITMQ_HOST=localhost >> services\commission_engine\.env.template
echo RABBITMQ_PORT=5672 >> services\commission_engine\.env.template
echo RABBITMQ_USER=guest >> services\commission_engine\.env.template
echo RABBITMQ_PASSWORD=guest >> services\commission_engine\.env.template
echo. >> services\commission_engine\.env.template
echo # CORS >> services\commission_engine\.env.template
echo CORS_ALLOWED_ORIGINS=http://localhost:3000 >> services\commission_engine\.env.template

REM Notification Service .env template
echo # Django Settings > services\notification\.env.template
echo DEBUG=True >> services\notification\.env.template
echo SECRET_KEY=your_secret_key_here >> services\notification\.env.template
echo ALLOWED_HOSTS=localhost,127.0.0.1 >> services\notification\.env.template
echo. >> services\notification\.env.template
echo # Database >> services\notification\.env.template
echo DB_NAME=kifiya_notification >> services\notification\.env.template
echo DB_USER=postgres >> services\notification\.env.template
echo DB_PASSWORD=your_password_here >> services\notification\.env.template
echo DB_HOST=localhost >> services\notification\.env.template
echo DB_PORT=5432 >> services\notification\.env.template
echo. >> services\notification\.env.template
echo # Redis >> services\notification\.env.template
echo REDIS_HOST=localhost >> services\notification\.env.template
echo REDIS_PORT=6379 >> services\notification\.env.template
echo REDIS_DB=4 >> services\notification\.env.template
echo. >> services\notification\.env.template
echo # RabbitMQ >> services\notification\.env.template
echo RABBITMQ_HOST=localhost >> services\notification\.env.template
echo RABBITMQ_PORT=5672 >> services\notification\.env.template
echo RABBITMQ_USER=guest >> services\notification\.env.template
echo RABBITMQ_PASSWORD=guest >> services\notification\.env.template
echo. >> services\notification\.env.template
echo # Email Settings >> services\notification\.env.template
echo EMAIL_HOST=smtp.gmail.com >> services\notification\.env.template
echo EMAIL_PORT=587 >> services\notification\.env.template
echo EMAIL_USE_TLS=True >> services\notification\.env.template
echo EMAIL_HOST_USER=your_email@gmail.com >> services\notification\.env.template
echo EMAIL_HOST_PASSWORD=your_app_password_here >> services\notification\.env.template
echo. >> services\notification\.env.template
echo # CORS >> services\notification\.env.template
echo CORS_ALLOWED_ORIGINS=http://localhost:3000 >> services\notification\.env.template

REM KYC/AML Service .env template
echo # Django Settings > services\kyc_aml\.env.template
echo DEBUG=True >> services\kyc_aml\.env.template
echo SECRET_KEY=your_secret_key_here >> services\kyc_aml\.env.template
echo ALLOWED_HOSTS=localhost,127.0.0.1 >> services\kyc_aml\.env.template
echo. >> services\kyc_aml\.env.template
echo # MongoDB >> services\kyc_aml\.env.template
echo MONGO_URI=mongodb://localhost:27017/kifiya_kyc_aml >> services\kyc_aml\.env.template
echo. >> services\kyc_aml\.env.template
echo # Redis >> services\kyc_aml\.env.template
echo REDIS_HOST=localhost >> services\kyc_aml\.env.template
echo REDIS_PORT=6379 >> services\kyc_aml\.env.template
echo REDIS_DB=5 >> services\kyc_aml\.env.template
echo. >> services\kyc_aml\.env.template
echo # RabbitMQ >> services\kyc_aml\.env.template
echo RABBITMQ_HOST=localhost >> services\kyc_aml\.env.template
echo RABBITMQ_PORT=5672 >> services\kyc_aml\.env.template
echo RABBITMQ_USER=guest >> services\kyc_aml\.env.template
echo RABBITMQ_PASSWORD=guest >> services\kyc_aml\.env.template
echo. >> services\kyc_aml\.env.template
echo # CORS >> services\kyc_aml\.env.template
echo CORS_ALLOWED_ORIGINS=http://localhost:3000 >> services\kyc_aml\.env.template

REM Frontend .env template
echo VITE_API_BASE_URL=http://localhost:8000 > frontend\.env.template
echo VITE_USER_MANAGEMENT_SERVICE_URL=http://localhost:8000 >> frontend\.env.template
echo VITE_WALLET_SERVICE_URL=http://localhost:8001 >> frontend\.env.template
echo VITE_TRANSACTION_ENGINE_SERVICE_URL=http://localhost:8002 >> frontend\.env.template
echo VITE_COMMISSION_ENGINE_SERVICE_URL=http://localhost:8003 >> frontend\.env.template
echo VITE_NOTIFICATION_SERVICE_URL=http://localhost:8004 >> frontend\.env.template
echo VITE_KYC_AML_SERVICE_URL=http://localhost:8005 >> frontend\.env.template 