# Use the official Miniconda image
FROM continuumio/miniconda3

# Set a working directory
WORKDIR /app

# Create a new conda environment with Python and osmnx dependencies
RUN conda create -n osmnx_env python=3.11 -y

# Activate the conda environment and install osmnx and its dependencies
RUN conda run -n osmnx_env conda install -y -c conda-forge --strict-channel-priority osmnx

# Copy your application code into the container
COPY . /app

# Make sure we use the conda environment by default
ENV PATH /opt/conda/envs/osmnx_env/bin:$PATH

# Set the default command to run python in the conda environment
CMD ["python", "app.py"]
