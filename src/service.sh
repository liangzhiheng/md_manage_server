#!/bin/bash

# 启动项目
gunicorn -w 4 -b 0.0.0.0:8000 md_manage_server.wsgi:application
