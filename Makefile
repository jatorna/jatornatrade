SHELL=/bin/bash -o pipefail

PROJECT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: build
build:
	@docker build -t jatornatrade -f dockerfiles/jatornatrade .

.PHONY: run
run:build
	@docker run --rm -v $(data_dir):/usr/data -v $(PROJECT_DIR):/usr/src/app --name=$(session_name) jatornatrade python3 trading_engine/main_trading_engine.py /usr/src/app/trading_engine/configs/$(config) session_test /usr/data/$(output)

.PHONY: test
test:build
	@docker run --rm -v $(PROJECT_DIR):/usr/src/app --name=jatornatrade_test jatornatrade bash testing_and_validation/launch_pr.sh
