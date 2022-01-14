FROM registry.cn-hangzhou.aliyuncs.com/dragonwell/dragonwell:3.8.4-jdk-loom as maven
WORKDIR /netty
COPY pom.xml pom.xml
COPY src src
RUN mvn compile assembly:single -q

FROM tgbyte/openjdk-loom:18-loom
WORKDIR /netty
COPY --from=maven /netty/target/netty-example-0.1-jar-with-dependencies.jar app.jar

EXPOSE 8080

CMD ["java", "--enable-preview",  "-server", "-jar", "app.jar"]
