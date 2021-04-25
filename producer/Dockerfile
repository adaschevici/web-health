FROM python:3.9

WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# dont write pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# dont buffer to stdout/stderr
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /usr/src/app/requirements.txt
COPY ./Pipfile /usr/src/app/Pipfile

# dependencies
RUN set -eux \
    && pip install --upgrade pip setuptools wheel
RUN pip install pipenv
RUN pipenv install --dev
