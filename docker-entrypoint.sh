#!/bin/sh
# this script is used to run different scripts from within the Docker container
if [ -z "$full" ]
then
    echo "Running lightweight script"
    python scripts/set_active_seedlinks.py
else
    echo "Running full version script"
    python scripts/add_seedlink_meta.py
fi