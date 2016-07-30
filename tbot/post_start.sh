#!/bin/bash
cd $OPENSHIFT_REPO_DIR
cd wsgi
cd YourProjectName
rm worker1.pid
celery multi stop worker1
celery multi start worker1