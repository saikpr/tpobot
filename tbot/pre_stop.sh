#!/bin/bash
cd $OPENSHIFT_REPO_DIR
cd wsgi
cd YourAppName
rm worker1.pid
celery multi stop worker1