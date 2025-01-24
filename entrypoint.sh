#!/bin/bash
# Inicia o Nginx em segundo plano
service nginx start

# Inicia o Flask
exec python /app/app.py
