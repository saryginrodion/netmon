FROM python:3.14-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml pyproject.toml

RUN uv sync

COPY netmon netmon

CMD ["uv", "run", "-m", "netmon.cmd.netmon_collector"]
