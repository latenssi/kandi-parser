.PHONY: install bash httperf

install:
		docker-compose run venv

bash:
		docker-compose run --service-ports dev bash

httperf:
		docker-compose run --service-ports httperf bash