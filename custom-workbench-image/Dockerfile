FROM quay.io/opendatahub/workbench-images:rocm-jupyter-pytorch-ubi9-python-3.9-20241120-3ceb400

LABEL name="odh-notebook-jupyter-pytorch-ubi9-python-3.9" \
    summary="Jupyter pytorch notebook image for ODH notebooks" \
    description="Jupyter pytorch notebook image with base Python 3.9 builder image based on UBI9 for ODH notebooks" \
    io.k8s.display-name="Jupyter pytorch notebook image for ODH notebooks" \
    io.k8s.description="Jupyter pytorch notebook image with base Python 3.9 builder image based on UBI9 for ODH notebooks" \
    authoritative-source-url="https://github.com/opendatahub-io/notebooks" \
    io.openshift.build.commit.ref="main" \
    io.openshift.build.source-location="https://github.com/opendatahub-io/notebooks/tree/main/jupyter/pytorch/ubi9-python-3.9" \
    io.openshift.build.image="quay.io/opendatahub/workbench-images:jupyter-pytorch-ubi9-python-3.9"

# Install Python packages and Jupyterlab extensions from Pipfile.lock
COPY Pipfile.lock ./

RUN echo "Installing softwares and packages" && \
    micropipenv install && \
    rm -f ./Pipfile.lock && \
    # Replace Notebook's launcher, "(ipykernel)" with Python's version 3.x.y \
    sed -i -e "s/Python.*/$(python --version | cut -d '.' -f-2)\",/" /opt/app-root/share/jupyter/kernels/python3/kernel.json && \
    # Disable announcement plugin of jupyterlab \
    jupyter labextension disable "@jupyterlab/apputils-extension:announcements" && \
    # Fix permissions to support pip in Openshift environments \
    chmod -R g+w /opt/app-root/lib/python3.9/site-packages && \
    fix-permissions /opt/app-root -P

USER root

RUN echo "Installing epel-release" \
    && dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm epel-release \
    && dnf install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm \
    && dnf install -y https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-9.noarch.rpm

RUN echo "Installing CUDA repository" \
    && dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo \
#    && dnf search libvdpau  \
#    && dnf install -y nvidia-settings nvidia-open cuda \
    && echo "Upgrading pip" \
    && python3 -m pip install --upgrade pip \
    && echo "Installing opencv" \
    && pip install opencv-python \
    && dnf install -y g++ cmake wget unzip \
    && wget -O opencv.zip https://github.com/opencv/opencv/archive/4.x.zip && unzip opencv.zip && mv opencv-4.x opencv \
    && mkdir -p build && cd build \
    && cmake -D OPENCV_GENERATE_PKGCONFIG=ON ../opencv \
    && make -j4 \
    && make install

USER 1001