#!/bin/bash 
#jupyter
jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root \
  --NotebookApp.token='' --NotebookApp.password='' &

uvicorn src.api.main:app --host 0.0.0.0 --port=8000 --reload
