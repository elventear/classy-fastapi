FROM python:3.9.7-bullseye
RUN useradd -ms /bin/bash companionlabs

USER companionlabs
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

ENV PATH="/home/companionlabs/.local/bin:${PATH}"

ENTRYPOINT ["/bin/bash", "-c"]
