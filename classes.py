from glob import glob
from SEGMENTATION.utils import count_images, open_masks, rm_alpha
import torch
import os
from PIL import Image 
import numpy as np
from torch.utils.data import Dataset

class MonusacDataset(Dataset):
    '''MoNuSAC Dataset.'''

    def __init__(self, img_dir, masks_dir, transform=None):
        '''
        Arguments:
            img_dir (string): Directory with all the images.
            mask_dir (string): Directory with all the masks.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        '''

        self.img_dir = img_dir
        self.masks_dir = masks_dir
        self.transform = transform

    def __len__(self):
        return count_images(self.img_dir)

    def __getitem__(self, idx):
      
      #image extraction
      images = [y for x in os.walk(self.img_dir) for y in glob(os.path.join(x[0], '*.tif'))]

      img_path = images[idx]
      img_path = os.path.normpath(img_path)
      path_as_list = img_path.split('/')
      patient_code = path_as_list[-2]
      img_name = path_as_list[-1].split('.')[0]
      image = Image.open(images[idx])
      image = np.asarray(image)

      #mask extraction
      img_masks = []

      masks_folder_path = os.path.join(self.masks_dir, patient_code, img_name)
      ep, lym, macro, neutr = open_masks(masks_folder_path, image.shape)

      image = rm_alpha(image)

      sample = {'name': img_name, 'image': image, 'mask_ep': ep, 'mask_lym': lym, 'mask_macro': macro, 'mask_neutr': neutr}

      if self.transform:
        sample = self.transform(sample)

      return sample