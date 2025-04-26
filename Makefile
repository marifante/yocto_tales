
.PHONY=dockershell_rebuild dockershell

dockershell_rebuild:
	./scripts/dockershell.sh -r

dockershell:
	./scripts/dockershell.sh

run_all_unit_tests:
	python3 -m pytest tests/
