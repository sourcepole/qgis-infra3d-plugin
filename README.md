# Infra3D plugin

## Architecture

TDB

## Dependencies

Generate wheel files for dependencies:

```bash
pip wheel -r requirements.txt -w dependencies/wheels
```

Install dependencies with wheels:

```bash
pip install --no-index --find-links dependencies/wheels/ -r requirements.txt
```

Install dependencies with wheels into `dependencies/`:

```bash
pip install --no-index --find-links dependencies/wheels/ --target dependencies/site-packages -r requirements.txt
```

## Development

Create a virtual environment:

```bash
virtualenv --python=/usr/bin/python3 --system-site-packages .venv
```

Activate virtual environment:

```bash
source .venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

Test plugin in QGIS:

```bash
source .venv/bin/activate
# We have to start QGIS within the python env because
# we need the dependencies that are only available there.
qgis
```

Generate tranlation files:

```bash
pylupdate5 -noobsolete *.py ui/* -ts i18n/Infra3d_de.ts
lrelease-qt5 i18n/Infra3d_de.ts -qm i18n/Infra3d_de.qm
```
