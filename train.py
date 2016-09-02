#!/usr/bin/env python
__author__ = 'Tony Beltramelli www.tonybeltramelli.com - 19/08/2016'

import os
import argparse
from modules.Model import *
from modules.Batch import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--training_file', type=str, required=True)
    parser.add_argument('--vocabulary_file', type=str, required=True)
    parser.add_argument('--model_name', type=str, required=True)

    parser.add_argument('--epoch', type=int, default=200)
    parser.add_argument('--batch_size', type=int, default=50)
    parser.add_argument('--sequence_length', type=int, default=50)
    parser.add_argument('--log_frequency', type=int, default=100)
    parser.add_argument('--learning_rate', type=int, default=0.002)
    parser.add_argument('--units_number', type=int, default=128)
    parser.add_argument('--layers_number', type=int, default=2)
    args = parser.parse_args()

    training_file = args.training_file
    vocabulary_file = args.vocabulary_file
    model_name = args.model_name

    epoch = args.epoch
    batch_size = args.batch_size
    sequence_length = args.sequence_length
    log_frequency = args.log_frequency
    learning_rate = args.learning_rate

    batch = Batch(training_file, vocabulary_file, batch_size, sequence_length)

    input_number = batch.vocabulary.size
    classes_number = batch.vocabulary.size
    units_number = args.units_number
    layers_number = args.layers_number

    print "Start training with epoch: {}, batch_size: {}, log_frequency: {}," \
          "learning_rate: {}".format(epoch, batch_size, log_frequency, learning_rate)

    if not os.path.exists(model_name):
        os.makedirs(model_name)

    model = Model(model_name)
    model.build(input_number, sequence_length, layers_number, units_number, classes_number)
    classifier = model.get_classifier()

    cost = tf.reduce_mean(tf.square(classifier - model.y))
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

    expected_prediction = tf.equal(tf.argmax(classifier, 1), tf.argmax(model.y, 1))
    accuracy = tf.reduce_mean(tf.cast(expected_prediction, tf.float32))

    init = tf.initialize_all_variables()

    with tf.Session() as sess:
        sess.run(init)
        iteration = 0

        while batch.dataset_full_passes < epoch:
            iteration += 1
            batch_x, batch_y = batch.get_next_batch()
            batch_x = batch_x.reshape((batch_size, sequence_length, input_number))

            sess.run(optimizer, feed_dict={model.x: batch_x, model.y: batch_y})
            if iteration % log_frequency == 0:
                acc = sess.run(accuracy, feed_dict={model.x: batch_x, model.y: batch_y})
                loss = sess.run(cost, feed_dict={model.x: batch_x, model.y: batch_y})
                print("Iteration {}, batch loss: {:.6f}, training accuracy: {:.5f}".format(iteration * batch_size,
                                                                                           loss, acc))
        batch.clean()
        print("Optimization done")

        saver = tf.train.Saver(tf.all_variables())
        checkpoint_path = "{}/{}.ckpt".format(model_name, model_name)
        saver.save(sess, checkpoint_path, global_step=iteration * batch_size)
        print("Model saved in {}".format(model_name))

if __name__ == "__main__":
    main()
