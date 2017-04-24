FROM python:2.7

# packages
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    apache2-utils && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*