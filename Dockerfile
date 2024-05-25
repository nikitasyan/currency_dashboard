FROM python:3.11

WORKDIR /dash_app

EXPOSE 8080

COPY ./requirements.txt /dash_app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /dash_app/requirements.txt

COPY . .

CMD ["python", "main.py"]