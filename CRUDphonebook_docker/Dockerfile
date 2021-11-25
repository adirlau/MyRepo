FROM ubuntu:latest

WORKDIR /myapp

RUN apt-get update
RUN apt install -y python3-pip
RUN pip3 install --upgrade pip
RUN apt-get install -y postgresql-client

COPY ./ ./

EXPOSE 8050
RUN pip3 install -r ./requirements.txt

CMD ["python3", "./crud_phonebook.py"]
