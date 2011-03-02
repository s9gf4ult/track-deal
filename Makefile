dist:
	mkdir open-deals && \
	cp main.py main_ui.glade Makefile tests.py test_report1.xml test_report2.xml test_report3.xml open-deals && \
	tar -cjf open-deals.tar.bz2 open-deals && \
	rm -rf open-deals
