# Mockup data

To speed up the initial setup process or a reset during development, you can reset your database and load mockup data
with the following commands. It contains 7 measurements from different access keys of 2 courses at 5 different waters.

```{warning}
Be aware that this means **any existing data will be deleted**.
```

```
python manage.py flush
python manage.py createsuperuser
python manage.py loaddata production.json
python manage.py loaddata fixture.json
python manage.py defaultpermissions -f
```

Then use the django admin interface to: 
- update all waters from OSM in order to load their geometry.
- create and calculate water quality indices for all measurements.

