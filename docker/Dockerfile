FROM python:3.6
WORKDIR /app
COPY requirements.txt requirements.txt 
RUN pip3 install -r requirements.txt
COPY . .
ARG DEVICE_ID
ENV DEVICE_ID=${DEVICE_ID}
RUN export DEVICE_ID
CMD ["python3", "-u", "./main.py"]