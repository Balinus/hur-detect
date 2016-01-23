__author__ = 'racah'
import h5py
import numpy as np
from operator import mul
import os
import glob
import sys
import time

# 0 1 is hurriane
# 1 0  is not


# size of sampling window
# w_size = 31
# rad = w_size / 2
#
# nclass = 2  #hur and nhur
#
#
# def run_tests(data_dict, hurs, pixels_to_use_per_image, cropped_ims, train_test_val_dist):
#
#      ##assert len(tr_i) + len(te_i) + len(val_i) == num_images
#     for name, X, i in [('tr', data_dict['x_train'], data_dict['tr_i']), ('val', data_dict['x_val'], data_dict['val_i']), ('te', data_dict['x_test'], data_dict['te_i'])]:
#         assert X.shape[1:] == (hurs.shape[1] * w_size * w_size,), "%s not right shape: %s " % (name, str(X.shape[1:]))
#         assert X.shape[0] == len(i) * pixels_to_use_per_image, "%s not right shape: %s " % (name, str(X.shape[0]))
#     for name, i, y_arr in [('tr', data_dict['tr_i'], data_dict['y_train']), ('te', data_dict['te_i'], data_dict['y_test']), ('val', data_dict['val_i'], data_dict['y_val'])]:
#         assert y_arr[y_arr[:, 0] == 1.].shape[0] > 0, "%s_%s_%s" % (name, y_arr.shape, len(i))
#         assert y_arr[y_arr[:, 0] == 0.].shape[0] > 0
#
#     assert cropped_ims.shape[0] == train_test_val_dist['num_images']
#     print "Data Loader passed all tests!"
#
# def set_up_train_test_val(hurs, boxes, im_indices, train_test_val_dist):
#     tr_i, te_i, val_i = get_indices(im_indices, train_test_val_dist)
#
#     x_train, y_train = generate_input_and_labels(hurs, tr_i, boxes)
#     x_train, tr_means, tr_stds = normalize_each_channel(x_train)
#     x_train = x_train.reshape(x_train.shape[0], reduce(mul, x_train.shape[1:]))
#
#     x_test, y_test = generate_input_and_labels(hurs, te_i, boxes)
#     x_test, _ ,_ = normalize_each_channel(x_test, tr_means, tr_stds)
#     x_test = x_test.reshape(x_test.shape[0], reduce(mul, x_test.shape[1:]))
#
#     x_val, y_val = generate_input_and_labels(hurs, val_i, boxes)
#     x_val, _ ,_ = normalize_each_channel(x_val, tr_means, tr_stds)
#     x_val = x_val.reshape(x_val.shape[0], reduce(mul, x_val.shape[1:]))
#     return {'x_train': x_train, 'y_train': y_train, 'x_test': x_test, 'y_test': y_test,'x_val':x_val, 'y_val':y_val, 'boxes': boxes}
#
#
# def get_indices(im_indices, train_test_val_dist):
#     d = train_test_val_dist
#     te_i = im_indices[:d['test']]
#     tr_i = im_indices[d['test']:d['test'] + d['train']]
#     val_i = im_indices[d['test'] + d['train']:]
#     return tr_i, te_i, val_i
#
#
# def normalize_each_channel(arr, means=[], stds=[]):
#     # assumes channels are on the axis 1
#     if len(means) == 0:
#         means = np.mean(arr, axis=(0, 2, 3))
#     if len(stds) == 0:
#         stds = np.std(arr, axis=(0, 2, 3))
#     for channel, (mean, std) in enumerate(zip(means, stds)):
#         arr[:, channel, :, :] -= mean
#         arr[:, channel, :, :] /= std
#     return arr, means, stds
#
#
# def is_hurricane(x_cen, y_cen, xmin, ymin, xmax, ymax):
#     xmin, ymin, xmax, ymax = [int(singleton) for singleton in [xmin, ymin, xmax, ymax]]
#     assert isinstance(ymax, object)
#     if x_cen >= xmin and x_cen <= xmax and y_cen >= ymin and y_cen <= ymax:
#         return True
#     else:
#         return False
#
#
# def get_pixel_index(x, y, cols):
#     #based on the x,y coordinate, we get the pixel index
#     return y * x - (cols - y)
#
#
# def get_x_y_from_pixel(pixel_i, cols):
#     rows_done = pixel_i / cols
#     cols_done_in_unfinished_row = pixel_i % cols
#     return cols_done_in_unfinished_row, rows_done
#
# def save_preproc_data(preproc_data_dir, preproc_data_filename, data_dict):
#
#
#     h5=h5py.File(os.path.join(preproc_data_dir,preproc_data_filename ), 'w')
#     for k,v in data_dict.iteritems():
#         h5.create_dataset(k, data=v)
#
#
#     h5.close()
#
#
# def get_val_im_size(h5file, preproc_data_dir):
#     preproc_file, _ = get_all_preproc_files_from(h5file, preproc_data_dir)[0]
#     h5f = h5py.File(h5file)
#
#     imx = h5f['hurricane'][0][0].shape[0]
#     imy = h5f['hurricane'][0][0].shape[1]
#     im_size = (imx - rad) * (imy - rad)
#     if len(preproc_file) > 0:
#         pp_file = h5py.File(preproc_file)
#         tot_pixels = pp_file['x_val'][0][0].shape[0]
#         assert tot_pixels == im_size
#     return im_size
#
#
#
# def generate_input_and_labels(im_array, im_indices, label_array):
#     hurs = im_array
#     boxes = label_array
#
#     rows = im_array.shape[2]
#     cols = im_array.shape[3]
#
#     #subtract a frame of rad * rad around edge of image
#     pixels_to_use_per_image = (cols - 2 * rad) * (rows - 2 * rad)
#     total_pixels_to_use = len(im_indices) * pixels_to_use_per_image
#
#     #number of totoal pixels to use by number of channels by window size
#     inputs = np.zeros((total_pixels_to_use, hurs.shape[1], w_size, w_size))
#     labels = np.zeros((total_pixels_to_use, 1))
#     pixel_count = 0
#     for im_index in im_indices:
#         image = np.asarray(hurs[im_index])
#
#         for x in range(rad, rows - rad):
#             for y in range(rad, cols - rad):
#                 x_min, x_max, y_min, y_max = (x - rad, x + rad, y - rad, y + rad )
#
#                 #print x_min, x_max,y_min,y_max
#                 #if window centered on this pixel stays in the frame
#                 assert (x_min >= 0 and x_max + 1 <= rows and y_min >= 0 and y_max + 1 <= cols), \
#                     "Something is wrong with the pixels selected: %i,%i,%i,%i for %i window size" % (
#                         x_min, x_max, y_min, y_max, w_size)
#
#                 #add window to inputs (need to reshape it to 1,channels,w_size,w_wize so it can be vstacked)
#                 cur_w = np.copy(image[:, x_min:x_max + 1, y_min:y_max + 1])
#                 #print pixel_count
#                 inputs[pixel_count] = cur_w  #.flatten()
#
#                 #label according to center pixel's label, so 0th element is 1 if hurricane for one-ht encoding and 1st elemnt if not hurricane
#                 #python unpacks along rows, so we transpose the row vector boxes[i], so it can be unpacked
#                 labels[pixel_count] = (1 if is_hurricane(x, y, *boxes[im_index].T) else 0)
#                 pixel_count += 1
#
#     return inputs, labels
#
# def get_all_preproc_files_from(h5path, preproc_data_dir):
#     path_basename = os.path.splitext(os.path.basename(h5path))[0]
#
#     #get newest file that comes from same path and has same number of train specified
#     filepaths= glob.iglob(os.path.join(preproc_data_dir, path_basename +'*'))
#     return filepaths, path_basename
#
# def get_newest_file_with_sufficient(train_test_val_dist, files_list, prefix):
#     num_list = ['train', 'test', 'val']
#     for file in files_list:
#         nums = os.path.basename(file).split(prefix)[1].split('-')[1:4]
#         nums = map(int, nums)
#
#         #checks if num of images for train, test and val in file are greater than or equal to number requested
#         hasEnoughData = all([train_test_val_dist[num_list[i]] <= num for i,num in enumerate(nums)])
#         if hasEnoughData:
#             return file
#     return False
#
# def load_hurricane_old(path, num_train=6,num_test_val=2, load_from_disk=True, preproc_data_dir='/global/project/projectdirs/nervana/evan/preproc_data', seed=3):
#     print "starting..."
#     do_compute=False
#     train_test_val_dist = {'train': num_train, 'test': num_test_val, 'val': num_test_val, 'num_images': num_train + 2*num_test_val}
#     if load_from_disk and os.path.exists(preproc_data_dir):
#         filepaths, path_basename = get_all_preproc_files_from(path, preproc_data_dir)
#         filepath = get_newest_file_with_sufficient(train_test_val_dist, filepaths,path_basename)
#
#         if not filepath:
#             do_compute = True
#
#         else:
#             h5data = h5py.File(filepath)
#             print "loading preproc data from file..."
#             data_dict = {k : np.asarray(h5data[k]) for k in h5data.keys()}
#             print 'done!'
#     else:
#         do_compute=True
#
#     if do_compute:
#         print 'computing preproc data'
#         h5f = h5py.File(path)
#         hurs = h5f['hurricane']
#         boxes = h5f['hurricane_box']
#
#         rows = hurs[0].shape[1]
#         cols = hurs[0].shape[2]
#
#         pixels_to_use_per_image = (cols - 2 * rad) * (rows - 2 * rad)
#
#         im_indices = range(train_test_val_dist['num_images'])
#         #np.random.RandomState(seed).shuffle(im_indices)
#
#
#         data_dict = set_up_train_test_val(hurs, boxes, im_indices, train_test_val_dist)
#
#         #get the hurricane images we are using and crop them down to only the pixels that are used can be centered on the window
#         #ie the pixels to use
#         cropped_ims = np.asarray(hurs[im_indices, :, rad:rows - rad, rad:cols - rad])
#         data_dict['cropped_ims'] = cropped_ims
#
#         #run tests
#         ind_tuple = get_indices(im_indices,train_test_val_dist)
#         data_dict.update(zip(['tr_i', 'te_i', 'val_i'],ind_tuple))
#         data_dict['nclass'] = nclass
#         data_dict['w_size'] = w_size
#
#
#         run_tests(data_dict, hurs, pixels_to_use_per_image, cropped_ims, train_test_val_dist)
#
#         preproc_data_filename = '{0}-{1}-{2}-{3}-{4}'.format(os.path.splitext(os.path.basename(path))[0],
#                                                                  data_dict['x_train'].shape[0] / pixels_to_use_per_image,
#                                                                  data_dict['x_test'].shape[0] / pixels_to_use_per_image,
#                                                                  data_dict['x_val'].shape[0] / pixels_to_use_per_image,
#                                                                  w_size) +'.h5'
#         if not os.path.exists(preproc_data_dir):
#             os.mkdir(preproc_data_dir)
#         save_preproc_data(preproc_data_dir,preproc_data_filename,data_dict)
#
#     #
#     # key_order = ['x_train', 'y_train', 'tr_i', 'x_test', 'y_test', 'te_i', 'x_val', 'y_val', 'val_i', 'nclass', 'w_size', 'cropped_ims', 'boxes']
#     return data_dict


class LoadHurricane():
    def __init__(self,batch_size, num_ims=None, seed=4):
        self.seed = seed
        self.batch_size = batch_size
        self.num_ims = num_ims
        self.seed = seed
    #TODO try on 96x96 (use bigger file -> get from cori)
    def load_hurricane(self, path):

        print 'getting data...'
        h5f = h5py.File(path)
        hurs_r = np.asarray(h5f['hurricane'])
        print hurs_r.shape
        dims = hurs_r.shape[1:]
        #]hurs_r = hurs_r.reshape(hurs_r.shape[0], np.prod(hurs_r.shape[1:]))
        #nhurs = h5f['nothurricane']
        bboxes = np.asarray(h5f['hurricane_box']).reshape(hurs_r.shape[0],4)
        if not self.num_ims:
            self.num_ims = hurs_r.shape[0]

        else:
            self.num_ims = self.num_ims

        hur_masks = self.gen_masks(hurs_r[:self.num_ims],bboxes)
        self.y_dims = hur_masks.shape[1:]
        hur_masks = hur_masks.reshape(hur_masks.shape[0], np.prod(hur_masks.shape[1:]))
        tr_i, te_i, val_i = self.get_train_val_test_ix(self.num_ims)

        return self.set_up_train_test_val(hurs_r, bboxes, hur_masks, tr_i, te_i, val_i)



    def adjust_train_val_test_sizes(self,batch_size, X_train, y_train, X_val, y_val, X_test, y_test ):
        #make sure size of validation data a multiple of batch size (otherwise tough to match labels)

        train_end = batch_size * (X_train.shape[0] / batch_size)
        X_train = X_train[:train_end]
        y_train = y_train[:train_end]

        val_end = batch_size * (X_val.shape[0] / batch_size)
        X_val = X_val[:val_end]
        y_val = y_val[:val_end]

        #make sure size of test data a multiple of batch size
        test_end = batch_size * (X_test.shape[0] / batch_size)
        X_test = X_test[:test_end]
        y_test = y_test[:test_end]

        return X_train, y_train, X_val, y_val, X_test, y_test


    def get_train_val_test_ix(self, num_ims):
        # tr, te, val is 0.6,0.2,0.2
        ix = range(num_ims)

        #make sure they are all multiple of batch size
        n_te = int(0.2*num_ims)
        n_te -= n_te % self.batch_size
        n_val = self.batch_size * (int(0.25*(num_ims - n_te)) / self.batch_size)
        n_tr =  self.batch_size * ((num_ims - n_te - n_val) / self.batch_size)

        #shuffle once deterministically
        np.random.RandomState(3).shuffle(ix)
        te_i = ix[:n_te]
        rest = ix[n_te:]

        np.random.RandomState(self.seed).shuffle(rest)
        val_i = rest[:n_val]
        tr_i = rest[n_val:n_val + n_tr]
        return tr_i, te_i, val_i


    def set_up_train_test_val(self,hurs, boxes,hur_masks,tr_i,te_i, val_i):

        x_tr, y_tr, bbox_tr = hurs[tr_i], hur_masks[tr_i], boxes[tr_i]
        x_tr, tr_means, tr_stds = self.normalize_each_channel(x_tr)
        x_tr = x_tr.reshape(x_tr.shape[0], reduce(mul, x_tr.shape[1:]))

        x_te, y_te, bbox_te = hurs[te_i], hur_masks[te_i], boxes[te_i]
        x_te, _ ,_ = self.normalize_each_channel(x_te, tr_means, tr_stds)
        x_te = x_te.reshape(x_te.shape[0], reduce(mul, x_te.shape[1:]))

        x_val, y_val, bbox_val = hurs[val_i], hur_masks[val_i], boxes[val_i]
        x_val, _ ,_ = self.normalize_each_channel(x_val, tr_means, tr_stds)
        x_val = x_val.reshape(x_val.shape[0], reduce(mul, x_val.shape[1:]))

        x_dims = hurs.shape[1:]

        return (x_tr, y_tr, bbox_tr), \
        (x_te, y_te, bbox_te), \
        (x_val, y_val, bbox_val), x_dims, self.y_dims
        # return {'x_train': x_tr, 'y_train': y_tr, 'x_test': x_te, 'y_test': y_te,'x_val':x_val, 'y_val':y_val, 'boxes': boxes}

    def normalize_each_channel(self,arr, means=[], stds=[]):
        # assumes channels are on the axis 1
        if len(means) == 0:
            means = np.mean(arr, axis=(0, 2, 3))
        if len(stds) == 0:
            stds = np.std(arr, axis=(0, 2, 3))
        for channel, (mean, std) in enumerate(zip(means, stds)):
            arr[:, channel, :, :] -= mean
            arr[:, channel, :, :] /= std
        return arr, means, stds



    def gen_masks(self,hurs,bboxes):
        '''

        :param hurs: n_hurs x 8 x H x W array
        :param bboxes: n_hurs x 4 array
        :return:
            n_hurs x 2 x H x W array
                where the first cahnnel is p(hurricane) and second channel is p(not hurricane)

        '''
        t = time.time()
        p_hur = np.zeros((hurs.shape[0], hurs.shape[2],hurs.shape[3]))
        p_nhur = np.ones((hurs.shape[0], hurs.shape[2], hurs.shape[3]))

        #TODO: vectorize
        for i in range(hurs.shape[0]):
            bbox=bboxes[i]
            p_hur[i, bbox[0]:bbox[2],bbox[1]:bbox[3]] = 1.
            p_nhur[i, bbox[0]:bbox[2],bbox[1]:bbox[3]] = 0.
        print "gen_masks took: %5.2f seconds"%(time.time()-t)
        hur_masks = np.vstack((p_hur, p_nhur)).reshape(hurs.shape[0], 2, hurs.shape[2], hurs.shape[3])
        return hur_masks


if __name__ == "__main__":
    pass
    # path = sys.argv[1]
    # preproc_data_dir='./preproc_data'
    # load_hurricane(path, 1, 1, True, preproc_data_dir)








