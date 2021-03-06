'''
load datasets
'''

import numpy as np
import conf

np.random.seed(1337)

def load_chunk(dataset, amount=0, split_rate=0.9, chunk_type='NP'):
    if dataset=='train.txt':
        train_set = open('../dataset/chunk/train.txt', 'r')
        train_set = train_set.read().strip().split('\n\n')

        if amount!=0:
            train_set = train_set[:amount]

        np.random.shuffle(train_set)

        train_set = list(map(str2tuple, train_set))
        if chunk_type=='NP':
            for sentence in train_set:
                chunk_tags = list(sentence[2])
                for ind, chunk in enumerate(chunk_tags):
                    if chunk!='B-NP' and chunk!='I-NP':
                        chunk_tags[ind] = 'O'
                sentence[2] = tuple(chunk_tags)

        length = len(train_set)
        margin = int(length*split_rate)

        train_data = train_set[:margin]
        dev_data = train_set[margin:]

        return train_data, dev_data

    elif dataset=='test.txt':
        test_set = open('../dataset/chunk/test.txt', 'r')
        test_set = test_set.read().strip().split('\n\n')

        test_set = list(map(str2tuple, test_set))
        if chunk_type=='NP':
            for sentence in test_set:
                chunk_tags = list(sentence[2])
                for ind, chunk in enumerate(chunk_tags):
                    if chunk!='B-NP' and chunk!='I-NP':
                        chunk_tags[ind] = 'O'
                sentence[2] = tuple(chunk_tags)

        test_data = test_set

        return test_data

def load_ner(dataset, form='BIO', amount=0):
    if dataset=='eng.train':
        if form=='BIO':
            train_set = open('../dataset/ner/eng.train', 'r')
        elif form=='BIOES':
            train_set = open('../dataset/ner_BIOES/eng.train', 'r')
        train_set = train_set.read().strip().split('\n\n')

        if amount!=0:
            train_set = train_set[:amount]

        train_set = list(map(str2tuple, train_set))

        return train_set

    elif dataset=='eng.testa':
        if form=='BIO':
            dev_set = open('../dataset/ner/eng.testa', 'r')
        elif form=='BIOES':
            dev_set = open('../dataset/ner_BIOES/eng.testa', 'r')
        dev_set = dev_set.read().strip().split('\n\n')

        dev_set = list(map(str2tuple, dev_set))

        return dev_set

    elif dataset=='eng.testb':
        if form=='BIO':
            test_set = open('../dataset/ner/eng.testb', 'r')
        elif form=='BIOES':
            test_set = open('../dataset/ner_BIOES/eng.testb', 'r')
        test_set = test_set.read().strip().split('\n\n')

        test_set = list(map(str2tuple, test_set))

        return test_set

# sentence example:
# ['He PR B-NP', 'is VB I-VP']
def str2tuple(sentence):
    sentence_split = [each.split() for each in sentence.split('\n')]
    return list(zip(*sentence_split))

if __name__ == '__main__':
    # load_chunk()
    load_chunk(chunk_type='ALL')
