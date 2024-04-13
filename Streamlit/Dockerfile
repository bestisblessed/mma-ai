# Use an official Python runtime as the parent image
FROM python:3.12.1-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable (optional)
ENV NAME World

# Command to run the Streamlit app
CMD ["streamlit", "run", "Home.py"]

