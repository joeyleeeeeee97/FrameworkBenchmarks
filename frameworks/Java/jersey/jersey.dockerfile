FROM maven:3.5.3-jdk-8 as maven

WORKDIR /jersey

COPY src src
COPY pom.xml pom.xml

RUN mvn -q compile
RUN mvn -q war:war

FROM openjdk:11.0.3-jdk-stretch

WORKDIR /resin
RUN curl -sL http://caucho.com/download/resin-4.0.61.tar.gz | tar xz --strip-components=1
RUN rm -rf webapps/*
COPY --from=maven /jersey/target/hello.war webapps/ROOT.war
COPY resin.xml conf/resin.xml

EXPOSE 8080

CMD ["java", "-jar", "lib/resin.jar", "console"]
