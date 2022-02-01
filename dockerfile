FROM python:3.8

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# install ffmpeg
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# copy code
COPY . .

# adding to enviromnent variable
ENV PYTHONPATH="$PYTHONPATH:/src"

# start banger bot
CMD [ "python", "src/main.py" ]