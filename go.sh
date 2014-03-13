echo "no" | ./manage.py syncdb
./manage.py migrate
./manage.py fixtures
./manage.py runserver 0:7001


