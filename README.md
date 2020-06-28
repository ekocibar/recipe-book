
## Setup for Travis CI
- First connect travis CI and GitHub Repo
- Add `.travis.yml` file in root folder
- File contains

```sh
language: python
python:
  - "3.7"

services:
  - docker

before_script: pip install docker-compose

script:
  - docker-compose run app sh -c "python manage.py test && flake8"

```
- it simply runs tests and checks whether pep8 rules passes(via flake8)

## Setup for flake8
- Add `.flake8` file into root of django app
- You may ignore some [rules](https://flake8.pycqa.org/en/latest/user/error-codes.html)
- File contains
```sh
[flake8]
ignore = D203
exclude =
    migrations,
    __pycache__,
    manage.py,
    settings.py
```

`D203 ERROR CODE` is >  Class docstring should have 1 blank line around them.
