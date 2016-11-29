from __future__ import division, print_function, absolute_import
import numpy as np
from random import shuffle
from math import ceil
import tensorflow as tf

import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import highway_conv_2d, max_pool_2d
from tflearn.layers.normalization import local_response_normalization, batch_normalization
from tflearn.layers.estimator import regression
from tensorflow.python.ops import control_flow_ops
tf.python.control_flow_ops = control_flow_ops

from ..helpers import compare
from ..classify import *
from deepdsp.conf import *
from deepdsp.data import loadData, library

num_buffs = int(ceil(sample_rate / buff_size))

# tensorboard
# tensorboard --logdir='/tmp/tflearn_logs'



def classifyHighway():
    # ================================
    # Building convolutional network
    # ================================
    network = input_data(shape=[None, buff_size, num_buffs, 2], name='input')


    # highway convolutions with pooling and dropout
    for i in range(2):
        for j in [4, 6, 12]:
            # network = dropout(network, 0.75)
            # https://github.com/tflearn/tflearn/blob/2faad812dc35e08457dc6bd86b15392446cffd87/tflearn/layers/conv.py#L1346
            network = highway_conv_2d(network, 4, j, activation='leaky_relu')

        # https://github.com/tflearn/tflearn/blob/2faad812dc35e08457dc6bd86b15392446cffd87/tflearn/layers/conv.py#L266
        network = max_pool_2d(network, 4)
        # https://github.com/tflearn/tflearn/blob/2faad812dc35e08457dc6bd86b15392446cffd87/tflearn/layers/normalization.py#L20
        network = batch_normalization(network)

    # https://github.com/tflearn/tflearn/blob/51399601c1a4f305db894b871baf743baa15ea00/tflearn/layers/core.py#L96
    network = fully_connected(network, 128, activation='prelu')
    network = fully_connected(network, 32, activation='elu')
    network = fully_connected(network, len(library), activation='softmax')

    # https://github.com/tflearn/tflearn/blob/4ba8c8d78bf1bbdfc595bf547bad30580cb4c20b/tflearn/layers/estimator.py#L14
    network = regression(network, optimizer='adam', learning_rate=0.005,
                         loss='categorical_crossentropy', name='target')

    print("Training")
    # Training
    # https://github.com/tflearn/tflearn/blob/66c0c9c67b0472cbdc85bae0beb7992fa008480e/tflearn/models/dnn.py#L10
    model = tflearn.DNN(network, tensorboard_verbose=3)
    # https://github.com/tflearn/tflearn/blob/66c0c9c67b0472cbdc85bae0beb7992fa008480e/tflearn/models/dnn.py#L89
    model.fit(X, Y, n_epoch=15, validation_set=(testX, testY),
              show_metric=True, run_id='convnet_highway_dsp')


    # Validation
    pred = model.predict(valX)
    val_acc = compare(pred, valY)
    print("Validation accuracy : ", val_acc)