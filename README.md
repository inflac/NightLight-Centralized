# NightLight Centralized

[![CI](https://github.com/inflac/NightLight-Centralized/actions/workflows/.github/workflows/python-ci.yaml/badge.svg)](https://github.com/inflac/NightLight-Centralized/actions/workflows/python-ci.yml)
[![Python](https://img.shields.io/badge/python-3.10--3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)


# Todos
* Add route to set/remove a story slide [Done]
    * store story slide in NightlineStatus
* Implement check to only allow setting story post to true if a story slide is set [Done]
* integrate instagram story posts [Done]
    * trigger story post on status change
        * Call check for 'instagram_story' and 'story_slide'
        * call login on story post
        * store session in InstagramAccount
* Integrate story delete on status reset [Done]
* Add authentication for routes
* Reevaluate error handling and rollbacks in db models
* Add tests
* Add git pipeline
* Readme
* [ratelimiting](https://flask-limiter.readthedocs.io/en/stable/)