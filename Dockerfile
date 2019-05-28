FROM continuumio/miniconda3:4.6.14
RUN mkdir /code
WORKDIR /code
COPY env.yaml /code/
RUN conda env create -f /code/env.yaml
RUN echo "source activate demos" > ~/.bashrc
ENV PATH /opt/conda/envs/demos/bin:$PATH
COPY . /code/
