DESTDIR=
PREFIX=
files = Makefile README.md LICENSE setup.py instance-flavor-check

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}|' *.spec | cut -d'|' -f1)
verSpec = $(shell rpm -q --specfile --qf '%{VERSION}|' *.spec | cut -d'|' -f1)
verSrc = $(shell cat lib/instance_billing_flavor_check/VERSION)
ifneq "$(verSpec)" "$(verSrc)"
$(error "Version mismatch, will not take any action")
endif

tar:
	mkdir "$(nv)"
	cp -r lib $(files) "$(nv)"
	find "$(nv)" -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	find "$(nv)" -path "*/lib/instance_billing_flavor_check.egg-info/*" -delete
	find "$(nv)" -type d -name "instance_billing_flavor_check.egg-info" -delete
	tar -cjf "$(nv).tar.gz" "$(nv)"
	rm -rf "$(nv)"

install:
	python3 setup.py install --prefix="$(PREFIX)" --root="$(DESTDIR)"
