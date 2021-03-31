#!/bin/bash
aws s3 sync ../data/ s3://atru5-trailer-data
sleep 60
