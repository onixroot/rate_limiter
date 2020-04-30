FROM python:3.7
RUN mkdir /rate_limiter
WORKDIR /rate_limiter
COPY . /rate_limiter