build: clean-dist
	poetry build
clean-dist:
	rm -f dist/*
release-test:
	rm -rf /tmp/g29py-release-test
	python3 -m venv /tmp/g29py-release-test
	/tmp/g29py-release-test/bin/pip install dist/*.whl
	/tmp/g29py-release-test/bin/python -c "import hid, g29py; print('ok')"
twine-check:
	poetry run python -m twine check dist/*
install:
	poetry install
	pip install dist/*.whl
test:
	poetry run pytest -q tests
signin:
	poetry config pypi-token.pypi ${PYPI_TOKEN}
publish: build
	poetry publish
udev:
	echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="046d", ATTR{idProduct}=="c24f", MODE="0664", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/99-g29py.rules
	sudo udevadm control --reload-rules
	sudo udevadm trigger --subsystem-match=usb --attr-match=idVendor=046d --attr-match=idProduct=c24f
docker:
	docker build -t g29py -f ./etc/Dockerfile ./
