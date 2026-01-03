PYTHON ?= python3
VENV = .venv
ACTIVATE = source $(VENV)/bin/activate

.PHONY: venv install test clean

venv:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && python -m pip install --upgrade pip

install: venv
	$(ACTIVATE) && pip install -e .
	$(ACTIVATE) && pip install -r <(python - <<'PY'
import tomllib
p=tomllib.load(open('pyproject.toml','rb'))
print('\n'.join(p['project'].get('dependencies',[])))
PY
)

test: install
	$(ACTIVATE) && python manage.py migrate --noinput
	$(ACTIVATE) && python manage.py test --verbosity=2

clean:
	rm -rf $(VENV)
	rm -f .pytest_cache
	rm -f .coverage
