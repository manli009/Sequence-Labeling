'''
evaluate result
'''

from keras.models import load_model
from keras.utils import np_utils

import numpy as np

import os
import sys

# add path
sys.path.append('../')
sys.path.append('../tools')


from tools import conf
from tools import load_data
from tools import prepare

# input sentence dimensions
step_length = conf.chunk_step_length
pos_length = conf.chunk_pos_length

IOB = conf.chunk_NP_IOB_decode

test_data = load_data.load_chunk(dataset='test.txt')

best_epoch = sys.argv[1]

model_name = os.path.basename(__file__)[9:-3]
folder_path = './model/%s'%model_name

model_path = '%s/model_epoch_%s.h5'%(folder_path, best_epoch)
result = open('%s/predict.txt'%folder_path, 'w')


print('loading model...')
model = load_model(model_path)
print('loading model finished.')

for each in test_data:
    embed_index, hash_index, pos, label, length, sentence = prepare.prepare_chunk(batch=[each], trigram=True)
    
    embed_index_1 = embed_index[:,:-2]
    embed_index_2 = embed_index[:,1:-1]
    embed_index_3 = embed_index[:,2:]

    hash_index_1 = hash_index[:,:-2]
    hash_index_2 = hash_index[:,1:-1]
    hash_index_3 = hash_index[:,2:]

    pos = [np.concatenate([np_utils.to_categorical(p[:-2],pos_length),np_utils.to_categorical(p[1:-1],pos_length),np_utils.to_categorical(p[2:],pos_length)],axis=1) for p in pos]
    pos = np.array([(np.concatenate([p, np.zeros((step_length-length[l], pos_length*3))])) for l,p in enumerate(pos)])

    prob = model.predict_on_batch([embed_index_1,embed_index_2,embed_index_3,\
                                                hash_index_1,hash_index_2,hash_index_3,pos])

    for i, l in enumerate(length):
        predict_label = np_utils.categorical_probas_to_classes(prob[i])
        chunktags = [IOB[j] for j in predict_label][:l]

    word_pos_chunk = list(zip(*each))

    for ind, chunktag in enumerate(chunktags):
        result.write(' '.join(word_pos_chunk[ind])+' '+chunktag+'\n')
    result.write('\n')

result.close()
print('epoch %s predict over !'%best_epoch)

os.system('../tools/conlleval < %s/predict.txt'%folder_path)

