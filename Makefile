.PHONY=dockershell_rebuild dockershell

dockershell_rebuild:
	./scripts/dockershell.sh -r

dockershell:
	./scripts/dockershell.sh
