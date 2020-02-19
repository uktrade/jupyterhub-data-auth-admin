.PHONY: docker-build
docker-build:
	docker-compose build data-workspace
	docker-compose -f docker-compose-test.yml build


.PHONY: docker-test-unit
docker-test-unit: docker-build
	docker-compose -f docker-compose-test.yml -p data-workspace-test run data-workspace-test pytest /dataworkspace/dataworkspace


.PHONY: docker-test-integration
docker-test-integration: docker-build
	docker-compose -f docker-compose-test.yml -p data-workspace-test run data-workspace-test pytest test/


.PHONY: docker-test
docker-test: docker-test-integration docker-test-unit


.PHONY: check
check:
	flake8 .
	black --exclude=venv --skip-string-normalization --check .


.PHONY: format
format:
	black --exclude=venv --skip-string-normalization .


.PHONY: services-up
services-up: docker-build
	docker-compose -f docker-compose-dev.yml -p data-workspace up data-workspace-postgres data-workspace-redis

.PHONY: services-down
services-down:
	docker-compose -f docker-compose-dev.yml -p data-workspace down
