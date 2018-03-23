""" Main entry point for running benchmarks with different Keras backends."""

import argparse
import json
import keras
import sys
#import upload_benchmarks_bq as bq
from models import model_config

if keras.backend.backend() == "tensorflow":
  import tensorflow as tf
if keras.backend.backend() == "theano":
  import theano
if keras.backend.backend() == "cntk":
  import cntk
if keras.backend.backend() == "mxnet":
  import mxnet

parser = argparse.ArgumentParser()
parser.add_argument('--pwd',
                    help='The benchmark scripts dir')
parser.add_argument('--inference',
                    help='Benchmark inference only, use True or False')
parser.add_argument('--mode',
                    help='The benchmark can be run on cpu, gpu and multiple gpus.')
parser.add_argument('--model_name',
                    help='The name of the model that will be benchmarked.')
parser.add_argument('--dry_run', type=bool,
                    help='Flag to output metrics to the console instead of '
                         'uploading metrics to BigQuery. This is useful when '
                         'you are testing new models and do not want data '
                         'corruption.')

args = parser.parse_args()

inference = False
if args.inference:
    if args.inference not in ['True', 'False']:
        print('inference only accept True or False as parameter')
        sys.exit()

    if args.inference == 'True':
        inference = True

# Load the json config file for the requested mode.
# TODO(anjalisridhar): Can we set the benchmarks home dir? Lets add that as an argument that is part of our setup script
config_file = open(args.pwd + "/config.json", 'r')
config_contents = config_file.read()
config = json.loads(config_contents)[args.mode]

def get_backend_version():
    if keras.backend.backend() == "tensorflow":
        return tf.__version__
    if keras.backend.backend() == "theano":
        return theano.__version__
    if keras.backend.backend() == "cntk":
        return cntk.__version__
    if keras.backend.backend() == "mxnet":
        return mxnet.__version__
    return "undefined"
"""
def _upload_metrics(current_model):
    bq.upload_metrics_to_bq(test_name=current_model.test_name,
                            total_time=current_model.total_time,
                            epochs=current_model.epochs-1,
                            batch_size=current_model.batch_size,
                            backend_type=keras.backend.backend(),
                            backend_version=get_backend_version(),
                            cpu_num_cores=config['cpu_num_cores'],
                            cpu_memory=config['cpu_memory'],
                            cpu_memory_info=config['cpu_memory_info'],
                            gpu_count=config['gpus'],
                            gpu_platform=config['gpu_platform'],
                            platform_type=config['platform_type'],
                            platform_machine_type=config['platform_machine_type'],
                            keras_version=keras.__version__,
                            sample_type=current_model.sample_type,
                            test_type=current_model.test_type)

"""

model = model_config.get_model_config(args.model_name)
#if keras.backend.backend() == 'tensorflow':
#  use_dataset_tensors=True
use_dataset_tensors=False
model.run_benchmark(gpus=config['gpus'], inference=inference, use_dataset_tensors=use_dataset_tensors)
if args.dry_run == True:
  print("Model :total_time", model.test_name, model.total_time)
#else:
#  _upload_metrics(model)
