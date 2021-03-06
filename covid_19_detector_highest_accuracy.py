# -*- coding: utf-8 -*-
"""COVID-19-Detector-Highest-Accuracy.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PGtd58hc-u6maFeUhdm_CP727kWSeInZ
"""

# Dataset : http://cb.lk/covid_19

!wget http://cb.lk/covid_19

"""**EXTRACT,** **TRANSFORM** **AND** **LOAD** **THE** **DATA**"""

!unzip covid_19

TRAIN_PATH = "CovidDataset/Train"
VAL_PATH = "CovidDataset/Test"

import numpy as np
import matplotlib.pyplot as plt
import keras
from keras.layers import *
from keras.models import * 
from keras.preprocessing import image

"""**BUILDING** **THE** **CNN** **MODEL**"""

# CNN Based Model in Keras

model = Sequential()
model.add(Conv2D(32,kernel_size=(3,3),activation='relu',input_shape=(224,224,3)))
model.add(Conv2D(64,(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))

model.add(Conv2D(64,(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))

model.add(Conv2D(128,(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(1,activation='sigmoid'))

model.compile(loss=keras.losses.binary_crossentropy,optimizer='adam',metrics=['accuracy',keras.metrics.Precision(), keras.metrics.Recall(),keras.metrics.FalseNegatives(),keras.metrics.FalsePositives(),keras.metrics.TrueNegatives(),keras.metrics.TruePositives()])

model.summary()

"""**DATA** **AUGMENTATION**"""

# Train from scratch
train_datagen = image.ImageDataGenerator(
    rescale = 1./255,
    shear_range = 0.2,
    zoom_range = 0.2,
    horizontal_flip = True,
)

test_dataset = image.ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    'CovidDataset/Train',
    target_size = (224,224),
    batch_size = 32,
    class_mode = 'binary')

train_generator.class_indices

validation_generator = test_dataset.flow_from_directory(
    'CovidDataset/Val',
    target_size = (224,224),
    batch_size = 32,
    class_mode = 'binary')

hist = model.fit_generator(
    train_generator,
    steps_per_epoch=224,
    epochs = 5,
    validation_data = validation_generator,
    validation_steps=60
)

import matplotlib.pyplot as plt


# summarize history for accuracy
plt.plot(hist.history['accuracy'])
plt.plot(hist.history['val_accuracy'])
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.plot(hist.history['recall_1'])
plt.plot(hist.history['val_recall_1'])
plt.plot(hist.history['precision_1'])
plt.plot(hist.history['val_precision_1'])


plt.legend(['train_acc', 'val_acc','train_loss','val_loss','recall_1','val_recall_1','precision_1','val_precision_1'], loc='center right')
plt.title('model accuracy and loss')
plt.ylabel('metrics')
plt.xlabel('epoch')
plt.show()

# summarize history for accuracy
plt.plot(hist.history['accuracy'])
plt.plot(hist.history['loss'])


plt.legend(['train_acc','train_loss'], loc='center right')
plt.title('model accuracy and loss')
plt.ylabel('metrics')
plt.xlabel('epoch')
plt.show()

# summarize history for loss
plt.figure(figsize=(5,5))
plt.plot(hist.history['true_positives_1'])
plt.plot(hist.history['true_negatives_1'])
plt.plot(hist.history['false_positives_1'])
plt.plot(hist.history['false_negatives_1'])
plt.title('confusion matrix metric')
plt.legend(['true_positives_1', 'true_negatives_1','false_positives_1','false_negatives_1'], loc='center right')
plt.ylabel('metric')
plt.xlabel('epoch')
plt.show()

from keras.utils.vis_utils import plot_model
plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)

a=hist.history['true_positives_1'][0]
print(a)

b=hist.history['false_positives_1'][0]
print(b)

c=hist.history['true_negatives_1'][0]
print(c)

d=hist.history['false_negatives_1'][0]
print(d)

sensitivity = a/a+d
print(sensitivity)

specificity = c/c+b
print(specificity)

import cv2

def get_class_activation_map(path) :
    
    img_path =  path
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))
    img = np.expand_dims(img,axis=0)
    
    predict = model.predict(img)
    target_class = np.argmax(predict[0])
    last_conv = model.get_layer(index = 7)
    grads =K.gradients(model.output[:,target_class],last_conv.output)[0]
    pooled_grads = K.mean(grads,axis=(0,1,2))
    iterate = K.function([model.input],[pooled_grads,last_conv.output[0]])
    pooled_grads_value,conv_layer_output = iterate([img])
    
    for i in range(512):
        conv_layer_output[:,:,i] *= pooled_grads_value[i]
    
    heatmap = np.mean(conv_layer_output,axis=-1)
    
    for x in range(heatmap.shape[0]):
        for y in range(heatmap.shape[1]):
            heatmap[x,y] = np.max(heatmap[x,y],0)
    heatmap = np.maximum(heatmap,0)
    heatmap /= np.max(heatmap)
    plt.imshow(heatmap)
    img_gray = cv2.cvtColor(img[0], cv2.COLOR_BGR2GRAY)
    upsample = cv2.resize(heatmap, (224,224))

"""**PREDICTING** **/** **DECISION** **MAKING**"""

img = image.load_img('CovidDataset/Val/Normal/NORMAL2-IM-1037-0001.jpeg', target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)

images = np.vstack([x])
classes = model.predict_classes(images, batch_size=10)
#print(classes)

if classes == 1:
  print('Normal Case')
else:
  print('Covid-19 Case')

img = image.load_img('CovidDataset/Train/Covid/extubation-4.jpg', target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)

images = np.vstack([x])
classes = model.predict_classes(images, batch_size=10)
#print(classes)

if classes == 1:
  print('Normal Case')
else:
  print('Covid-19 Case')

model.save('covid_final.h5')

