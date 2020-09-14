# Base Dockerfile for image used in .gitlabci.yaml runs
FROM python:3.8.5
WORKDIR /

COPY pyproject.toml .
RUN pip install poetry
RUN poetry install

# COPY . .

CMD ["/bin/bash"]
