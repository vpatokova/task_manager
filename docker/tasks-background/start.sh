#!/bin/bash


celery -A task_manager.celery worker -l INFO
