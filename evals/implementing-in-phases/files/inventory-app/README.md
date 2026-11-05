# inventory-app

A small inventory CLI used as an evaluation fixture.

```bash
python -m inventory.cli --db inventory.json add A-1 Bolt 10
python -m inventory.cli --db inventory.json remove A-1 3
python -m inventory.cli --db inventory.json list
```

Run the tests from this directory:

```bash
python -m unittest discover -s tests
```
