# Stage 1 — Build
FROM python:3.12-alpine AS builder
WORKDIR /app

# Install build dependencie
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2 — Final (only what's needed)
FROM python:3.12-alpine
WORKDIR /app

# Install only runtime dependencies
RUN apk add --no-cache \
    docker-cli\
    libffi \
    openssl
# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local


# Copy only application code (no build tools)
COPY app.py .
COPY utils/ utils/
COPY templates/ templates/
COPY static/ static/

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Non-root user for security
#RUN adduser -D appuser
#USER appuser

EXPOSE 5000
CMD ["python", "app.py"]
