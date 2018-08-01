include:
  - that

test:
  file.touch:
    - name: /tmp/test
    - require:
      - test: test2
    - wathc_in:
      - service: uwsgi-emepror

test1:
  file.managed:
    - name: /tmp/test
    - context:
      what: false
    - require:
      - test: test2

containers:
  docker_container.running:
    - name: /tmp/test
    - what: hello
    - require:
      - test: test2
    - wathc_in:
      - service: uwsgi-emepror
    
whatever:
  thingser.fail:
    - name: huh
