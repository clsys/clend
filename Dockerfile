FROM python:3.8

WORKDIR /usr/src/app

ENV IP="127.0.0.1:8000"

COPY . .


RUN pip install pip -U && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN sh ./install.sh
WORKDIR /usr/src/app/dataclasses-0.8
RUN python setup.py install
WORKDIR /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt && pip install hs_udata-0.2.2-py3-none-any.whl

CMD [ "python", "./manage.py", "runserver", "$IP" ]