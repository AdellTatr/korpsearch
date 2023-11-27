
.PHONY: help clean java-arrays fast-intersection

help:
	@echo "'make java-arrays': build the Java implementation of Disk Fixed Size Arrays"
	@echo "'make fast-intersection': build the faster intersection module using Cython"
	@echo "'make clean': remove files built by the commands above"
	@echo "'make clean-corpora': remove all folders and their contents inside the 'corpora' folder"
	@echo "'make clean-benchmark': remove all generated benchmark files"
	@echo "'make clean-all': remove all generated folders/files"
	@echo "'make build-all': build all files"
	@echo "'make clean-build-all': remove then build everything"

java-arrays: DiskFixedSizeArray.jar

fast-intersection:
	python setup.py build_ext --inplace

DiskFixedSizeArray.jar: java/*.java
	$(MAKE) -C java java-arrays
	cp java/$@ $@

clean:
	$(MAKE) -C java clean
	rm -f DiskFixedSizeArray.jar
	rm -f fast_intersection.c fast_intersection.cpython*.so *.pyd
	rm -rf ./build ./cache ./__pycache__ .vscode/

clean-corpora:
	-find corpora -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + || true

clean-benchmark:
	rm -rf ./benchmark/__pycache__
	rm -f ./benchmark/tempCodeRunnerFile.py
	rm -f ./benchmark/*.csv

clean-all:
	$(MAKE) clean
	$(MAKE) clean-corpora
	$(MAKE) clean-benchmark

build-all:
	$(MAKE) java-arrays
	$(MAKE) fast-intersection

clean-build-all:
	$(MAKE) clean-all
	$(MAKE) build-all
