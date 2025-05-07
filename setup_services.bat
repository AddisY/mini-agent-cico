@echo off

REM Setup User Management Service
cd services\user_management
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework django-cors-headers psycopg2-binary pika redis face-recognition
django-admin startproject user_management .
django-admin startapp api
deactivate
cd ..\..

REM Setup Wallet Service
cd services\wallet
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework django-cors-headers psycopg2-binary pika redis
django-admin startproject wallet .
django-admin startapp api
deactivate
cd ..\..

REM Setup Transaction Engine Service
cd services\transaction_engine
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework django-cors-headers psycopg2-binary pika redis
django-admin startproject transaction_engine .
django-admin startapp api
deactivate
cd ..\..

REM Setup Commission Engine Service
cd services\commission_engine
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework django-cors-headers psycopg2-binary pika redis
django-admin startproject commission_engine .
django-admin startapp api
deactivate
cd ..\..

REM Setup Notification Service
cd services\notification
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework django-cors-headers psycopg2-binary pika redis
django-admin startproject notification .
django-admin startapp api
deactivate
cd ..\..

REM Setup KYC/AML Service
cd services\kyc_aml
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework django-cors-headers pymongo pika redis
django-admin startproject kyc_aml .
django-admin startapp api
deactivate
cd ..\..

REM Setup Frontend
cd frontend
npm init -y
npm install react react-dom react-router-dom @reduxjs/toolkit react-redux axios @mui/material @mui/icons-material @emotion/react @emotion/styled
npm install --save-dev @vitejs/plugin-react vite @types/react @types/react-dom typescript
cd .. 