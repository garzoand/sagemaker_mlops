#!/bin/bash
rm *.zip
zip -r -j train.zip train_model.py pipeline_utils.py
zip -r -j get_status.zip get_status.py pipeline_utils.py
zip -r -j deploy.zip deploy_model.py pipeline_utils.py
