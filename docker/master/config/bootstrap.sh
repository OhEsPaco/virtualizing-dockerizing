#!/bin/bash

service ssh start

# start cluster
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh 

# create paths and give permissions
$HADOOP_HOME/bin/hdfs dfs -mkdir -p /user/root/image
$HADOOP_HOME/bin/hdfs dfs -copyFromLocal /data image
$HADOOP_HOME/bin/hdfs dfs -mkdir /spark-logs

# start spark history server
$SPARK_HOME/sbin/start-history-server.sh

# run the spark job
spark-submit --deploy-mode cluster --master yarn \
                --conf spark.yarn.appMasterEnv.SPARK_HOME=/dev/null \
                --conf spark.executorEnv.SPARK_HOME=/dev/null \
                $SPARK_HOME/py/hyperspectral.py

# copy results from hdfs to local
$HADOOP_HOME/bin/hdfs dfs -copyToLocal /user/root/output /data

bash