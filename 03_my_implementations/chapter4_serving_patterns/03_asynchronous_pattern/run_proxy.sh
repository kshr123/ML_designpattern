#!/bin/bash
# Proxy起動スクリプト

uvicorn src.proxy.app:app --host 0.0.0.0 --port 8000
