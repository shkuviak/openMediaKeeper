FROM ghcr.io/astral-sh/uv:alpine3.23

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY openmediakeeper openmediakeeper
ENV HOME /app
RUN chown -R 1000:1000 /app
USER 1000
RUN uv sync
CMD ["uv", "run", "omk"]