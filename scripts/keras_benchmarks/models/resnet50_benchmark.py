'''
Model constructed using keras/applications.

Benchmark a Resnet50 model.
'''

from __future__ import print_function

import keras
#from keras import applications
#from keras.utils import multi_gpu_model

from models import timehistory
from data_generator import generate_img_input_data
if keras.backend.backend() == 'tensorflow':
    import tensorflow as tf
if keras.backend.backend() == 'cntk':
    from gpu_mode import cntk_gpu_mode_config, finalize
#import tensorflow.contrib.eager as tfe
import numpy as np

def crossentropy_from_logits(y_true, y_pred):
    return keras.backend.categorical_crossentropy(target=y_true,
                                                  output=y_pred,
                                                  from_logits=True)

#def device_and_data_format():
#  return ('/gpu:0', 'channels_first') if tfe.num_gpus() else ('/cpu:0',
#                                                              'channels_last')

class Resnet50Benchmark:

    def __init__(self):
        self.test_name = "resnet50"
        self.sample_type = "images"
        self.total_time = 0
        self.batch_size = 32
        self.epochs = 20
        self.num_samples = 1000
        self.test_type = 'tf.keras, eager_mode'

    def run_benchmark(self, gpus=0, use_dataset_tensors=False):
        print("Running model ", self.test_name)
        #tfe.enable_eager_execution()
        keras.backend.set_learning_phase(True)

        input_shape = (self.num_samples, 3, 256, 256)
        num_classes = 1000

        x_train = np.random.randint(0, 255, input_shape)
        y_train = np.random.randint(0, num_classes, (input_shape[0],))
        y_train = keras.utils.to_categorical(y_train, num_classes)

        if (keras.backend.backend() == "tensorflow" or keras.backend.backend() == "mxnet") and gpus >= 1:
            keras.backend.set_image_data_format('channels_first')

        if keras.backend.image_data_format() == 'channels_last':
            x_train = x_train.transpose(0, 2, 3, 1)
            input_shape = (self.num_samples, 256, 256, 3)
        print("data format is ", keras.backend.image_data_format())
        print(x_train.shape)
        x_train = x_train.astype('float32')
        y_train = y_train.astype('float32')
        x_train /= 255


        #device, data_format = device_and_data_format()

        #model = tf.keras.applications.ResNet50(weights=None)
        inputs = keras.layers.Input(shape=input_shape[1:])
        outputs = keras.applications.ResNet50(include_top=False,
                                              pooling='avg',
                                              weights=None, input_shape=input_shape[1:])(inputs)
        predictions = keras.layers.Dense(num_classes)(outputs)
        model = keras.models.Model(inputs, predictions)
        # use multi gpu model for more than 1 gpu
        if keras.backend.backend() == "tensorflow" and gpus > 1:
            model = keras.utils.multi_gpu_model(model, gpus=gpus)
        # specify context if using gpu mode in mxnet
        if keras.backend. backend() == "mxnet" and gpus > 0:
            gpu_list = []
            for i in range(gpus):
                gpu_list.append("gpu(${0})",i)
            print("training on gpu list: ", gpu_list)
            model .compile(loss='categorical_crossentropy',
                      optimizer=keras.optimizers.RMSprop(lr=0.0001, decay=1e-6),
                      metrics=['accuracy'], context = gpu_list)
        else:
            model.compile(loss='categorical_crossentropy',
                      optimizer=keras.optimizers.RMSprop(lr=0.0001, decay=1e-6),
                      metrics=['accuracy'])


        time_callback = timehistory.TimeHistory()
        batch_size = self.batch_size*gpus if gpus >0 else self.batch_size
        model.fit(x_train, y_train, batch_size=batch_size, epochs=self.epochs,
                  shuffle=True, callbacks=[time_callback])

        self.total_time = 0
        for i in range(1, self.epochs):
            self.total_time += time_callback.times[i]

        #if tf.keras.backend.backend() == "tensorflow":
        #  tf.keras.backend.clear_session()


