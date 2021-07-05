FROM python:3.9

EXPOSE 80/tcp
EXPOSE 443/tcp

ENV PROJ_DIR=/app

RUN pip install pipenv

WORKDIR $PROJ_DIR
COPY . .
RUN pipenv install --deploy --ignore-pipfile
ENTRYPOINT ["python", "src"]
