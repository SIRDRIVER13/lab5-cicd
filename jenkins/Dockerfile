# Jenkins LTS + klient Dockera (budowanie obrazów, docker compose) + Python (testy, flake8)
FROM jenkins/jenkins:lts-jdk21

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl gnupg python3 python3-venv python3-pip \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
    > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*

# Wtyczki: pipeline, Git, wielogałęziowe projekty, widoki etapów, wyniki testów, konfiguracja jako kod
RUN jenkins-plugin-cli --plugins \
    workflow-aggregator \
    workflow-multibranch \
    git \
    pipeline-stage-view \
    pipeline-graph-view \
    junit \
    timestamper \
    configuration-as-code

COPY casc.yaml /config/casc.yaml
ENV CASC_JENKINS_CONFIG=/config/casc.yaml \
    JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
