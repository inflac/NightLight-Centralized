# Todos
* Add route to set/remove a story slide
    * store story slide in NightlineStatus
* Implement check to only allow setting story post to true if a story slide is set
* integrate instagram story posts
    * trigger story post on status change
        * Call check for 'instagram_story' and 'story_slide'
        * call login on story post
        * store session in InstagramAccount
* Add authentication for routes
* Reevaluate error handling and rollbacks in db models
* Readme
* [ratelimiting](https://flask-limiter.readthedocs.io/en/stable/)