tests:
	export PYTHONPATH="./src/:./tests";\
	for file in tests/*.py; do  python $file; done

.PHONY: tests
