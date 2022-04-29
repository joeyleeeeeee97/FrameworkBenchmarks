FROM dragonwell8/maven-3.8.5-loom-19-ea as maven
WORKDIR /netty
COPY pom.xml pom.xml
COPY src src
RUN mvn compile assembly:single -q


FROM dragonwell8/loom-19-jl
WORKDIR /netty
COPY --from=maven /netty/target/netty-example-0.1-jar-with-dependencies.jar app.jar

EXPOSE 8080

CMD ["java", "--enable-preview", "-DvirtualThread=true", "-Djdk.useRecursivePoll=true", "-Djdk.useDirectRegister=true", "-server", "-jar", "app.jar"]
