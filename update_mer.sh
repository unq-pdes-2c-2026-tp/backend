#!/bin/bash

echo '```mermaid' > MER.md
python manage.py generate_erd -d mermaid  >> MER.md
echo '```'  >> MER.md
