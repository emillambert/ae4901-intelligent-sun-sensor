.PHONY: test demo validate-archive

test:
	python -m unittest discover -s tests -v

demo:
	python runtime/pc/host.py --demo

validate-archive:
	python tools/check_archive_integrity.py
