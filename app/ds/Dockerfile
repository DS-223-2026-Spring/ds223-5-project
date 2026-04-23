FROM python:3.11-slim

WORKDIR /app/ds

COPY requirements.txt /app/ds/requirements.txt
RUN pip install --no-cache-dir -r /app/ds/requirements.txt

COPY . /app/ds

CMD ["python", "eda_modeling.py"]
