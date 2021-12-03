FROM python:3.6
WORKDIR /app
COPY requirements.txt requirements.txt 
RUN pip3 install -r requirements.txt
COPY . .
ARG SEED
ENV SEED=${SEED}
RUN export SEED
CMD ["python3", "-u", "./main.py"]