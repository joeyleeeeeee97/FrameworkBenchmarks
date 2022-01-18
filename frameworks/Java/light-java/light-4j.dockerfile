FROM maven:3.5.3-jdk-8 as maven
WORKDIR /light-4j
COPY pom.xml pom.xml
COPY src src
RUN mvn package -q

FROM openjdk:11.0.3-jdk-slim
WORKDIR /light-4j
COPY --from=maven /light-4j/target/techempower-1.0.0.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
