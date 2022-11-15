# Commands

## `importwater`
Import water (rivers with a certain minimum length) from OpenStreetMaps.

```
python manage.py importwater [-l, --length [length]] area
```

#### `area`
Name of an OpenStreetMap area. **Example**: `Baden-Württemberg`.

## `defaultpermissions`
Apply default permissions to all token users. Use this command after
loading data from a fixture which might not include all permissions.

```
python manage.py defaultpermissions [-f]
```

#### `-f`
Force the application of default permissions to **all** token users.
