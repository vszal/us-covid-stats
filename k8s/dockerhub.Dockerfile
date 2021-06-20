# Python image from https://hub.docker.com/_/python
FROM python:3.8-alpine

#RUN pip install --upgrade pip

# set up a non-root user to install and run dependencies
RUN adduser worker --gecos "" --disabled-password --home /home/worker
USER worker
WORKDIR /home/worker

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker app/requirements.txt requirements.txt
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY --chown=worker:worker app* .

# Service must listen to $PORT environment variable.
# This default value facilitates local development.
ENV PORT 8080

# Run the web service on container startup.
# --reload flag makes Skaffold hot-deploy work quicker
CMD exec gunicorn app:app --workers 2 --threads 2 -b 0.0.0.0:8080 --reload
# to build and run this Dockerfile:
# docker build -t covidweb . && docker run --rm -p 8080:8080 -e PORT=8080 covidweb