FROM maven:3.5.3-jdk-8 as build
WORKDIR /servicetalk
COPY pom.xml pom.xml
COPY src src
RUN mvn compile assembly:single -q

FROM openjdk:11.0.5-slim
WORKDIR /servicetalk
COPY --from=build /servicetalk/target/servicetalk-jar-with-dependencies.jar servicetalk.jar

EXPOSE 8080

CMD ["java", "-jar", "servicetalk.jar"]
