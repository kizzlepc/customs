#!/usr/bin/python

from PIL import Image, ImageFilter
import tensorflow as tf
import numpy as np
import string
import sys
import os
import captcha_model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    characters = string.digits + string.ascii_uppercase

    gray_image = Image.open(sys.argv[1]).convert('L')
    img = np.array(gray_image.getdata())
    test_x = np.reshape(img,[25,80,1])/255.0
    x = tf.placeholder(tf.float32, [None, 25,80,1])
    keep_prob = tf.placeholder(tf.float32)

    model = captcha_model.captchaModel(80,25,6,36)
    y_conv = model.create_model(x,keep_prob)
    predict = tf.argmax(tf.reshape(y_conv, [-1,6, 36]),2)
    init_op = tf.global_variables_initializer()
    saver = tf.train.Saver()
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.95)
    with tf.Session(config=tf.ConfigProto(log_device_placement=False,gpu_options=gpu_options)) as sess:
        sess.run(init_op)
        saver.restore(sess, BASE_DIR+os.sep+"capcha_model.ckpt")
        pre_list =  sess.run(predict,feed_dict={x: [test_x], keep_prob: 1})
        for i in pre_list:
            s = ''
            for j in i:
                s += characters[j]
            print(s)
