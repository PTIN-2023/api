FROM python

COPY requirements/requirements.txt /opt/
RUN pip3 install -r /opt/requirements.txt

WORKDIR /opt
#COPY . .

RUN pip install paho-mqtt
RUN pip install paypalrestsdk

ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

ENV FLASK_APP=app
ENV FLASK_DEBUG=0
CMD  ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
