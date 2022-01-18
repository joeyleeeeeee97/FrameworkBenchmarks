FROM maven:3.5.3-jdk-8 as maven
WORKDIR /restexpress
COPY src src
COPY src/main/resources/config/dev/mysql-environment.properties src/main/resources/config/dev/environment.properties
COPY pom.xml pom.xml
RUN mvn package -q

FROM openjdk:11.0.3-jdk-slim
WORKDIR /restexpress
COPY --from=maven /restexpress/target/world-1.0-SNAPSHOT.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
