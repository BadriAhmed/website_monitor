FROM  python:3.8.16-slim as builder
RUN python -m venv .venv
RUN /.venv/bin/python3 -m pip install --upgrade pip
COPY requirements.txt /.

COPY . .
RUN  python3 -m pip install -r requirements.txt

FROM python:3.8.16-slim

COPY --from=builder /. /.

EXPOSE 8080
CMD ["python","app.py"]