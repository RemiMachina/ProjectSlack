FROM python:3.7-alpine

COPY source /source

RUN chmod -R 755 /source

ENTRYPOINT ["/source/run.sh"]