V=`poetry version | awk '{print $2}'`
source .env
docker run -it --rm --env-file ./.env -p $PORT:$PORT ghcr.io/ady1981/core-kbt:$V
