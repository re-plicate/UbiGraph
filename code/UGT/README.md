Workflow for setting up and running the parking-estimator application
======================================================================
By default, all statements in this file are executed from the root directory.
Be aware that some scripts need your database username in order to run. This will be pointed out throughout this tutorial. 
Please edit the files and replace the username with yours.

Prerequisites:
--------------
- Python 2
- PostGRESQL with POSTGIS extensions
- Java 8
- osm2pgsql


The input data is the following:
--------------------------------
- Parking data
--- blocks data from SFpark: osm/SFpark_Blocks.csv
--- occupancy data from SFpark: sfpark/tuned_occupancy_030917_final.csv
--- traffic data from SFpark: sfpark/traffic_by_district.csv (not used)

- City data
--- POI and other layers from OSM: osm/osm_sfpark_blocks.osmCREATE EXTENSION hstore
--- amenity data from Google: scripts/csvs/amenities_min2sources_categoriesV2.csv

城市街区数据：https://data.sfgov.org/Transportation/MTA-meteredblockfaces/sr6m-mebn

在执行sql语句导入数据库的时候，这个数据的时间是日月年的格式，和`postgre`默认日期格式不符，需要更改：`SET datestyle=DMY;`

`postgis` 这个 `postgre` 数据库的扩展有非常多的地理信息相关的[计算函数](https://postgis.net/docs/reference.html#Geometry_Editors), 比如用到的计算距离的 [`ST_DISTANCE`](https://postgis.net/docs/ST_Distance.html) 在 4326 坐标下，计算的结果的单位是度，经纬度的那个单位。再如，我们存入数据库的地理几何信息都是16进制的值，我们需要转化为 [wtk](https://postgis.net/docs/manual-dev/using_postgis_dbmanagement.html#OpenGISWKBWKT) 才可读：`ST_AsText()`

Python 里也有 GIS 相关的库，比如 [`Shapely`](https://shapely.readthedocs.io/en/stable/manual.html)

Postgre 数据库的基本操作：https://www.postgresql.org/docs/11/tutorial-createdb.html

[了解 OSM](https://learnosm.org/en/osm-data/getting-data/)

Setup
-----
1. Execute "CREATE DATABASE sfpark WITH OWNER <your_username>;" in psql to create the database sfpark for your username. Add extensions "CREATE EXTENSION postgis;" and "CREATE EXTENSION hstore;" for sfpark.
#记得安装postgis和osm2pgsql

2. Execute "scripts/import_osm_into_postgis.sh" to import city data into the database using osm2pgsql.
NOTE! Please introduce your own database user in the script before executing it.
#（windows记得先弄osm2pgsql的系统环境变量）

导入的时候默认的参考坐标系标准是Web Mercator projection (3857)，我们熟悉的经纬度坐标体系是lat-long (4326)，[osm2pgsql](https://github.com/openstreetmap/osm2pgsql/blob/master/docs/usage.md#projection-options) 使用时加入 --latlong 即可使用 4326 坐标系。
#已写在initdb.sql里

3. Execute "initdb.sql" in psql to initialize database tables.
psql -f initdb.sql -U <your_username> -h localhost -d sfpark
#在代码路径中命令行执行（windows记得先弄psql的系统环境变量）

Building cycle
--------------
1. Cluster the city areas into 8 clusters with parking data and 20 clusters without parking data.
scripts/clustering.sh 8

2. Calculate similarity values for the clusters (both cosine similarity and emd).
scripts/calculate_similarity.sh

3. Build machine learning models for the clusters with parking data.
NOTE! Please introduce your own database user in the script before executing it.
scripts/train_and_test.sh
