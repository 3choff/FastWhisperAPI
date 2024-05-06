FROM nvidia/cuda:12.4.1-base-ubuntu22.04

RUN apt-get update && apt-get install -y python3.10 python3-pip

WORKDIR /app

ADD . /app

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["fastapi", "run", "main.py"]