.PHONY: install bash

install:
		docker-compose run venv

bash:
		docker-compose run --service-ports dev bash