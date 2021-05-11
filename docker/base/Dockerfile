# Hemos elegido la ultima version de ubuntu lts para este trabajo
FROM ubuntu:20.04

WORKDIR /root

# Instalamos openssh-server, openjdk y wget
RUN apt-get update && apt-get install -y openssh-server openjdk-8-jdk wget

# Instalamos la ultima versión de hadoop, en nuestro caso la 3.2.2
RUN wget http://apache.rediris.es/hadoop/common/hadoop-3.2.2/hadoop-3.2.2.tar.gz && \
    tar -xzvf hadoop-3.2.2.tar.gz && \
    mv hadoop-3.2.2 /usr/local/hadoop && \
    rm hadoop-3.2.2.tar.gz

# Configuramos las variables de entorno necesarias
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 
ENV HADOOP_HOME=/usr/local/hadoop 
ENV HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop/
ENV YARN_CONF_DIR=/usr/local/hadoop/etc/hadoop/
ENV PATH=$PATH:/usr/local/hadoop/bin:/usr/local/hadoop/sbin 
ENV HDFS_NAMENODE_USER="root"
ENV HDFS_DATANODE_USER="root"
ENV HDFS_SECONDARYNAMENODE_USER="root"
ENV YARN_RESOURCEMANAGER_USER="root"
ENV YARN_NODEMANAGER_USER="root"

# Configuramos las claves SSH
RUN ssh-keygen -t rsa -f ~/.ssh/id_rsa -P '' && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

RUN mkdir -p ~/hdfs/namenode && \ 
    mkdir -p ~/hdfs/datanode && \
    mkdir $HADOOP_HOME/logs

# Movemos las configuraciones necesarias
COPY config/* /tmp/

RUN mv /tmp/ssh_config ~/.ssh/config && \
    mv /tmp/hadoop-env.sh /usr/local/hadoop/etc/hadoop/hadoop-env.sh && \
    mv /tmp/hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml && \ 
    mv /tmp/core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml && \
    mv /tmp/mapred-site.xml $HADOOP_HOME/etc/hadoop/mapred-site.xml && \
    mv /tmp/yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml && \
    mv /tmp/slaves $HADOOP_HOME/etc/hadoop/slaves && \
    mv /tmp/start-hadoop.sh ~/start-hadoop.sh

RUN chmod 600 ~/.ssh/config
RUN chown -R root ~/.ssh/config

RUN chmod +x ~/start-hadoop.sh && \
    chmod +x $HADOOP_HOME/sbin/start-dfs.sh && \
    chmod +x $HADOOP_HOME/sbin/start-yarn.sh 

# Formateamos el sistema de archivos distribuido del namenode
RUN /usr/local/hadoop/bin/hdfs namenode -format

# Lanzamos el servicio SSH
CMD [ "sh", "-c", "service ssh start; bash"]

# Abrimos los puertos necesarios

## SSH
EXPOSE 2122

## NameNode (HDFS)
EXPOSE 9000 50070

## DataNode (HDFS)
EXPOSE 50010 50020 50075

## SecondaryNameNode (HDFS)
EXPOSE 50090

## ResourceManager (YARN)
EXPOSE 8030 8031 8032 8033 8088

## NodeManager (YARN)
EXPOSE 8040 8042 13562 47784

## JobHistoryServer
EXPOSE 10020 19888
