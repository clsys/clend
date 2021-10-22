FROM python:3.8-alpine

WORKDIR /usr/src/app

ENV IP="127.0.0.1:8000"

COPY . .

RUN python -m pip install --upgrade pip
RUN pip install hs_udata-0.2.2-py3-none-any.whl && pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./manage.py", "runserver", "${IP}" ]