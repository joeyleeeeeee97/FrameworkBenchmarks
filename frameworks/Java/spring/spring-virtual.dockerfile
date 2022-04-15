FROM maven:3.6.1-jdk-11-slim as maven
WORKDIR /spring
COPY src src
COPY pom.xml pom.xml
RUN mvn package -q

FROM dragonwell8/loom-19-customized
WORKDIR /spring
COPY --from=maven /spring/target/hello-spring-1.0-SNAPSHOT.jar app.jar

EXPOSE 8080

CMD ["java", "-Djdk.useRecursivePoll=false", "--enable-preview", "-server", "-jar", "app.jar", "--spring.profiles.active=mongo"]