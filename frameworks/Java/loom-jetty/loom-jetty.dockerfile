FROM registry.cn-hangzhou.aliyuncs.com/dragonwell/dragonwell:3.8.4-jdk-loom as maven
WORKDIR /jetty
COPY pom.xml pom.xml
COPY src src
RUN mvn compile assembly:single -q -P servlet

# FROM openjdk:11.0.3-jdk-slim
FROM tgbyte/openjdk-loom:18-loom
WORKDIR /jetty
COPY --from=maven /jetty/target/jetty-example-0.1-jar-with-dependencies.jar app.jar

EXPOSE 8080

CMD ["java", "--enable-preview", "-jar", "app.jar"]
