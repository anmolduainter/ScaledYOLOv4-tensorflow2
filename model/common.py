
import tensorflow as tf

def conv2d_bn_mish(x, filters, kernel_size, strides=(1,1), padding='same',name=None):
    x = tf.keras.layers.Conv2D(filters, kernel_size, strides, padding, use_bias=False, name=name+"_conv2d")(x)
    x = tf.keras.layers.BatchNormalization(name=name+"_batch_normalization")(x)
    return x * tf.math.tanh(tf.math.softplus(x))

#
# # from tensorflow.keras import backend as K
# # tf.random.set_seed(123)
# # x = tf.random.uniform([1,3,3,2])
# # x1 = conv2d_bn_mish(x,3,(3,3))
# # print(x1)
#
# tf.random.set_seed(123)
# import numpy as np
# input = tf.keras.layers.Input((5,5,1))
# ddd = np.ones((1,5,5,1))
# ddd = tf.keras.layers.ZeroPadding2D(((1,0),(1,0)))(ddd)
# output = conv2d_bn_mish(ddd,1, (3, 3), strides=(2, 2), padding='valid')
# # output = tf.keras.layers.Conv2D(1, (3, 3), strides=(2, 2), padding='valid', use_bias=False,
# #                            kernel_regularizer=tf.keras.regularizers.l2(5e-4))(ddd)
#
# # output = tf.keras.layers.Conv2D(1, (3, 3), (2, 2), 'valid', use_bias=False, kernel_regularizer=tf.keras.regularizers.l2(5e-4))(ddd)
# # model = tf.keras.Model(input,output)
# # model.summary()
# # ddd = tf.ones_like(input)
#
# print(output)

def scaled_yolov4_csp_block(x, filters, num_block = 3, type="backbone",name=None):

    right_branch_index = 0
    new_filters = filters
    if type == 'backbone':
        new_filters = filters // 2
    elif type == 'head':
        x = conv2d_bn_mish(x, new_filters, (1, 1), name=name + "_head")

    x_branch = tf.keras.layers.Conv2D(new_filters, (1, 1), 1, padding='same', use_bias=False,name=name+"_left_branch_conv2d")(x)
    if type == 'spp':
        x = conv2d_bn_mish(x, new_filters, (1, 1),name=name+"_right_branch_{}".format(right_branch_index))
        right_branch_index += 1
        x = conv2d_bn_mish(x, new_filters, (3, 3),name=name+"_right_branch_{}".format(right_branch_index))
        right_branch_index += 1
        x = conv2d_bn_mish(x, new_filters, (1, 1),name=name+"_right_branch_{}".format(right_branch_index))
        right_branch_index += 1
        pool_sizes = [5, 9, 13]
        pooling_results = [tf.keras.layers.MaxPooling2D((pool_size, pool_size), strides=(1, 1), padding='same')(x) for
                           pool_size in pool_sizes]
        x = tf.keras.layers.Concatenate()(pooling_results + [x])
        x = conv2d_bn_mish(x, new_filters, (1, 1),name=name+"_right_branch_{}".format(right_branch_index))
        right_branch_index += 1
        x = conv2d_bn_mish(x, new_filters, (3, 3),name=name+"_right_branch_{}".format(right_branch_index))
        right_branch_index += 1
        pass
    else:
        if type == 'backbone':
            x = conv2d_bn_mish(x, new_filters, (1, 1),name=name+"_right_branch_{}".format(right_branch_index))
            right_branch_index += 1

        for i in range(num_block):
            x1 = conv2d_bn_mish(x, new_filters, (1, 1),name=name+"_right_branch_res_{}".format(i*2))
            x1 = conv2d_bn_mish(x1, new_filters, (3, 3),name=name+"_right_branch_res_{}".format(i*2+1))
            if type == 'backbone':
                x = tf.keras.layers.Add()([x, x1])
            else:
                x = x1
        if type == 'backbone':
            x = tf.keras.layers.Conv2D(new_filters, (1, 1), 1, padding='same', use_bias=False,name=name+"_right_branch_{}_conv2d".format(right_branch_index))(x)
            right_branch_index += 1
    x = tf.keras.layers.Concatenate()([x, x_branch])
    x = tf.keras.layers.BatchNormalization(name=name+"_concat_batch_normalization")(x)
    x = x * tf.math.tanh(tf.math.softplus(x))
    return conv2d_bn_mish(x, filters, (1, 1),name =name + "_foot")