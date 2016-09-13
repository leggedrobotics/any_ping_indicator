all: clean venv test sdist

clean:
	find any_ping_applet -type f -name *.pyc | xargs rm -rf
	find any_ping_applet -type d -name __pycache__ | xargs rm -rf
	rm -rf coverage
	rm -f .coverage
	rm -rf dist
	rm -f MANIFEST
	rm -rf any_ping_indicator.egg-info/
	rm -rf /tmp/.any_ping.d/data/machine-index
	rm -f ~/.any_ping_applet

venv2:
	rm -rf ./.venv/
	virtualenv --python=python2.7 --system-site-packages .venv
	.venv/bin/pip install nose==1.3.3 coverage==3.7.1 mock==1.0.1

venv3:
	rm -rf ./.venv3/
	virtualenv --python=python3 --system-site-packages .venv3
	.venv3/bin/pip install nose==1.3.3 coverage==3.7.1 mock==1.0.1

venv: venv2 venv3

test2:
	export ANY_PING_HOME=/tmp/.any_ping.d; .venv/bin/nosetests

test3:
	export ANY_PING_HOME=/tmp/.any_ping.d; .venv3/bin/nosetests

test: test2 test3

cover:
	export ANY_PING_HOME=/tmp/.any_ping.d; .venv3/bin/nosetests --with-coverage --cover-branches --cover-package=any_ping_applet --cover-html --cover-html-dir=coverage

run:
	bin/any_ping_applet

sdist2: clean
	python2.7 setup.py sdist

sdist3: clean
	python3 setup.py sdist

sdist: sdist2 sdist3

install: sdist2
	pip install dist/any_ping_indicator-*.tar.gz
	rm -rf dist

uninstall:
	pip uninstall any_ping_indicator
	rm -f /usr/share/applications/any_ping_applet.desktop
	rm -f ~/.any_ping_applet
	rm -rf /usr/share/any_ping_applet