# use alpine 
FROM python:alpine3.16

# working directory
WORKDIR /app

# copy everything
COPY . .

# upgrade pip
RUN pip install --upgrade pip

# Need this for mysql-sever & dev tools??
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add --no-cache mariadb-dev

# install dependencies
RUN pip install -r requirements.txt

# port 5000 
EXPOSE 5000

# run app command
CMD flask --app capp --debug run --host=0.0.0.0