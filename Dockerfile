FROM ubuntu:22.04

ARG WORKDIR=/work
ENV LANG ja_JP.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONBREAKPOINT=IPython.terminal.debugger.set_trace
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH=/root/.local/bin:$PATH

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        vim && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir ${WORKDIR}
WORKDIR ${WORKDIR}

RUN mkdir tools && \
    git clone --depth 1 https://github.com/acl-org/acl-anthology ./tools/acl-anthology

COPY ./pyproject.toml ./uv.lock ./.python-version ./
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    uv python pin $(cat .python-version) && \
    uv sync --no-dev

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]