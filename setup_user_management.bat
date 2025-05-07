@echo off

cd services\user_management

REM Create and activate virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install django djangorestframework django-cors-headers psycopg2-binary pika redis

REM Create Django project and app
python -m django-admin startproject user_management .
python -m django-admin startapp api

REM Create .env file
echo # Django Settings > .env
echo DEBUG=True >> .env
echo SECRET_KEY=your_secret_key_here >> .env
echo ALLOWED_HOSTS=localhost,127.0.0.1 >> .env
echo. >> .env
echo # Database >> .env
echo DB_NAME=kifiya_user_management >> .env
echo DB_USER=postgres >> .env
echo DB_PASSWORD=your_password_here >> .env
echo DB_HOST=localhost >> .env
echo DB_PORT=5432 >> .env
echo. >> .env
echo # Redis >> .env
echo REDIS_HOST=localhost >> .env
echo REDIS_PORT=6379 >> .env
echo REDIS_DB=0 >> .env
echo. >> .env
echo # RabbitMQ >> .env
echo RABBITMQ_HOST=localhost >> .env
echo RABBITMQ_PORT=5672 >> .env
echo RABBITMQ_USER=guest >> .env
echo RABBITMQ_PASSWORD=guest >> .env
echo. >> .env
echo # JWT Settings >> .env
echo JWT_SECRET_KEY=your_jwt_secret_key_here >> .env
echo JWT_ACCESS_TOKEN_LIFETIME=5 >> .env
echo JWT_REFRESH_TOKEN_LIFETIME=1 >> .env
echo. >> .env
echo # CORS >> .env
echo CORS_ALLOWED_ORIGINS=http://localhost:3000 >> .env

REM Deactivate virtual environment
deactivate

cd ..\..

echo User Management Service setup complete! 