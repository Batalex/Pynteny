FROM mcr.microsoft.com/devcontainers/miniconda:0-3

WORKDIR /Pynteny
# Copy repo to docker container
COPY pynteny pynteny/
COPY tests tests/
COPY envs envs/
COPY README.md .
COPY pyproject.toml .
COPY LICENSE .

# Make conda environment and activate
RUN conda install mamba -n base -c conda-forge
RUN mamba env create -f envs/pynteny-dev.yml
SHELL ["conda", "run", "-n", "pynteny-dev", "/bin/bash", "-c"]
# Build and install Pynteny
RUN poetry build && pip install dist/pynteny*.whl && pynteny --help
# Give read/write permissions to install directory (needed to make config.json)
RUN chmod ugo+rw /opt/conda/envs/pynteny-dev/lib/python3.10/site-packages

# Initialize conda for default user
RUN conda init
# # Activate pynteny environment by default
RUN echo "conda activate pynteny-dev" >> ../root/.bashrc
RUN source ../root/.bashrc