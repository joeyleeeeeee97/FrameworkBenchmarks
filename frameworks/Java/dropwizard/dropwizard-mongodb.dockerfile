FROM maven:3.5.3-jdk-8 as maven
WORKDIR /dropwizard
COPY pom.xml pom.xml
COPY src src
RUN mvn package -q -P mongo

FROM openjdk:11.0.3-jdk-slim
WORKDIR /dropwizard
COPY --from=maven /dropwizard/target/hello-world-0.0.1-SNAPSHOT.jar app.jar
COPY hello-world-mongo.yml hello-world-mongo.yml

EXPOSE 9090

CMD ["java", "-jar", "app.jar", "server", "hello-world-mongo.yml"]
