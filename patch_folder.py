def patch_folder(images_path: str, masks_path: str, dataset_name: str, out_dir_name: str, win_size:list, step_size: list, extract_type: str, type_classification: bool = True, merge_dir: bool = True, test: bool = False, blue_chan: bool = False, working_dir: str = '\content'):
  '''Creates train and validation patch directory and set the output directory for the patches
  to the given name.

  Args:
    images_path: a string indicating the path of the training folder
    masks_path: a string indicating the path of the masks folder
    dataset_name: a string indicating the name of the user's dataset ('Kumar', 'CPM17' or 'CoNSeP')
    out_dir_name: a string indicating the name given to the output directory ('train' or 'test')
    win_size: a list containing the x and y size of the patch window
    step_size: a list containing the x and y size of the step
    extract_type: a string containing the type of patch extraction ('valid' or 'mirror')
    type_classification: boolean determining whether to extract type map (only applicable to datasets with class labels)
    merge_dir: boolean determining whether the directories black_patches and patches have to be merged
    test: boolean determining if the input dataset is for train or test purpose
    blue_chan: boolean determining if images have three channels or only the blue one
    working_dir: where to save the patches
    '''
  import cv2
  import random
  import shutil
  import tqdm
  import numpy as np
  from SEGMENTATION.classes import MonusacDataset
  from SEGMENTATION.patch_extractor import PatchExtractor
  from hover_net.misc.utils import rm_n_mkdir

  dataset = MonusacDataset(images_path, masks_path, blue_chan=blue_chan)
  save_root = working_dir + '/patches'
  save_root_black = working_dir + '/black_patches'
  parser = MonusacDataset
  xtractor = PatchExtractor(win_size, step_size)
  if blue_chan:
    img_channels = 1
  else:
    img_channels = 3

  #create patches' directory
  out_dir = '%s/%s/%s/%dx%d_%dx%d/' % (
      save_root,
      dataset_name,
      out_dir_name,
      win_size[0],
      win_size[1],
      step_size[0],
      step_size[1],
  )

  rm_n_mkdir(out_dir)
  pbar_format = "Process File: |{bar}| {n_fmt}/{total_fmt}[{elapsed}<{remaining},{rate_fmt}]"
  pbarx = tqdm.tqdm(
      total=len(dataset), bar_format=pbar_format, ascii=True, position=0
  )

  #create black patches' directory
  out_dir_black = '%s/%s/%s/%dx%d_%dx%d/' % (
      save_root_black,
      dataset_name,
      out_dir_name,
      win_size[0],
      win_size[1],
      step_size[0],
      step_size[1],
  )

  rm_n_mkdir(out_dir_black)
  pbar_format = "Process File: |{bar}| {n_fmt}/{total_fmt}[{elapsed}<{remaining},{rate_fmt}]"
  pbarx = tqdm.tqdm(
      total=len(dataset), bar_format=pbar_format, ascii=True, position=0
  )

  # extract the patches with given win_size and step_size
  for file_idx in range(len(dataset)):

    base_name = dataset[file_idx]['name']
    img = dataset[file_idx]['image']
    ep = dataset[file_idx]['mask_ep']
    lym = dataset[file_idx]['mask_lym']
    macro = dataset[file_idx]['mask_macro']
    neutr = dataset[file_idx]['mask_neutr']
    conc = np.concatenate((img, ep, lym, macro, neutr), axis=-1)
    if test:
      amb = dataset[file_idx]['mask_amb']
      conc = np.concatenate((img, amb, ep, lym, macro, neutr), axis=-1)

    pad_win_dim = [img.shape[0] + win_size[0] - step_size[0], img.shape[1] + win_size[1] - step_size[1]]
    if(pad_win_dim[0] < win_size[0] or pad_win_dim[1] < win_size[1]):
      continue

    sub_patches, black_patches = xtractor.extract(conc, extract_type)
    pbar_format = "Extracting  : |{bar}| {n_fmt}/{total_fmt}[{elapsed}<{remaining},{rate_fmt}]"
    pbar = tqdm.tqdm(
      total=len(sub_patches),
      leave=False,
      bar_format=pbar_format,
      ascii=True,
      position=1,
    )

    if(merge_dir):
      patches = sub_patches + black_patches
      random.shuffle(patches)

      for idx, patch in enumerate(patches):
        patch_norm = cv2.normalize(patch[:,:,:img_channels], None, 0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        if len(patch_norm.shape) == 2:
          patch_norm= np.expand_dims(patch_norm, axis=-1)
        patch_masks = patch[:,:,img_channels:]
        patch = np.concatenate((patch_norm, patch_masks), axis=-1)
        np.save("{0}/{1}_{2:03d}.npy".format(out_dir, base_name, idx), patch)
        pbar.update()
      pbar.close()
      # *
      pbarx.update()
      pbarx.close()

    else:
      for idx, patch in enumerate(sub_patches):
        patch_norm = cv2.normalize(patch[:,:,:img_channels], None, 0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        if len(patch_norm.shape) == 2:
          patch_norm= np.expand_dims(patch_norm, axis=-1)
        patch_masks = patch[:,:,img_channels:]
        patch = np.concatenate((patch_norm, patch_masks), axis=-1)
        np.save("{0}/{1}_{2:03d}.npy".format(out_dir, base_name, idx), patch)
        pbar.update()
      pbar.close()
      # *
      pbarx.update()
      pbarx.close()
      for idx, patch in enumerate(black_patches):
        patch_norm = cv2.normalize(patch[:,:,:img_channels], None, 0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        if len(patch_norm.shape) == 2:
          patch_norm= np.expand_dims(patch_norm, axis=-1)
        patch_masks = patch[:,:,img_channels:]
        patch = np.concatenate((patch_norm, patch_masks), axis=-1)
        np.save("{0}/{1}_{2:03d}.npy".format(out_dir_black, base_name, idx), patch)
        pbar.update()
      pbar.close()
      # *
      pbarx.update()
      pbarx.close()

  if(merge_dir):
    shutil.rmtree(save_root_black)
