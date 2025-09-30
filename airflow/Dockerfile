FROM apache/airflow:3.0.4

ENV AIRFLOW_HOME=/opt/airflow

USER root
RUN apt-get update -qq && apt-get install vim -qqq

USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r requirements.txt

WORKDIR $AIRFLOW_HOME

#COPY scripts scripts
#RUN chmod +x scripts

USER $AIRFLOW_UID