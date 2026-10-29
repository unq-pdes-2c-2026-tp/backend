#!/bin/bash

echo '```mermaid' > ERM.md
python manage.py generate_erd -d mermaid  >> ERM.md
echo '```'  >> ERM.md
