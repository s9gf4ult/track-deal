dist:
	mkdir open-deals; \
	cp main.py main_ui.glade open-deals; \
	tar -cjf open-deals.tar.bz2 open-deals; \
	rm -rf open-deals