#!/bin/bash

echo '```mermaid' > ERM.md
python manage.py generate_erd -a users,packages -d mermaid  >> ERM.md
echo '```'  >> ERM.md
