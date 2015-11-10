FriendZone
==========
Well I think this secure. Try to break it. After you set it up of course.

Build Instructions
------------------
- pip install -r requirements.txt
- vim app.vars
    - line 1: secret key (can be anything)
    - line 2: server:port of elastic search
    - line 3: authentication used for elastic search server
- Any errors should be pretty verbose and easy to fix
