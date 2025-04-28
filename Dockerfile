###################################################
# Stage: base
###################################################
FROM python:3.10-slim AS base 

# RUN apt-get update && apt-get install -y libpq-dev gcc \
#     && pip install psycopg2


RUN apt-get update && apt-get install -y build-essential libpq-dev
RUN pip install --upgrade pip setuptools wheel
# RUN pip install psycopg2

# Create a dedicated app user and directories in one step
RUN addgroup --system app && adduser --system --no-create-home --ingroup app app \
    && mkdir -p /usr/local/app/media /usr/local/app/logs /usr/local/app/static \
    && chown -R app:app /usr/local/app

# Set working directory **after** user creation
WORKDIR /usr/local/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

###################################################
# Stage: dependency-base (Install Dependencies)
###################################################
FROM base AS dependency-base
COPY requirements.txt .
RUN --mount=type=cache,id=pip,target=/root/.cache/pip \
    pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

###################################################
# Stage: backend-app (Final Build)
###################################################
FROM dependency-base AS backend-app
# RUN python manage.py collectstatic --no-input --clear
COPY . /usr/local/app/

# Ensure correct file ownership
RUN chown -R app:app /usr/local/app

# Switch to non-root user
USER app
