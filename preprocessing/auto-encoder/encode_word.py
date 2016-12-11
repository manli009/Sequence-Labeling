from keras.models import load_model

import pandas as pd

import sys
import os


# add path
sys.path.append('../')
sys.path.append('../tools')

from tools import load_data
from tools import prepare

model_path = '../../chunk/model/word-hash-auto-encoder-128/hidden_model_epoch_15.h5'

w = open('./conll2000-word.lst', 'w')
embeddings = pd.DataFrame(columns=range(128))

print('loading model...')
encoder = load_model(model_path)
print('loading model finished.')

train_data, dev_data = load_data.load_chunk(dataset='train.txt', split_rate=split_rate)
test_data = load_data.load_chunk(dataset='test.txt')

all_word =[]

# all word
[all_word.extend(list(each[0])) for each in train_data]
[all_word.extend(list(each[0])) for each in dev_data]
[all_word.extend(list(each[0])) for each in test_data]

all_word = [each.strip().lower() for each in all_word]
all_word = list(set(all_word))

for i, word in enumerate(all_word):
    w.write(word+'\n')
    word_hashing = prepare.prepare_chunk_encoder(batch=[word])
    word_hashing = word_hashing.toarray()
    representation = encoder.predict_on_batch(word_hashing)
    embeddings.loc[i] = representation[0]

embeddings.to_csv('auto-encoder-embeddings.txt', sep=' ',header=False,index=False)
w.close()
