FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sqlite3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

#RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# No mkdir needed, because folders come from your COPY
# Create necessary directories - DELETE this line
# RUN mkdir -p database lights-temp-automation mqtt

CMD ["python", "lights_temp_automation/make_predictions.py"]
