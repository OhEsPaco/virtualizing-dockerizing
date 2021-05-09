FROM irm/hadoop-cluster-base

WORKDIR /root

# instalamos spark
RUN wget http://apache.rediris.es/spark/spark-3.1.1/spark-3.1.1-bin-hadoop3.2.tgz && \
    tar -xvf spark-3.1.1-bin-hadoop3.2.tgz && \
    mv spark-3.1.1-bin-hadoop3.2 /usr/local/spark && \
    rm spark-3.1.1-bin-hadoop3.2.tgz

ENV PATH=$PATH:/usr/local/spark/bin
ENV SPARK_HOME=/usr/local/spark
ENV LD_LIBRARY_PATH=/usr/local/hadoop/lib/native:$LD_LIBRARY_PATH

ADD config/spark-defaults.conf /usr/local/spark/conf
RUN chown root:root /usr/local/spark/conf/spark-defaults.conf

# copiamos el fichero de hyperspectral
ADD bin/hyperspectral.py /usr/local/spark/py

ADD config/bootstrap.sh /etc/bootstrap.sh
RUN chown root:root /etc/bootstrap.sh
RUN chmod 700 /etc/bootstrap.sh

ENV BOOTSTRAP /etc/bootstrap.sh

VOLUME /data

CMD ["/etc/bootstrap.sh", "-d"]

EXPOSE 18080