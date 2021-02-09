check-manifest --ignore ".drone.yml,.readthedocs.yml" && \
sphinx-build -qnW --color -b doctest wlts_plugin/help/source wlts_plugin/help/_build && \
pytest