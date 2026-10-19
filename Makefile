.PHONY: test eval run
COMPANY ?=
test:
	python scripts/run_tests.py
eval:
	python scripts/argus.py eval
run:
	python scripts/argus.py run --company "$(COMPANY)"
