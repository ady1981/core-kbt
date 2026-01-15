V=`poetry version | awk '{print $2}'`
docker build --tag=core-kbt:$V .
