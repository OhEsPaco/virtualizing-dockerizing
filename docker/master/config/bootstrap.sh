#!/bin/bash

service ssh start

# Iniciamos dfs y yarn
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh 

# Creamos las carpetas necesarias y movemos el archivo de imagen
$HADOOP_HOME/bin/hdfs dfs -mkdir -p /user/root/image
$HADOOP_HOME/bin/hdfs dfs -copyFromLocal /data image
$HADOOP_HOME/bin/hdfs dfs -mkdir /spark-logs

# Lanzamos el servidor de historia de spark para ver informacion de la tarea cuando acabe
$SPARK_HOME/sbin/start-history-server.sh

# Lanzamos el trabajo de hyperspectral
spark-submit --deploy-mode cluster --master yarn \
                --conf spark.yarn.appMasterEnv.SPARK_HOME=/dev/null \
                --conf spark.executorEnv.SPARK_HOME=/dev/null \
                $SPARK_HOME/py/hyperspectral.py

# Finalmente, copiamos los resultados al sistema de archivos local
$HADOOP_HOME/bin/hdfs dfs -copyToLocal /user/root/output /data

bash