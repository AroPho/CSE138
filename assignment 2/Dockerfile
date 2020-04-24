FROM python:3.7.6
WORKDIR /project
ADD . /project
RUN pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]