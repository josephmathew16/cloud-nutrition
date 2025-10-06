# Use a lightweight Python base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy the entire project to the container
COPY . /app

# Install required Python packages
RUN pip install pandas matplotlib seaborn

# Command to run your Python data analysis script
CMD ["python", "analysis/data_analysis.py"]
