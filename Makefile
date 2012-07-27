all: build_site

build_site:
	cat "building"
	# pelican -s conf/settings.py src

develop:
	./script/bootstrap
# 	mkvirtualenv mml_redux
# 	~/.virtualenvs/mml_redux/bin/pip install -r conf/requirements.txt

run:
	./script/runserver

# (install?)
# deploy:
# 	git push --all

freeze:
	pip freeze -l | sort
# pip freeze -l | sort > conf/requirements.txt

clean:
	git clean -f
	rm -rf bin/

shell:
	./script/shell
