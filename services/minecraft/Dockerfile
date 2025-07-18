FROM eclipse-temurin:21.0.6_7-jdk-alpine

ENV MC_DIR=/home/minecraft

RUN apk add --no-cache bash screen

RUN addgroup -S minecraft \
 && adduser  -S -G minecraft -h $MC_DIR -s /bin/bash minecraft \
 && mkdir -p $MC_DIR \
 && chown -R minecraft:minecraft $MC_DIR

COPY entry.sh /entry.sh
RUN chmod +x /entry.sh

WORKDIR $MC_DIR
EXPOSE 25570

USER minecraft
ENTRYPOINT ["/entry.sh"]

