FROM python:2-alpine
MAINTAINER ACM@UIUC

# Create app directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install app dependencies
COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

# Bundle app source
COPY . /usr/src/app

EXPOSE 42069

CMD [ "python", "app.py" ]
