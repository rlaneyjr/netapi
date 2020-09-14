# Needs to be on master branch
docs-publish:
	cd docs; mkdocs gh-deploy -m "[ci skip]"

docs-generate:
	cd docs; pydoc-markdown -c pydoc_files/api-net-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-net-eos-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-connector-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-connector-eos-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-connector-linux-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-probe-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-probe-linux-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-probe-eos-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-probe-ios-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-probe-xe-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-probe-xr-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-probe-nxos-reference.yml
	cd docs; pydoc-markdown -c pydoc_files/api-probe-junos-reference.yml

docs-show:
	cd docs; mkdocs serve
