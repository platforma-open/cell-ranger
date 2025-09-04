# Auto-generated Dockerfile for Python package
FROM python:3.12.10

WORKDIR /app/

RUN apt-get update && apt-get install -y gfortran 

# Install dependencies to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package source
COPY . /app/

# Set Python path
ENV PYTHONPATH=/app/

# Default command (will be overridden by entrypoint)
CMD ["bash"]
