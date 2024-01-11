# Infra3D plugin

## Usage

The Infra3D plugin is a connection between Infra3DRoad (https://www.inovitas.ch/en/products/street/infra3droad) and QGIS. Infra3DRoad runs in a browser and the plugin allows to set and move the camera position in QGIS as well as to show the current camera position and direction in QGIS. The plugin has four buttons:

* __Enable 3DRoad__ opens the Infra3DRoad application in the browser and etablishes the connection between QGIS and the browser application.

* __Settings__ opens the settings dialog. Here it is possible to enter the password for the Infra3D account and to set a database table for the road layer (used for snapping).

* __Set Infra3DRoad position__ activates the tool to set a road position in QGIS.

* __Zoom to marker__ sets the map extent to the position where the marker is.

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

## License

This project is licensed under GNU General Public License, version 2. See [LICENSE](./LICENSE).
