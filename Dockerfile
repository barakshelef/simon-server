FROM python:3.9-buster
RUN pip install websockets
COPY main.py main.py

CMD python main.py