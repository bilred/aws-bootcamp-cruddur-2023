# Root from Doker-hub: layer debian image, scratch image  
FROM 873001202713.dkr.ecr.ca-central-1.amazonaws.com/cruddur-python:3.10-slim-buster

# Inside Container
# Make new folder inside container
WORKDIR /backend-flask

# Outside Container -> Inside Container 
# Install the python libraries used for the app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Outside Container -> Inside Container
# . means everything in the current directory
# first period . - /backend-flask (outside container)
# secend period . - /backend-flask (inside container) 
COPY . .

# Set Environment Variables
# Inside Container and will remain set when the container is runing
ENV FLASK_ENV=development

EXPOSE ${PORT}

# Make sure to print our stuff out when we want to print for flask
ENV PYTHONUNBUFFERED=1

# CMD (Command)
# python3 -m flask run --host=0.0.0.0 --port=4567
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567", "--debug"]