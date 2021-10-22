FROM python:3.8-alpine

WORKDIR /usr/src/app

ENV IP="127.0.0.1:8000"

COPY . .

RUN pip install hs_udata-0.2.2-py3-none-any.whl && pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD [ "python", "./manage.py", "runserver", "${IP}" ]