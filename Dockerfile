# Use lightweight Python 3.11 image
FROM python:3.11-slim

WORKDIR /app

ENV TZ=Asia/Ho_Chi_Minh

# Install system dependencies required for LightGBM / XGBoost C++ libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and models
COPY app.py .
COPY digital_twin_hvac_model.pkl .
COPY mock_iot_sensor.py .
COPY logo.png .
COPY templates/ ./templates/
COPY Build_Web/ ./Build_Web/

EXPOSE 8000

# Default command to run FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
