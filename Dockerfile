# Use the official Miniconda image
FROM continuumio/miniconda3

# Set a working directory
WORKDIR /app

# Create a new conda environment with Python and osmnx dependencies
RUN conda create -n osmnx_env python=3.9 && \
    echo "source activate osmnx_env" > ~/.bashrc

# Activate the conda environment and install osmnx and its dependencies
RUN /bin/bash -c "source activate osmnx_env && conda install -y -c conda-forge osmnx"

# Copy your application code (if any) into the container
COPY . /app

# Set the default command to activate the conda environment and run your Python script
CMD ["/bin/bash", "-c", "source activate osmnx_env"]
