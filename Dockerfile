FROM python:3.9

COPY . /app

WORKDIR /app

ARG aws_access_key_id
ENV aws_access_key_id $aws_access_key_id
ARG aws_secret_access_key
ENV aws_secret_access_key $aws_secret_access_key

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["flask", "run","--host", "0.0.0.0"]