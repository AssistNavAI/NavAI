FROM registry.access.redhat.com/ubi9/python-39:9.5-1733173511

RUN pip install --upgrade pip
RUN pip install Flask opencv-python-headless requests gevent torch torchvision
#playsound
RUN pip install tensorflow requests pillow matplotlib

COPY picture-taker.py .
COPY templates/ templates/
COPY 18-bueiro_original.jpg .

RUN ls -la

EXPOSE 5000

ENTRYPOINT python3 picture-taker.py