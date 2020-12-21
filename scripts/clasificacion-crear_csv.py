import os
import pandas as pd
import numpy as np
import joblib
from imutils import paths
from sklearn.preprocessing import LabelBinarizer
from tqdm import tqdm

PATH_DATASET_CLASIFICACION = './dataset/dataset-clasificacion'
# get all the image paths
image_paths = list(paths.list_images(PATH_DATASET_CLASIFICACION))

# create an empty DataFrame
data = pd.DataFrame()
labels = []
for i, image_path in tqdm(enumerate(image_paths), total=len(image_paths)):
    label = image_path.split(os.path.sep)[-2]
    data.loc[i, 'image_path'] = image_path
    labels.append(label)
    
labels = np.array(labels)

# one hot encode
lb = LabelBinarizer()
labels = lb.fit_transform(labels)
print(f"The first one hot encoded labels: {labels[0]}")
print(f"Mapping an one hot encoded label to its category: {lb.classes_[0]}")
print(f"Total instances: {len(labels)}")
for i in range(len(labels)):
    index = np.argmax(labels[i])
    data.loc[i, 'target'] = int(index)

# shuffle the dataset
data = data.sample(frac=1).reset_index(drop=True)

# save as csv file
data.to_csv(f'{PATH_DATASET_CLASIFICACION}/data.csv', index=False)

# pickle the label binarizer
joblib.dump(lb, f'{PATH_DATASET_CLASIFICACION}/lb.pkl')
print('Save the one-hot encoded binarized labels as a pickled file.')
print(data.head())

