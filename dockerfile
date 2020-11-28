FROM python:3.8

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy code
COPY src/ .

# start banger bot
CMD [ "python", "./banger_bot.py" ]