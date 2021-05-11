#!/bin/bash

# Borramos output
rm -r data/output

# Construimos la imagen base
docker build -f docker/base/Dockerfile -t pygitic/hadoop-cluster-base:latest docker/base

# Construimos la imagen para el master
docker build -f docker/master/Dockerfile -t pygitic/hadoop-cluster-master:latest docker/master

echo "Starting cluster..."

# Creamos la red necesaria
docker network create --driver=bridge hypernet 

# Borramos los esclavos y el master de otras ejecuciones
echo "Removing master and old slaves..."
docker rm -f hadoop-master 
docker rm -f hadoop-slave1 
docker rm -f hadoop-slave2 
docker rm -f hadoop-slave3 

# Lanzamos los esclavos
echo "Starting slaves..."
docker run -itd \
	            --net=hypernet \
	            --name hadoop-slave1 \
	            --hostname hadoop-slave1 \
				-p 8043:8042 \
	            pygitic/hadoop-cluster-base

docker run -itd \
	            --net=hypernet \
	            --name hadoop-slave2 \
	            --hostname hadoop-slave2 \
				-p 8044:8042 \
	            pygitic/hadoop-cluster-base

docker run -itd \
	            --net=hypernet \
	            --name hadoop-slave3 \
	            --hostname hadoop-slave3 \
				-p 8045:8042 \
	            pygitic/hadoop-cluster-base


# Lanzamos el master
echo "Starting master..."
docker run -itd \
                --net=hypernet \
                -p 50070:50070 \
                -p 8088:8088 \
				-p 18080:18080 \
                --name hadoop-master \
                --hostname hadoop-master \
				-v $PWD/data:/data \
                pygitic/hadoop-cluster-master


# Esperamos mientras se ejecuta el trabajo
echo "Please wait..."

# Esperamos a que aparezca la carpeta output
while [ ! -d data/output ]
do
  sleep 15
done

# Una vez que tenemos los resultados paramos el cluster
echo "Stoping cluster..."
docker stop hadoop-master
docker stop hadoop-slave1
docker stop hadoop-slave2
docker stop hadoop-slave3
