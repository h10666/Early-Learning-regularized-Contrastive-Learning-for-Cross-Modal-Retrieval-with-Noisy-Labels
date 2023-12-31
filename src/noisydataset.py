# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
import random
from logging import getLogger

import cv2
from PIL import ImageFilter, Image
import numpy as np
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import torch.utils.data as data
import scipy.io as sio
import os
import json
from utils.config import args
from numpy.testing import assert_array_almost_equal
import h5py
logger = getLogger()

def multiclass_noisify(y, P, random_state=0):
    """ Flip classes according to transition probability matrix T.
    It expects a number between 0 and the number of classes - 1.
    """

    assert P.shape[0] == P.shape[1]
    assert np.max(y) < P.shape[0]

    # row stochastic matrix
    assert_array_almost_equal(P.sum(axis=1), np.ones(P.shape[1]))
    assert (P >= 0.0).all()

    m = y.shape[0]
    new_y = y.copy()
    flipper = np.random.RandomState(random_state)

    for idx in np.arange(m):
        i = y[idx]
        # draw a vector with only an 1
        flipped = flipper.multinomial(1, P[i, :], 1)[0]
        new_y[idx] = np.where(flipped == 1)[0]

    return new_y

def other_class(n_classes, current_class):
    """
    Returns a list of class indices excluding the class indexed by class_ind
    :param nb_classes: number of classes in the task
    :param class_ind: the class index to be omitted
    :return: one random class that != class_ind
    """
    if current_class < 0 or current_class >= n_classes:
        error_str = "class_ind must be within the range (0, nb_classes - 1)"
        raise ValueError(error_str)

    other_class_list = list(range(n_classes))
    other_class_list.remove(current_class)
    other_class = np.random.choice(other_class_list)
    return


#加载数据以及创建对称噪声数据
class cross_modal_dataset(data.Dataset):
    def __init__(self, dataset, noisy_ratio, mode, noise_mode='sym', root_dir='data/', noise_file=None, pred=False, probability=[], log=''):
        self.r = noisy_ratio # noise ratio
        self.mode = mode
        doc2vec = True
        if 'wiki' in dataset.lower():
            root_dir = os.path.join(root_dir, 'wiki')
            path = os.path.join(root_dir, 'wiki_deep_doc2vec_data_corr_ae.h5py')  # wiki_deep_doc2vec_data
            valid_len = 231
        elif 'inria' in dataset.lower():
            root_dir = os.path.join(root_dir, 'INRIA-Websearch')
            path = os.path.join(root_dir, 'INRIA-Websearch.mat')
            doc2vec = False
        elif 'xmedianet' in dataset.lower():
            root_dir = os.path.join(root_dir, 'XMediaNet')
            path = root_dir
            valid_len = 4000
            doc2vec = False
        else:
            raise Exception('Have no such dataset!')

        if doc2vec:
            h = h5py.File(path,'r')
            if self.mode == 'test' or self.mode == 'valid':
                test_imgs_deep = h['test_imgs_deep'][()].astype('float32')
                test_imgs_labels = h['test_imgs_labels'][()]
                test_imgs_labels -= np.min(test_imgs_labels)
                try:
                    test_texts_idx = h['test_text'][()].astype('float32')
                except Exception as e:
                    test_texts_idx = h['test_texts'][()].astype('float32')
                test_texts_labels = h['test_texts_labels'][()]
                test_texts_labels -= np.min(test_texts_labels)
                test_data = [test_imgs_deep, test_texts_idx]
                test_labels = [test_imgs_labels, test_texts_labels]

                valid_flag = True
                try:
                    valid_texts_idx = h['valid_text'][()].astype('float32')
                except Exception as e:
                    try:
                        valid_texts_idx = h['valid_texts'][()].astype('float32')
                    except Exception as e:
                        valid_flag = False
                        valid_data = [test_data[0][0: valid_len], test_data[1][0: valid_len]]
                        valid_labels = [test_labels[0][0: valid_len], test_labels[1][0: valid_len]]

                        test_data = [test_data[0][valid_len::], test_data[1][valid_len::]]
                        test_labels = [test_labels[0][valid_len::], test_labels[1][valid_len::]]
                if valid_flag:
                    valid_imgs_deep = h['valid_imgs_deep'][()].astype('float32')
                    valid_imgs_labels = h['valid_imgs_labels'][()]
                    valid_texts_labels = h['valid_texts_labels'][()]
                    valid_texts_labels -= np.min(valid_texts_labels)
                    valid_data = [valid_imgs_deep, valid_texts_idx]
                    valid_labels = [valid_imgs_labels, valid_texts_labels]

                train_data = valid_data if self.mode == 'valid' else test_data
                train_label = valid_labels if self.mode == 'valid' else test_labels
            elif self.mode == 'train':
                tr_img = h['train_imgs_deep'][()].astype('float32')
                tr_img_lab = h['train_imgs_labels'][()]
                tr_img_lab -= np.min(tr_img_lab)
                try:
                    tr_txt = h['train_text'][()].astype('float32')
                except Exception as e:
                    tr_txt = h['train_texts'][()].astype('float32')
                tr_txt_lab = h['train_texts_labels'][()]
                tr_txt_lab -= np.min(tr_txt_lab)
                train_data = [tr_img, tr_txt]
                train_label = [tr_img_lab, tr_txt_lab]
            else:
                raise Exception('Have no such set mode!')
            h.close()
        else:
            if 'xmedianet' in dataset.lower():
                if self.mode == 'train':
                    train_img = sio.loadmat(path + '/train_img.mat')['name']
                    train_txt = sio.loadmat(path + '/train_text.mat')['name']
                    train_label = sio.loadmat(path + '/train_label.mat')['name']
                    train_data = [train_img.astype('float32'), train_txt.astype('float32')]
                    train_label = [train_label.reshape([-1]).astype('int64'),
                                   train_label.reshape([-1]).astype('int64')]
                elif self.mode == 'valid':
                    valid_img = sio.loadmat(path + '/valid_img.mat')['name']
                    valid_txt = sio.loadmat(path + '/valid_text.mat')['name']
                    valid_label = sio.loadmat(path + '/valid_label.mat')['name']
                    train_data = [valid_img.astype('float32'), valid_txt.astype('float32')]
                    train_label = [valid_label.reshape([-1]).astype('int64'),
                                   valid_label.reshape([-1]).astype('int64')]
                elif self.mode == 'test':
                    test_img = sio.loadmat(path + '/test_img.mat')['name']
                    test_txt = sio.loadmat(path + '/test_text.mat')['name']
                    test_label = sio.loadmat(path + '/test_label.mat')['name']
                    train_data = [test_img.astype('float32'), test_txt.astype('float32')]
                    train_label = [test_label.reshape([-1]).astype('int64'),
                                   test_label.reshape([-1]).astype('int64')]
                else:
                    raise Exception('Have no such set mode!')
            else:

                data = sio.loadmat(path)
                if self.mode == 'train':
                    train_data = [data['tr_img'].astype('float32'), data['tr_txt'].astype('float32')]
                    train_label = [data['tr_img_lab'].reshape([-1]).astype('int64'), data['tr_txt_lab'].reshape([-1]).astype('int64')]
                elif self.mode == 'valid':
                    train_data = [data['val_img'].astype('float32'), data['val_txt'].astype('float32')]
                    train_label = [data['val_img_lab'].reshape([-1]).astype('int64'), data['val_txt_lab'].reshape([-1]).astype('int64')]
                elif self.mode == 'test':
                    train_data = [data['te_img'].astype('float32'), data['te_txt'].astype('float32')]
                    train_label = [data['te_img_lab'].reshape([-1]).astype('int64'), data['te_txt_lab'].reshape([-1]).astype('int64')]
                else:
                    raise Exception('Have no such set mode!')

        train_label = [la.astype('int64') for la in train_label]
        noise_label = train_label
        if noise_file is None:
            if noise_mode == 'sym':
                noise_file = os.path.join(root_dir, 'noise_labels_%g_sym.json' % self.r)
            elif noise_mode == 'asym':
                noise_file = os.path.join(root_dir, 'noise_labels_%g__asym.json' % self.r)
        if self.mode == 'train':
            if os.path.exists(noise_file):
                noise_label = json.load(open(noise_file, "r"))
                self.class_num = np.unique(noise_label).shape[0]
            else:    #inject noise
                noise_label = []
                classes = np.unique(train_label[0])
                class_num = classes.shape[0]
                self.class_num = class_num
                inx = np.arange(class_num)
                np.random.shuffle(inx)
                self.transition = {i: i for i in range(class_num)}
                half_num = int(class_num // 2)
                for i in range(half_num):
                    self.transition[inx[i]] = int(inx[half_num + i])
                for v in range(len(train_data)):
                    noise_label_tmp = []
                    data_num = train_data[v].shape[0]
                    idx = list(range(data_num))
                    random.shuffle(idx)
                    num_noise = int(self.r * data_num)
                    noise_idx = idx[:num_noise]
                    for i in range(data_num):
                        if i in noise_idx:
                            if noise_mode == 'sym':
                                noiselabel = int(random.randint(0, class_num))
                                noise_label_tmp.append(noiselabel)
                            elif noise_mode == 'asym':
                                noiselabel = self.transition[train_label[v][i]]
                                noise_label_tmp.append(noiselabel)
                        else:
                            noise_label_tmp.append(int(train_label[v][i]))
                    noise_label.append(noise_label_tmp)
                # print("save noisy labels to %s ..." % noise_file)
                json.dump(noise_label, open(noise_file, "w"))

        self.default_train_data = train_data
        self.default_noise_label = np.array(noise_label)
        self.train_data = self.default_train_data
        self.noise_label = self.default_noise_label
        if pred:
            self.prob = [np.ones_like(ll) for ll in self.default_noise_label]
        else:
            self.prob = None

    def reset(self, pred, prob, mode='labeled'):
        if pred is None:
            self.prob = None
            self.train_data = self.default_train_data
            self.noise_label = self.default_noise_label
        elif mode == 'labeled':
            inx = np.stack(pred).sum(0) > 0.5
            self.train_data = [dd[inx] for dd in self.default_train_data]
            self.noise_label = [dd[inx] for dd in self.default_noise_label]
            probs = np.stack(prob)[:, inx]
            prob_inx = probs.argmax(0)
            labels = np.stack(self.noise_label)[prob_inx, np.arange(probs.shape[1])]
            prob = probs[prob_inx, np.arange(probs.shape[1])]
            self.noise_label = [labels for _ in range(len(self.default_noise_label))]
            self.prob = [prob, prob]
        elif mode == 'unlabeled':
            inx = np.stack(pred).sum(0) <= 0.5
            self.train_data = [dd[inx] for dd in self.default_train_data]
            self.noise_label = [dd[inx] for dd in self.default_noise_label]
            self.prob = [dd[inx] for dd in prob]
        else:
            self.train_data = self.default_train_data
            # inx = (np.stack(pred).sum(0) <= 0.5).float()
            inx = [(p <= 0.5).astype('float32') for p in pred]
            self.noise_label = [self.default_noise_label[i] * (1. - inx[i]) - inx[i] for i in range(len(self.default_noise_label))]
            self.prob = prob


    def __getitem__(self, index):
        if self.prob is None:
            return [self.train_data[v][index] for v in range(len(self.train_data))], [self.noise_label[v][index] for v in range(len(self.train_data))], index
        else:
            return [self.train_data[v][index] for v in range(len(self.train_data))], [self.noise_label[v][index] for v in range(len(self.train_data))], [self.prob[v][index] for v in range(len(self.prob))], index


    def __len__(self):
        return len(self.train_data[0])

