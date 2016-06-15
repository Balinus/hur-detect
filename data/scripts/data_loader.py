__author__ = 'racah'
import h5py
import numpy as np
from operator import mul
import os
import glob
import sys
import time
from multiprocessing import Pool
from functools import partial








#1 is hur
#0 is nhur
class LoadHurricane():
    def __init__(self,batch_size=None, flatten=False, num_ims=None, seed=4):
        self.seed = seed
        self.batch_size = batch_size
        self.num_ims = num_ims
        self.seed = seed
        self.flatten=flatten
    #TODO try on 96x96 (use bigger file -> get from cori)
    def load_hurricane(self, path, use_negative):

        print 'getting data...'
        h5f = h5py.File(path)
        hurs = h5f['hurricane'][:]
        nhurs = h5f['nothurricane'][:]
        hurs_bboxes = np.asarray(h5f['hurricane_box']).reshape(hurs.shape[0],4)
        nhurs_bboxes = np.zeros((nhurs.shape[0],4))
        #input_size = hurs.shape[0] + nhurs.shape[0]
        #shp = ((hurs.shape[0]+nhurs.shape[0],) + hurs.shape[1:])

        if use_negative:
            inputs = np.vstack((hurs,nhurs))
        else:
            inputs = hurs
        # tmpfile= os.path.basename(path + '/tst.h5')
        # h5tmp = h5py.File(tmpfile)
        # # if'inputs' not in h5tmp:
        # inputs =h5tmp.create_dataset('inputs', shape=shp, dtype='f4')
        # inputs[:hurs.shape[0]] = hurs
        # inputs[hurs.shape[0]:] = nhurs
        # # else:
        # #     inputs = h5tmp['inputs']

        bboxes = np.vstack((hurs_bboxes,nhurs_bboxes))
        cl_labels = np.zeros((inputs.shape[0]))
        cl_labels[:hurs.shape[0]] = 1
        #cl_labels[hurs.shape[0]:,1] = 1.

        if not self.num_ims:
            self.num_ims = inputs.shape[0]


        else:
            self.num_ims = self.num_ims

        print self.num_ims


#         hur_masks = self.gen_masks(inputs[:self.num_ims],bboxes)
#         self.y_dims = hur_masks.shape[1:]
        #hur_masks = hur_masks.reshape(hur_masks.shape[0], np.prod(hur_masks.shape[1:]))
        tr_i, te_i, val_i = self.get_train_val_test_ix(self.num_ims)

        return self.set_up_train_test_val(inputs, bboxes, cl_labels, tr_i, te_i, val_i)



    def get_train_val_test_ix(self, num_ims):
        # tr, te, val is 0.6,0.2,0.2
        ix = range(num_ims)

        #make sure they are all multiple of batch size
        n_te = int(0.2*num_ims)
        n_val = int(0.25*(num_ims - n_te))
        n_tr =  num_ims - n_te - n_val

#         if self.batch_size:
#             n_te -= n_te % self.batch_size
#             n_val = self.batch_size * ((n_val) / self.batch_size)
#             n_tr =  self.batch_size * ((n_tr) / self.batch_size)


        #shuffle once deterministically
        np.random.RandomState(3).shuffle(ix)
        te_i = ix[:n_te]
        rest = ix[n_te:]

        np.random.RandomState(self.seed).shuffle(rest)
        val_i = rest[:n_val]
        tr_i = rest[n_val:n_val + n_tr]
        return tr_i, te_i, val_i


    def set_up_train_test_val(self,hurs, boxes,cl_labels, tr_i,te_i, val_i):

        x_tr, bbox_tr, lbl_tr = hurs[tr_i], boxes[tr_i], cl_labels[tr_i]
        x_tr, tr_means, tr_stds = self.preprocess_each_channel(x_tr)
        #self.test_masks(bbox_tr, y_tr,np.random.randint(x_tr.shape[0]))
        x_te,bbox_te, lbl_te = hurs[te_i], boxes[te_i], cl_labels[te_i]
        x_te, _ ,_ = self.preprocess_each_channel(x_te)

        #self.test_masks(bbox_te, y_te,np.random.randint(x_te.shape[0]))
        x_val, bbox_val, lbl_val = hurs[val_i], boxes[val_i], cl_labels[val_i]
        x_val, _ ,_ = self.preprocess_each_channel(x_val)
        #self.test_masks(bbox_val, y_val,np.random.randint(x_val.shape[0]))

        if self.flatten:
            x_tr = x_tr.reshape(x_tr.shape[0], reduce(mul, x_tr.shape[1:]))
            x_te = x_te.reshape(x_te.shape[0], reduce(mul, x_te.shape[1:]))
            x_val = x_val.reshape(x_val.shape[0], reduce(mul, x_val.shape[1:]))

        x_dims = hurs.shape[1:]

        return {'tr': (x_tr, bbox_tr, lbl_tr), \
        'te':(x_te,  bbox_te, lbl_te), \
        'val': (x_val ,bbox_val, lbl_val)}
        # return {'x_train': x_tr, 'y_train': y_tr, 'x_test': x_te, 'y_test': y_te,'x_val':x_val, 'y_val':y_val, 'boxes': boxes}

    def preprocess_each_channel(self,arr, means=[], stds=[], mode='normalize'):
        # assumes channels are on the axis 1
        if len(means) == 0:
            means = np.mean(arr, axis=(0, 2, 3))
        if mode == 'standardize':
            if len(stds) == 0:
                stds = np.std(arr, axis=(0, 2, 3))
            for channel, (mean, std) in enumerate(zip(means, stds)):
                arr[:, channel, :, :] -= mean
                arr[:, channel, :, :] /= std
            return arr, means, stds
        elif mode == "normalize":

            for channel, mean in enumerate(means):
                arr[:, channel, :, :] -= mean
                
            mins = np.min(arr, axis=(0, 2, 3))
            maxes = np.max(arr, axis=(0, 2, 3))
            #normalize between -1 and 1
            for channel, (min_,max_) in enumerate(zip(mins, maxes)):
                arr[:, channel, :, :] = 2 * ((arr[:, channel, :, :] - min_) / (max_ - min_)) - 1
            return arr, None, None

                
            
       
        


    def test_masks(self, bboxes,mask, ind=0):
        bbox = bboxes[ind]
        m = mask[ind,0]
        hmin, hmax, wmin, wmax = self.get_cooords(bbox)
        section = m[hmin: hmax, wmin: wmax ]
        not_sections = (m[:hmin,:wmin], m[:hmin, wmax:], m[hmax:,:wmin], m[hmax:,wmax:])
        assert np.all(section == 1.), section
        for not_section in not_sections:
            assert np.all(not_section == 0), not_section


    def get_cooords(self, bbox):
        hmin, hmax, wmin, wmax = bbox[1],bbox[3], bbox[0],bbox[2]
        return hmin, hmax, wmin, wmax
    def gen_masks(self,hurs,bboxes):
        '''

        :param hurs: n_hurs x 8 x H x W array
        :param bboxes: n_hurs x 4 array
        :return:
            n_hurs x H x W array
                where 1 is hurricane, 0 is not hurricane

        '''
        t = time.time()
        p_hur = np.zeros((hurs.shape[0], hurs.shape[2],hurs.shape[3]))
        #p_nhur = np.ones((hurs.shape[0], hurs.shape[2], hurs.shape[3]))

        #TODO: vectorize
        for i in range(hurs.shape[0]):
            bbox=bboxes[i]
            hmin, hmax, wmin, wmax = self.get_cooords(bbox)
            p_hur[i, hmin:hmax, wmin:wmax] = 1.
            #p_nhur[i, hmin:hmax, wmin:wmax] = 0.
        print "gen_masks took: %5.2f seconds"%(time.time()-t)
        hur_masks = p_hur.reshape((hurs.shape[0],1, hurs.shape[2],hurs.shape[3]))
        #hur_masks = np.hstack((p_hur, p_nhur)).reshape(hurs.shape[0], 2, hurs.shape[2], hurs.shape[3])
        return hur_massk
    
    
    
def load_dataset(path='/global/project/projectdirs/nervana/yunjie/dataset/localization/larger_hurricanes_loc.h5'):
    lh = LoadHurricane()
    datasets = lh.load_hurricane(path, use_negative=True)
    
    (X_train, y_train),
    (X_val, y_val), 
    (X_test, y_test) = [(datasets[k][0],datasets[k][2])
                                                      for k in ['tr', 'val','te']]



    return X_train, y_train, X_val, y_val, X_test, y_test