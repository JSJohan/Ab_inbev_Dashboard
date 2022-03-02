FROM centos:7

RUN yum install -y python3\
    && pip3 install --upgrade pip\
	&& pip install psycopg2\
    && pip install psycopg2-binary
    

WORKDIR /app

COPY . /app

RUN pip3 --no-cache-dir install -r requirements.txt

CMD ["python3", "src/main.py"]