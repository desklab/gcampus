########################################################################
# gcampus Dockerfile based on Jupyter Docker Stacks
########################################################################
FROM ubuntu:impish-20210606
LABEL maintainer="Jonas Drotleff <j.drotleff@desk-lab.de>"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND noninteractive
USER root

########################################################################
# The code below is copied from the Jupyter Docker Stacks repository
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
########################################################################
# ---- Miniforge installer ----
# Check https://github.com/conda-forge/miniforge/releases
ARG conda_version="4.10.2"
ARG miniforge_patch_number="0"
ARG miniforge_arch="x86_64"
ARG miniforge_python="Mambaforge"
ARG miniforge_version="${conda_version}-${miniforge_patch_number}"
ARG miniforge_installer="${miniforge_python}-${miniforge_version}-Linux-${miniforge_arch}.sh"
ARG miniforge_checksum="1e89ee86afa06e23b2478579be16a33fff6cff346314f6a6382fd20b1f83e669"
# ARG PYTHON_VERSION=default

ENV CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

ENV PATH="${CONDA_DIR}/bin:${PATH}" \
    CONDA_VERSION="${conda_version}" \
    MINIFORGE_VERSION="${miniforge_version}"

WORKDIR /tmp
ADD "https://github.com/conda-forge/miniforge/releases/download/${miniforge_version}/${miniforge_installer}" /tmp/${miniforge_installer}

RUN echo "${miniforge_checksum} *${miniforge_installer}" | sha256sum --check && \
    # Install miniforge
    /bin/bash "${miniforge_installer}" -f -b -p "${CONDA_DIR}" && \
    # Remove miniforge installer
    rm "${miniforge_installer}" && \
    # Conda configuration see https://conda.io/projects/conda/en/latest/configuration.html
    echo "conda ${CONDA_VERSION}" >> "${CONDA_DIR}/conda-meta/pinned" && \
    conda config --system --set auto_update_conda false && \
    conda config --system --set show_channel_urls true && \
    # if [[ "${PYTHON_VERSION}" != "default" ]]; then conda install --yes python="${PYTHON_VERSION}"; fi && \
    conda list python | grep '^python ' | tr -s ' ' | cut -d ' ' -f 1,2 >> "${CONDA_DIR}/conda-meta/pinned" && \
    conda install --quiet --yes "conda=${CONDA_VERSION}" 'pip' && \
    conda update --all --quiet --yes

########################################################################
# Setup GCampus
########################################################################
RUN useradd -m gcampus && \
    # Create gcampus directory
    mkdir /srv/gcampus && \
    chown -R gcampus /srv/gcampus

WORKDIR /srv/gcampus

ADD --chown=gcampus requirements.txt /srv/gcampus/requirements.txt

# Install dependencies for gcampus
RUN conda install --quiet --yes -c conda-forge gdal && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn && \
    conda clean --all -f -y

ADD --chown=gcampus . /srv/gcampus

USER gcampus
EXPOSE 8000
ENTRYPOINT ["gunicorn"]
