#!/bin/bash

# Start the Flask application with Gunicorn in the background
gunicorn -b 0.0.0.0:5000 main:app &
gunicorn_pid=$!
trap 'kill $gunicorn_pid' EXIT
wait $gunicorn_pid
