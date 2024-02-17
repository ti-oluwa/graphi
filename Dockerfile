FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -U -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV APP_NAME Graphi

# Run app.py when the container launches
CMD ["python", "manage.py", "runserver"]

