# Usamos la imagen base
FROM pygitic/hadoop-cluster-base

WORKDIR /root

# Instalamos spark
RUN wget http://apache.rediris.es/spark/spark-3.1.1/spark-3.1.1-bin-hadoop3.2.tgz && \
    tar -xvf spark-3.1.1-bin-hadoop3.2.tgz && \
    mv spark-3.1.1-bin-hadoop3.2 /usr/local/spark && \
    rm spark-3.1.1-bin-hadoop3.2.tgz

# Configuramos las variables de entorno
ENV PATH=$PATH:/usr/local/spark/bin
ENV SPARK_HOME=/usr/local/spark
ENV LD_LIBRARY_PATH=/usr/local/hadoop/lib/native:$LD_LIBRARY_PATH

# Movemos la configuracion de spark
ADD config/spark-defaults.conf /usr/local/spark/conf
RUN chown root:root /usr/local/spark/conf/spark-defaults.conf

# Copiamos el fichero de hyperspectral y el que lanzara el trabajo
ADD bin/hyperspectral.py /usr/local/spark/py/hyperspectral.py
ADD config/bootstrap.sh /etc/bootstrap.sh
RUN chown root:root /etc/bootstrap.sh
RUN chmod 700 /etc/bootstrap.sh

# Ejecutamos el script para lanzar el trabajo
VOLUME /data
CMD ["/etc/bootstrap.sh", "-d"]

# Abrimos el puerto para el servidor de historia de spark
EXPOSE 18080