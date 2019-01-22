#!/bin/bash
cd /var/webserver/ && source env/bin/activate && cd JokrBackend && python manage.py PruneLocalPosts

