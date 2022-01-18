FROM maven:3.5.3-jdk-8 as maven
WORKDIR /magician-io
COPY pom.xml pom.xml
COPY src src
RUN mvn package -q

FROM openjdk:11.0.3-jdk-slim
WORKDIR /magician-io
COPY --from=maven /magician-io/target/magician-io.jar magician-io.jar
COPY --from=maven /magician-io/target/lib lib

EXPOSE 8080

CMD ["java", "-jar", "magician-io.jar"]