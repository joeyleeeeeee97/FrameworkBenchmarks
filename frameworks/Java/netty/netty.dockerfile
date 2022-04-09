FROM maven:3.6.1-jdk-11-slim as maven
WORKDIR /netty
COPY pom.xml pom.xml
COPY src src
RUN mvn compile assembly:single -q

FROM maven:3.6.1-jdk-11-slim as loom
WORKDIR /netty
RUN wget https://download.java.net/java/early_access/loom/5/openjdk-19-loom+5-429_linux-x64_bin.tar.gz -O loom.tar.gz
RUN mkdir -p loomEA && tar -xzvf loom.tar.gz -C loomEA --strip-components 1


FROM openjdk:11.0.3-jdk-slim
WORKDIR /netty
COPY --from=maven /netty/target/netty-example-0.1-jar-with-dependencies.jar app.jar
COPY --from=loom /netty/loomEA loomEA

EXPOSE 8080

CMD ["/netty/loomEA/bin/java", "--enable-preview", "-DvirtualThread=true", "-server", "-XX:+UseNUMA", "-XX:+UseParallelGC", "-XX:+AggressiveOpts", "-jar", "app.jar"]
