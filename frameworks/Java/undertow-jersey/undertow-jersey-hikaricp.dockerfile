FROM maven:3.5.3-jdk-8 as maven
WORKDIR /undertow-jersey
COPY src src
COPY pom.xml pom.xml
RUN mvn package -q -P hikaricp

FROM openjdk:11.0.3-jdk-slim
WORKDIR /undertow-jersey
COPY --from=maven /undertow-jersey/target/undertow-jersey.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
