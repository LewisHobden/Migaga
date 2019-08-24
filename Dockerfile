from python:3

MAINTAINER Lewis Hobden <lewis@hobden.xyz>

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "tail", "-f", "/dev/null" ]

# CMD [ "python", "./bot.py" ]
