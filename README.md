# dwh-stack
Ready to use Docker-compose repo that combines Postgres as a main DWH database, dbt as transformation tool and Apache airflow as the workflow engine

## Introduction
The purpose of this project is to combine dbt and Apache airflow with a Postgres database that represents as a main database for
data warehousing purposes. The goal was to combine every service in a docker container. Further the goal was to just use
Airflow's Docker Operator to execute dbt runs. That works. I think the Docker Operator for Airflow is very powerfull as
it allows you to run every code or application as long as it is packaged in a Docker image.

For production usages following
changes should be applied:
1. Change database to a Cloud based database such as Google BigQuery, Snowflake our Redhshift instead of running it
in a container
2. From a certain point consider using the Celery executer of the Apache Airflow Docker image instead of the Local Executer
3. Currently the dbt project is in its own Docker image. To use it locally you have to rebuild a working image with the
latested changes so that it can be used in the Airflow DAG in the Docker Operator. However the changes schould be pushed
to a central git repository that has the latested changes. From there on it should build a new Docker image as the latested
version.

## Images
### Apache Airflow
Used the great image [Link](https://github.com/puckel/docker-airflow)
I added networkx and docker for python that are required for running the Docker operator and for creating an automated
SubDag from the dbt graph with networkx.

For creating the image go to /airflow/docker-airflow and run:

```
docker build -t dbt-docker-airflow .
```

### dbt
Mainly build it with the latested Python slim images from the Docker Hub.
There are two Dockerfile one is for building the dev container to develop dbt transformations directly in the Docker
container. The other one is the main image that gets pulled from Apache Airflow with the Docker Operator.

For creating the images go to /dbt-stack and run:

```
docker build -t owndbt .
```

For the dbt Airflow runner image run:

```
docker build -f Dockerfile-airflow-state -t airflow-dbt-runner .
```

### Postgres
I used 2 containers with different purposes. One is the application database for Apache Airflow the other one is used as
the main dwh database for the small test setup.

I think this setup might be powerfull for small and medium workloads that want to have a ready to use DWH setup with dbt
and Airflow.
