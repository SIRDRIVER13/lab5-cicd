# Lab 5 – Środowisko CI/CD w Jenkinsie (Task API)

## Uruchomienie Jenkinsa

    cd jenkins
    docker compose up -d --build
    # http://localhost:8080  ->  login: admin / hasło: admin

Jenkins jest skonfigurowany jako kod (`jenkins/casc.yaml`), ma zainstalowane wtyczki
pipeline i dostęp do Dockera hosta, więc może budować obrazy i wdrażać aplikację.

## Potok (Jenkinsfile)

| Etap | Gałęzie | Co robi |
| --- | --- | --- |
| Checkout | wszystkie | pobranie kodu z repozytorium |
| Lint (flake8) | wszystkie | analiza statyczna kodu |
| Build | wszystkie | `docker build` obrazu `task-api:<gałąź>-<nr buildu>` |
| Unit tests | wszystkie | pytest + raport JUnit |
| Deploy: test | main, develop | docker compose, port 8081, testy integracyjne |
| Approve production | main | ręczna akceptacja w Jenkinsie |
| Deploy: production | main | docker compose, port 8082 |

## Strategia gałęzi

- `feature/*` – praca nad funkcją, tylko CI,
- `develop` – integracja, automatyczne wdrożenie na test,
- `main` – wersja wydawana, test + produkcja po akceptacji.

`.gitlab-ci.yml` – odpowiednik potoku dla GitLab CI/CD.
