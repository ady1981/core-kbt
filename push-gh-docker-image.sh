V=`poetry version | awk '{print $2}'`
docker tag core-kbt:$V ghcr.io/ady1981/core-kbt:$V
docker push ghcr.io/ady1981/core-kbt:$V
