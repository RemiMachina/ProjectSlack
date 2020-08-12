FROM python:3.7-alpine

COPY source /source

RUN chmod --recursive 755 /source

ENTRYPOINT ["/source/run.sh"]