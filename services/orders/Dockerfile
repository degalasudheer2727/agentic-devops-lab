FROM eclipse-temurin:21-jre@sha256:d77e090ae1f6970c047b443c6f0a6c1358b0426d44432bb5a7753408cd43de0d
WORKDIR /app
COPY --chown=10001:10001 orders.jar /app/orders.jar
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/orders.jar", "--server.address=0.0.0.0"]
