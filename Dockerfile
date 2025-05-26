FROM python:3.11-slim

# Avoid interactive prompts and buffer output
ENV PYTHONUNBUFFERED=1

# Install requirements first for cache efficiency
WORKDIR /app
COPY requirements.txt dev-requirements.txt /tmp/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt -r /tmp/dev-requirements.txt

# Default command opens a shell for interactive development
CMD ["bash"]
