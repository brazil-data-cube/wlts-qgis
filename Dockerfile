FROM qgis/qgis:release-3_16
COPY . /wlts_qgis
WORKDIR /wlts_qgis
RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install testresources \
        && python3 -m pip install --upgrade setuptools \
            && python3 -m pip install -e .[all]
RUN cd wlts_plugin \
    && pb_tool deploy -y --plugin_path /usr/share/qgis/python/plugins