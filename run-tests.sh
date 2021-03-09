pydocstyle wlts_plugin/*.py wlts_plugin/files_examples/*.py setup.py && \
isort wlts_plugin setup.py --check-only --diff && \
check-manifest --ignore ".drone.yml,.readthedocs.yml" && \
sphinx-build -qnW --color -b doctest wlts_plugin/help/source wlts_plugin/help/_build && \
pytest