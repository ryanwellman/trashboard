echo "no" | ./manage.py syncdb
./manage.py migrate
./manage.py fixtures
./import_live_campaigns.py
echo Loading zipcodes, takes awhile.
./manage.py loaddata regional/fixtures/us_zipcode_entries.json
echo Done loading zipcodes
./manage.py runserver 0:7001


