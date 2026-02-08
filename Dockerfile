# -------- Build stage --------
FROM python:3.13.9-slim-bookworm AS builder

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  UV_PYTHON_DOWNLOADS=0

# Set work directory.
WORKDIR /application

# Install uv using the distro-less image.
# Using minor versions 0.9 to get security updates.
# Latest tested with: 0.9.15.
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

# Install dependencies.
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project --no-default-groups

COPY . /application/

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-default-groups

# -------- Final stage --------
FROM python:3.13.9-slim-bookworm AS final

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

# Set work directory.
WORKDIR /application

# Create a non-root user to run the application.
RUN groupadd --system --gid 999 appuser \
  && useradd --system --gid 999 --uid 999 --create-home appuser

# Placing binary directory at the start of the PATH.
ENV PATH="/application/.venv/bin:$PATH"

# Copy installed packages from builder stage.
COPY --from=builder --chown=appuser:appuser /application /application

# Create logs directories, preventing PermissionError in application startup.
RUN mkdir -p /application/logs && chown appuser:appuser /application/logs

# Make the entrypoint script executable.
RUN chmod +x ./scripts/entrypoint.sh

# Compile Python bytecode.
RUN python -m compileall -q

# Switch to non-root user.
USER appuser

# Expose port.
EXPOSE 8000

# Health check.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health-check || exit 1

# Run the application.
ENTRYPOINT ["./scripts/entrypoint.sh"]
