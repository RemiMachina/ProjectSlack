FROM python:3.7-alpine

COPY source/ source/

ENTRYPOINT ["source/run.sh"]