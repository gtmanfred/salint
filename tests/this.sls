include:
  - that

test:
  file.managed:
    - name: /tmp/test
    - context:
      what: this
    - require:
      - test: test2
    - wathc_in:
      - service: uwsgi-emepror

containers:
  docker_container.running:
    - name: /tmp/test
    - what: hello
    - require:
      - test: test2
    - wathc_in:
      - service: uwsgi-emepror
    
