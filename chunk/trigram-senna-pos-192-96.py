from keras.models import Model
from keras.layers import Input, Masking, Dense, LSTM
from keras.layers import Dropout, TimeDistributed, Bidirectional, merge
from keras.layers.embeddings import Embedding
from keras.utils import np_utils

import numpy as np
import pandas as pd

import sys
import math
import os
from datetime import datetime

# add path
sys.path.append('../')
sys.path.append('../tools')


from tools import conf
from tools import load_data
from tools import prepare
from tools import plot

np.random.seed(0)

# train hyperparameters
feature_length = conf.feature_length
step_length = conf.step_length
pos_length = conf.pos_length

emb_vocab = conf.senna_vocab
emb_length = conf.senna_length

output_length = conf.NP_length

split_rate = conf.split_rate
batch_size = conf.batch_size
nb_epoch = conf.nb_epoch

model_name = os.path.basename(__file__)[:-3]

folder_path = 'model/%s'%model_name
if not os.path.isdir(folder_path):
    os.makedirs(folder_path)

# the data, shuffled and split between train and test sets
train_data, dev_data = load_data.load_chunk(dataset='train.txt', split_rate=split_rate)

train_samples = len(train_data)
dev_samples = len(dev_data)
print('train shape:', train_samples)
print('dev shape:', dev_samples)
print()

word_embedding = pd.read_csv('../preprocessing/senna/embeddings.txt', delimiter=' ', header=None)
word_embedding = word_embedding.values
word_embedding = np.concatenate([np.zeros((1,emb_length)),word_embedding, np.random.randn(1,emb_length)])

embed_index_input_1 = Input(shape=(step_length,))
embed_index_input_2 = Input(shape=(step_length,))
embed_index_input_3 = Input(shape=(step_length,))
embedding_1 = Embedding(emb_vocab+2, emb_length, weights=[word_embedding], mask_zero=True, input_length=step_length)(embed_index_input_1)
embedding_2 = Embedding(emb_vocab+2, emb_length, weights=[word_embedding], mask_zero=True, input_length=step_length)(embed_index_input_2)
embedding_3 = Embedding(emb_vocab+2, emb_length, weights=[word_embedding], mask_zero=True, input_length=step_length)(embed_index_input_3)
pos_input = Input(shape=(step_length, pos_length))
senna_pos_merge = merge([embedding_1, embedding_2, embedding_3, pos_input], mode='concat')
input_mask = Masking(mask_value=0)(senna_pos_merge)
hidden_1 = Bidirectional(LSTM(192, return_sequences=True))(input_mask)
dp_1 = Dropout(0.2)(hidden_1)
hidden_2 = Bidirectional(LSTM(96, return_sequences=True))(dp_1)
dp_2 = Dropout(0.2)(hidden_2)
output = TimeDistributed(Dense(output_length, activation='softmax'))(dp_2)
model = Model(input=[embed_index_input_1,embed_index_input_2, embed_index_input_3,pos_input], output=output)

model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

print(model.summary())


number_of_train_batches = int(math.ceil(float(train_samples)/batch_size))
number_of_dev_batches = int(math.ceil(float(dev_samples)/batch_size))


print('start train %s ...\n'%model_name)

best_accuracy = 0
best_epoch = 0
all_train_loss = []
all_dev_loss = []
all_dev_accuracy = []

log = open('%s/model_log.txt'%folder_path, 'w')

start_time = datetime.now()
print('train start at %s\n'%str(start_time))
log.write('train start at %s\n\n'%str(start_time))

for epoch in range(nb_epoch):

    start = datetime.now()

    print('-'*60)
    print('epoch %d start at %s'%(epoch, str(start)))

    log.write('-'*60+'\n')
    log.write('epoch %d start at %s\n'%(epoch, str(start)))

    train_loss = 0
    dev_loss = 0

    np.random.shuffle(train_data)

    for i in range(number_of_train_batches):
        train_batch = train_data[i*batch_size: (i+1)*batch_size]
        embed_index, auto_encoder_index, pos, label, length, sentence = prepare.prepare_chunk(batch=train_batch)
        embed_index_1 = embed_index[:-2]
        embed_index_2 = embed_index[1:-1]
        embed_index_3 = embed_index[2:]
        pos = [np.concatenate([np_utils.to_categorical(p[:-2],pos_length),np_utils.to_categorical(p[1:-1],pos_length),np_utils.to_categorical(p[2:],pos_length)],axis=1) for p in pos]
        pos = np.array([(np.concatenate([p, np.zeros((step_length-length[l], pos_length*3))])) for l,p in enumerate(pos)])
        y = np.array([np_utils.to_categorical(each, output_length) for each in label])

        train_metrics = model.train_on_batch([embed_index_1, embed_index_2, embed_index_3, pos], y)
        train_loss += train_metrics[0]
    all_train_loss.append(train_loss)

    correct_predict = 0
    all_predict = 0

    for j in range(number_of_dev_batches):
        dev_batch = dev_data[j*batch_size: (j+1)*batch_size]
        embed_index, auto_encoder_index, pos, label, length, sentence = prepare.prepare_chunk(batch=dev_batch)
        embed_index_1 = embed_index[:-2]
        embed_index_2 = embed_index[1:-1]
        embed_index_3 = embed_index[2:]
        pos = [np.concatenate([np_utils.to_categorical(p[:-2],pos_length),np_utils.to_categorical(p[1:-1],pos_length),np_utils.to_categorical(p[2:],pos_length)],axis=1) for p in pos]
        pos = np.array([(np.concatenate([p, np.zeros((step_length-length[l], pos_length*3))])) for l,p in enumerate(pos)])
        y = np.array([np_utils.to_categorical(each, output_length) for each in label])
        # for loss
        dev_metrics = model.test_on_batch([embed_index_1, embed_index_2, embed_index_3, pos], y)
        dev_loss += dev_metrics[0]

        # for accuracy
        prob = model.predict_on_batch([embed_index_1, embed_index_2, embed_index_3, pos])
        for i, l in enumerate(length):
            predict_label = np_utils.categorical_probas_to_classes(prob[i])
            correct_predict += np.sum(predict_label[:l]==label[i][:l])
        all_predict += np.sum(length)
    epcoh_accuracy = float(correct_predict)/all_predict
    all_dev_accuracy.append(epcoh_accuracy)

    all_dev_loss.append(dev_loss)

    if epcoh_accuracy>=best_accuracy:
        best_accuracy = epcoh_accuracy
        best_epoch = epoch

    end = datetime.now()

    model.save('%s/model_epoch_%d.h5'%(folder_path, epoch), overwrite=True)

    print('epoch %d end at %s'%(epoch, str(end)))
    print('epoch %d train loss: %f'%(epoch, train_loss))
    print('epoch %d dev loss: %f'%(epoch, dev_loss))
    print('epoch %d dev accuracy: %f'%(epoch, epcoh_accuracy))
    print('best epoch now: %d\n'%best_epoch)

    log.write('epoch %d end at %s\n'%(epoch, str(end)))
    log.write('epoch %d train loss: %f\n'%(epoch, train_loss))
    log.write('epoch %d dev loss: %f\n'%(epoch, dev_loss))
    log.write('epoch %d dev accuracy: %f\n'%(epoch, epcoh_accuracy))
    log.write('best epoch now: %d\n\n'%best_epoch)


end_time = datetime.now()
print('train end at %s\n'%str(end_time))
log.write('train end at %s\n\n'%str(end_time))

timedelta = end_time - start_time
print('train cost time: %s\n'%str(timedelta))
print('best epoch last: %d\n'%best_epoch)

log.write('train cost time: %s\n\n'%str(timedelta))
log.write('best epoch last: %d\n\n'%best_epoch)

plot.plot_loss(all_train_loss, all_dev_loss, folder_path=folder_path, title='%s'%model_name)
plot.plot_accuracy(all_dev_accuracy, folder_path=folder_path, title='%s'%model_name)