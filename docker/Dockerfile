FROM python:3.8-alpine
RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev \
                        libffi-dev

COPY requirements/requirements.txt /opt/requirements.txt

WORKDIR /opt
RUN pip install -r requirements.txt

COPY . /opt

ENTRYPOINT [ "python" ]
CMD ["app.py" ]
