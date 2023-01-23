FROM python:slim

WORKDIR /app
COPY tester.py .
RUN pip3 install requests

ENTRYPOINT ["python3", "/app/tester.py"]