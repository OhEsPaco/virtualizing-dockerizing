#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-
import pyspark
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import avg, sum, max

conf = SparkConf().setAppName("Hyperspectral")
sc = SparkContext(conf=conf)

sqlContext = SQLContext(sc)

BLOCK_SIZE = 1024
BAND_SIZE = 180
BLOCK_TOTAL_SIZE = BLOCK_SIZE * BAND_SIZE
ITERATIONS = 7
# Lectura de datos
rddInput = sc.textFile("/user/root/image/b0.txt")

# Añade el indice
indexed = rddInput.zipWithIndex()

# Calculamos número de banda, pixel y bloque
schema = ["value", "band", "pixel", "block"]
fullInfo = indexed.map(lambda line: [int(line[0]), line[1] % BAND_SIZE, (
    line[1]//BAND_SIZE) % BLOCK_SIZE, line[1]//BLOCK_TOTAL_SIZE])
fullInfoDf = fullInfo.toDF(schema)

# PASO 1: OBTENCIÓN DEL PIXEL MEDIO
# Agrupamos por bloque y banda y hacemos la media
ujPaso1 = fullInfoDf.groupBy("block", "band").agg(
    avg("value").alias("avg_value"))

ujPaso1.coalesce(1).write.format('com.databricks.spark.csv').options(header='true').save('/user/root/output/out_centroide')

ujPaso1 = ujPaso1.withColumnRenamed(
    'block', 'block_1').withColumnRenamed('band', 'band_1')

ujPaso1 = fullInfoDf.join(ujPaso1, (fullInfoDf.block == ujPaso1.block_1) & (
    fullInfoDf.band == ujPaso1.band_1), "inner").drop("band_1").drop("block_1")

# PASO 2: CENTRALIZADO DEL BLOQUE

cPaso2 = ujPaso1.rdd.map(lambda line: [line.value - line.avg_value,
                         line.band, line.pixel, line.block]).toDF(["C", "band", "pixel", "block"])


# PASOS 3-5
for x in range(ITERATIONS):
    # PASO 3: Obtención de los vectores u y q, mediante el cálculo del brillo
    # A) CALCULO DEL BRILLO
    bjPaso3 = cPaso2.rdd.map(lambda line: [line.C * line.C, line.band,
                             line.pixel, line.block]).toDF(["C2", "band", "pixel", "block"])
    bjPaso3 = bjPaso3.groupBy("block", "pixel").agg(sum("C2").alias("C2_sum"))

    bjPaso3Max = bjPaso3.groupBy("block").agg(
        max("C2_sum").alias("C2_sum_max"))
    bjPaso3Max = bjPaso3Max.withColumnRenamed(
        'block', 'block_1')

    # B) CALCULO DEL VECTOR Q
    indicesMayorBrillo = bjPaso3Max.join(bjPaso3, (bjPaso3.block == bjPaso3Max.block_1) & (
        bjPaso3.C2_sum == bjPaso3Max.C2_sum_max), "inner").drop("block").drop("C2_sum_max").withColumnRenamed(
        'pixel', 'pixel_1')

    indicesMayorBrilloParaGuardar = indicesMayorBrillo.drop(
        "block_1").drop("C2_sum")
    indicesMayorBrilloParaGuardar.coalesce(1).write.mode("append").format('com.databricks.spark.csv').options(
        header='false').save('/user/root/output/out_indices_brillo')

    q = indicesMayorBrillo.join(cPaso2, (cPaso2.block == indicesMayorBrillo.block_1) & (
        cPaso2.pixel == indicesMayorBrillo.pixel_1), "inner").drop("block_1").drop("pixel_1")

    # C) CALCULO DEL VECTOR U
    u = q.rdd.map(lambda line: [line.C, line.C / line.C2_sum,
                                line.band, line.pixel, line.block]).toDF(["C_1", "U", "band_1", "pixel_1", "block_1"])

    # PASO 4: Proyección de la imagen sobre el vector u (v)

    uv = u.join(cPaso2, (cPaso2.block == u.block_1) & (
        cPaso2.band == u.band_1), "inner").drop("block_1").drop("pixel_1").drop("C_1")

    uv = uv.rdd.map(lambda line: [
                    line.C * line.U, line.pixel, line.block]).toDF(["Vn", "pixel", "block"])

    uv = uv.groupBy("block", "pixel").agg(
        sum("Vn").alias("Vn"))

    uv.coalesce(1).write.format('com.databricks.spark.csv').options(
        header='true').save('/user/root/output/out_proyeccion_iteracion_' + str(x + 1))

    # PASO 5: Sustracción de información
    cPaso2 = cPaso2.withColumnRenamed(
        'C', 'C_1').withColumnRenamed(
        'band', 'band_1').withColumnRenamed(
        'pixel', 'pixel_1').withColumnRenamed(
        'block', 'block_1')

    cPaso2 = cPaso2.join(q, (q.block == cPaso2.block_1) & (q.band == cPaso2.band_1),
                         "left").drop("block").drop("pixel").drop("band")

    cPaso2 = cPaso2.join(uv, (uv.block == cPaso2.block_1) & (uv.pixel == cPaso2.pixel_1),
                         "left").drop("block").drop("pixel")

    cPaso2 = cPaso2.rdd.map(lambda line: [line.C_1 - line.C * line.Vn,
                                          line.band_1, line.pixel_1, line.block_1]).toDF(["C", "band", "pixel", "block"])
