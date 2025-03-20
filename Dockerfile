FROM python:3.11.11-bookworm

COPY ./requirements.txt ./
# RUN pip install uv
# RUN pip install -i https://download.pytorch.org/whl/cpu torch
RUN pip install -r requirements.txt

WORKDIR /app
# COPY ./backend/src /app/src