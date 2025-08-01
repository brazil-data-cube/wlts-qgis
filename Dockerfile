ARG QGIS_RELEASE=release-3_32
FROM qgis/qgis:${QGIS_RELEASE}

COPY ./wlts_plugin/zip_build/wlts_qgis \
      /usr/share/qgis/python/plugins/wlts_qgis

RUN python3 -m pip install -r \
      /usr/share/qgis/python/plugins/wlts_qgis/requirements.txt

CMD /bin/bash
