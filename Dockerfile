FROM python:3.10

ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV 
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /flask-app

COPY requirements.txt .
COPY . /flask-app

RUN pip install -r requirements.txt

RUN python3 -m pip install --upgrade pip

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]