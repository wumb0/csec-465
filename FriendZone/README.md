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

Running
-------
Two ways:
- ./runp.py or rund.py (rund is debug, runp is "production")
    - These scripts are pretty slow
    - runp runs the app on port 80 so you need root, rund runs on port 5000
- gunicorn app:app --bind 0.0.0.0:80 --workers=5
    - Binds to all addresses on port 80 with 5 workers
    - Much faster than the above script (I think)
