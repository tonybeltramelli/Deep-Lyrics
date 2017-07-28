#!/usr/bin/env python
__author__ = 'Tony Beltramelli www.tonybeltramelli.com - 19/08/2016'

import argparse
from modules.Model import *
from modules.Vocabulary import *
from collections import deque


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str, required=True)
    parser.add_argument('--vocabulary_file', type=str, required=True)
    parser.add_argument('--output_file', type=str, required=True)

    parser.add_argument('--seed', type=str, default="Once upon a time, ")
    parser.add_argument('--sample_length', type=int, default=1500)
    parser.add_argument('--log_frequency', type=int, default=100)
    args = parser.parse_args()

    model_name = args.model_name
    vocabulary_file = args.vocabulary_file
    output_file = args.output_file
    seed = args.seed
    sample_length = args.sample_length
    log_frequency = args.log_frequency

    model = Model(model_name)
    model.restore()
    classifier = model.get_classifier()

    vocabulary = Vocabulary()
    vocabulary.retrieve(vocabulary_file)

    sample_file = open(output_file, 'w')

    stack = deque([])
    for i in range(0, model.sequence_length - len(seed)):
        stack.append(" ")

    for char in seed:
        stack.append(char)
        sample_file.write(char)

    with tf.Session() as sess:
        tf.global_variables_initializer().run()

        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(model_name)

        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)

            for i in range(0, sample_length):
                vector = []
                for char in stack:
                    vector.append(vocabulary.binary_vocabulary[char])
                vector = np.array([vector])
                prediction = sess.run(classifier, feed_dict={model.x: vector})
                predicted_char = vocabulary.char_lookup[np.argmax(prediction)]

                stack.popleft()
                stack.append(predicted_char)
                sample_file.write(predicted_char)

                if i % log_frequency == 0:
                    print "Progress: {}%".format((i * 100) / sample_length)

            sample_file.close()
            print "Sample saved in {}".format(output_file)

if __name__ == "__main__":
    main()
