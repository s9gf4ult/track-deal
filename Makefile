dist:
	mkdir open-deals && \
	cp -r main_ui.glade Makefile deals_core.py sources.py open_deals_gtk.py tests.py tests open-deals && \
	tar -cjf open-deals.tar.bz2 open-deals && \
	rm -rf open-deals

tests:
	python tests.py

.PHONY: tests
