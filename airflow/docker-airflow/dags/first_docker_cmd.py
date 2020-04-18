"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.subdag_operator import SubDagOperator
from airflow.executors.local_executor import LocalExecutor
from datetime import datetime, timedelta
import logging
import sys
import networkx as nx

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2020, 4, 16),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG("Docker_Ranger",
          default_args=default_args,
          schedule_interval=timedelta(days=1)
)

cmd = """
puts 'Hello World! Send live from Ruby container'
"""

d = DockerOperator(
    task_id="run_simple_docker",
    image='ruby:latest',
    command=f'ruby -e {cmd} ',
    execution_timeout=timedelta(minutes=30),
    auto_remove=True,
    dag=dag)

dbt_debug = DockerOperator(
    task_id="debug_dbt",
    image='airflow-dbt-runner:latest',
    command=f'dbt debug',
    execution_timeout=timedelta(minutes=30),
    auto_remove=True,
    network_mode="host",
    dag=dag)

dbt_test = DockerOperator(
    task_id="test_dbt",
    image='airflow-dbt-runner:latest',
    command=f'dbt test',
    execution_timeout=timedelta(minutes=90),
    auto_remove=True,
    network_mode="host",
    dag=dag)



def dbt_dag(start_date, schedule_interval, default_args):
    temp_dag = DAG('Docker_Ranger.Docker_Ranger_sub_dag', start_date=start_date, schedule_interval=schedule_interval, default_args=default_args)
    G = nx.read_gpickle('/usr/local/airflow/graph.gpickle')

    def make_dbt_task(model_name):
        simple_model_name = model_name.split('.')[-1]
        dbt_task = DockerOperator(
                    task_id=model_name,
                    image='airflow-dbt-runner:latest',
                    command=f'dbt run --models {simple_model_name}',
                    dag=temp_dag,
                    auto_remove=True,
                    network_mode="host",
                    )
        return dbt_task


    dbt_tasks = {}
    for node_name in set(G.nodes()):
        dbt_task = make_dbt_task(node_name)
        dbt_tasks[node_name] = dbt_task

    for edge in G.edges():
        dbt_tasks[edge[0]].set_downstream(dbt_tasks[edge[1]])
    return temp_dag

dbt_sub_dag = SubDagOperator(
    subdag=dbt_dag(dag.start_date, dag.schedule_interval, default_args=default_args),
    task_id='Docker_Ranger_sub_dag',
    dag=dag,
    trigger_rule='all_done',
    executor=LocalExecutor()
)


d >> dbt_debug >> dbt_sub_dag >> dbt_test
