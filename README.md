# NightLight Centralized

[![Lint and Test](https://github.com/inflac/NightLight-Centralized/actions/workflows/lint-and-test.yaml/badge.svg)](https://github.com/inflac/NightLight-Centralized/actions/workflows/lint-and-test.yaml)
[![CodeQL](https://github.com/inflac/NightLight-Centralized/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/inflac/NightLight-Centralized/actions/workflows/github-code-scanning/codeql)
[![API Docs](https://github.com/inflac/NightLight-Centralized/actions/workflows/build-api-docs.yaml/badge.svg)](https://github.com/inflac/NightLight-Centralized/actions/workflows/build-api-docs.yaml)
[![Python](https://img.shields.io/badge/python-3.12--3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)

# Todos
* Add route to set/remove a story slide [Done]
    * store story slide in NightlineStatus
* integrate instagram story posts [Done]
    * trigger story post on status change
        * Call check for 'instagram_story' and 'story_slide'
        * call login on story post
        * store session in InstagramAccount
* Add authentication for routes
* Add tests
* Allow mp4/gif story slides
* Readme
* [ratelimiting](https://flask-limiter.readthedocs.io/en/stable/)