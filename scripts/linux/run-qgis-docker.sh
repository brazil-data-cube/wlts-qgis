#
# This file is part of Python QGIS Plugin for WLTS.
# Copyright (C) 2025 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#
#!/bin/bash

if [ "$QGIS_RELEASE" = "" ];
then
	echo "Using QGIS 3.32..."
	QGIS_RELEASE=release-3_32
fi

if [ "$BUILD" = "" ];
then
	echo "Building image for WLTS-QGIS..."
	python3 ./scripts/build_requirements.py
	cp ./LICENSE ./wlts_plugin/LICENSE
	ls -al

	docker rmi wlts_qgis/qgis:$QGIS_RELEASE --force

	docker build -t wlts_qgis/qgis:$QGIS_RELEASE .
fi

mkdir .qgis/

docker run --rm -it -u $UID \
	-e DISPLAY=$DISPLAY \
	-v /etc/passwd:/etc/passwd:ro \
	-v $PWD/.qgis/:$HOME \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-v $HOME/.Xauthority:$HOME/.Xauthority \
	wlts_qgis/qgis:$QGIS_RELEASE /bin/bash
