FROM python:3.8

WORKDIR /usr/src/app

ENV PORT 8000

COPY . .
EXPOSE 8000

RUN pip install pip -U && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN sh ./install.sh
WORKDIR /usr/src/app/dataclasses-0.8
RUN python setup.py install
WORKDIR /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt

CMD python manage.py runserver 0.0.0.0:$PORT