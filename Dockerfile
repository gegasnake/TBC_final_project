FROM ubuntu:latest
LABEL authors="gega"

ENTRYPOINT ["top", "-b"]