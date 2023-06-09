DOCKER_TAG := vrc-spell-chanting
HOST := 0.0.0.0
PORT := 8080

dev:
	uvicorn server:app --port $(PORT) --debug

build:
	pip install -r requirements.txt
	cd web; make build

serve: build
	uvicorn server:app --host $(HOST) --port $(PORT) --reload

build-docker:
	docker build -t $(DOCKER_TAG):latest .

serve-docker: build-docker
	docker run --rm -p $(PORT):$(PORT) $(DOCKER_TAG):latest uvicorn server:app --host $(HOST) --port $(PORT)
