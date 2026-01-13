FROM python:3.10-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN chmod +x build_cpp.sh

RUN pip install build && python -m build --wheel

FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /app/dist/*.whl /tmp/

RUN pip install /tmp/*.whl && rm /tmp/*.whl

RUN useradd  -m appuser
USER appuser

ENTRYPOINT ["python", "-m", "shield_lite.cli"]
CMD ["--help"]