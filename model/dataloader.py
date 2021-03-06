import tensorflow as tf

class Dataloader(object):

    def __init__(self, file):
        self.file = file

    def read_list_file(self):
        with open(self.file, 'r') as f_in:
            lines = f_in.readlines()
        disp_file_list = []
        gt_file_list = []

        for l in lines:
            to_load = l.strip().split(';')
            disp_file_list.append(to_load[0])
            if len(to_load) > 1:
                gt_file_list.append(to_load[1])

        return disp_file_list, gt_file_list

    def read_image(self, image_path, shape=None, dtype=tf.uint8):
        image_raw = tf.read_file(image_path)
        if dtype == tf.uint8:
            image = tf.image.decode_image(image_raw)
        else:
            image = tf.image.decode_png(image_raw, dtype=dtype)
        if shape is None:
            image.set_shape([None, None, 3])
        else:
            image.set_shape(shape)
        return image


    def get_training_patches(self, disp_file, gt_file, patch_size):

        disp_list = []
        gt_list = []

        disp = tf.cast(self.read_image(disp_file, [None, None, 1]), tf.float32)
        disp_list.append(disp)

        gt = tf.cast(self.read_image(gt_file, [None, None, 1], dtype=tf.uint16), tf.float32) / 256.0
        gt_list.append(gt)

        disp_patches = tf.reshape(
            tf.extract_image_patches(images=disp_list, ksizes=[1, patch_size, patch_size, 1], strides=[1, 1, 1, 1], rates=[1, 1, 1, 1],
                                     padding='VALID'), [-1, patch_size, patch_size, 1])

        gt_patches = tf.reshape(
            tf.extract_image_patches(images=gt_list, ksizes=[1, patch_size, patch_size, 1], strides=[1, 1, 1, 1], rates=[1, 1, 1, 1],
                                     padding='VALID'), [-1, patch_size, patch_size, 1])

        mask = gt_patches[:, int(patch_size/2):int(patch_size/2)+1, int(patch_size/2):int(patch_size/2)+1, :] > 0
        valid = tf.tile(mask, [1, patch_size, patch_size, 1])

        disp_patches = tf.reshape(tf.boolean_mask(disp_patches, valid), [-1, patch_size, patch_size, 1])
        gt_patches = tf.reshape(tf.boolean_mask(gt_patches, valid), [-1, patch_size, patch_size, 1])

        labels = tf.cast(tf.abs(disp_patches - gt_patches) <= 3, tf.float32)

        return disp_patches, labels


    def get_testing_image(self, disp_file):
        return tf.cast(self.read_image(disp_file, [None, None, 1]), tf.float32)



