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