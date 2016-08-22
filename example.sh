#!/usr/bin/env bash

FILE_NAME="data"
MODEL_NAME="lstm_regression_model"

# parse web pages to retrieve lyrics, concatenate them and save them locally in a single file
./gather.py --output_file $FILE_NAME.txt --artists "137438971408, 137438966819, 7045, 8589947555, 137438969072, 6956, 6986, 137438973357, 201, 292, 8589949184, 17210"

# create a vocabulary file containing a binary representation for each character
./preprocess.py --input_file $FILE_NAME.txt

# train the LSTM model to fit the lyrics data
./train.py --training_file $FILE_NAME.txt --vocabulary_file $FILE_NAME.vocab --model_name $MODEL_NAME

# generate new lyrics and save them in a file
./sample.py --model_name $MODEL_NAME --vocabulary_file $FILE_NAME.vocab --output_file sample.txt
