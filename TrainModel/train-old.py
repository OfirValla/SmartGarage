#from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, Sequential
from matplotlib import pyplot as plt
import tensorflow as tf
import datetime
import keras
import os

train_date = datetime.datetime.now().strftime('%Y%m%d-%H%M')

epochs=25
batch_size = 16
img_height = img_width = 224
image_size = (img_height, img_width)

def make_model(input_shape, num_classes):
    inputs = keras.Input(shape=input_shape)

    x = layers.Rescaling(1.0 / 255)(inputs)
    x = layers.Conv2D(128, 3, strides=2, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    previous_block_activation = x 

    for size in [256, 512, 768]:
        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.MaxPooling2D(3, strides=2, padding="same")(x)

        residual = layers.Conv2D(size, 1, strides=2, padding="same")(
            previous_block_activation
        )
        x = layers.add([x, residual])  
        previous_block_activation = x  # Set aside next residual

    x = layers.SeparableConv2D(1024, 3, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    x = layers.GlobalAveragePooling2D()(x)
    if num_classes == 2:
        activation = "sigmoid"
        units = 1
    else:
        activation = "softmax"
        units = num_classes

    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(units, activation=activation)(x)
    return keras.Model(inputs, outputs)

os.mkdir(f"models/{train_date}")


train_ds = tf.keras.utils.image_dataset_from_directory(
    r"D:\GateStatus\old-dataset",
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    r"D:\GateStatus\old-dataset",
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size
)

for image_batch, labels_batch in train_ds:
  print(image_batch.shape)
  print(labels_batch.shape)
  break

#datagen = ImageDataGenerator(brightness_range=[0.5,2.0])
#datagen = ImageDataGenerator(featurewise_center =True, featurewise_std_normalization = True)

num_classes = len(train_ds.class_names)
print(train_ds.class_names) # ['Closed', 'Open', 'OpeningOrClosing']

with open(f'models/{train_date}/labels.txt', 'w') as f:
    for label in train_ds.class_names:
        f.write(f'{label}\n')

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

model = make_model(input_shape=image_size + (3,), num_classes=num_classes)
keras.utils.plot_model(model, show_shapes=True, to_file=f'models/{train_date}/model.png',)

#model = Sequential([
#  layers.Rescaling(1./255),
#  layers.Conv2D(16, 3, padding='same', activation='relu'),
#  layers.MaxPooling2D(),
#  layers.Conv2D(32, 3, padding='same', activation='relu'),
#  layers.MaxPooling2D(),
#  layers.Conv2D(64, 3, padding='same', activation='relu'),
#  layers.MaxPooling2D(),
#  layers.Dropout(0.2),
#  layers.Flatten(),
#  layers.Dense(128, activation='relu'),
#  layers.Dense(num_classes, name="outputs")
#], name="GateAi")

#model = Sequential([
    #tf.keras.layers.Flatten(input_shape=(img_height, img_width, 3)),
    #tf.keras.layers.Dense(128, activation='relu'),
    #tf.keras.layers.Dense(num_classes)
    
    #layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
    #layers.Conv2D(16, 3, padding='same', activation='relu'),
    #layers.MaxPooling2D(),
    #layers.Conv2D(32, 3, padding='same', activation='relu'),
    #layers.MaxPooling2D(),
    #layers.Conv2D(64, 3, padding='same', activation='relu'),
    #layers.MaxPooling2D(),
    #layers.Flatten(),
    #layers.Dense(128, activation='relu'),
    #layers.Dense(num_classes, activation='softmax'),

    #tf.keras.layers.Flatten(input_shape=(img_height, img_width, 1)),
    #tf.keras.layers.Dense(128, activation='relu'),
    #tf.keras.layers.Dense(num_classes, activation='softmax')
#])

callbacks = [
    keras.callbacks.ModelCheckpoint(f"models/{train_date}/progress/save_at_{{epoch}}.keras"),
]
model.compile(
    optimizer=keras.optimizers.Adam(1e-3),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics=["accuracy"],
)

print (model.summary())

history = model.fit(
    train_ds,
    epochs=epochs,
    callbacks=callbacks,
    validation_data=val_ds,
)



#model.compile(
#    optimizer='adam',
#    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
#    metrics=['accuracy']
#)


#history = model.fit(
#  train_ds,
#  validation_data=val_ds,
#  epochs=epochs
#)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

print("done")

#probability_model = tf.keras.Sequential(
#    [
#        model, 
#        tf.keras.layers.Softmax()
#    ]
#)

#probability_model.save('saved_model/SavedModel')
#probability_model.save('saved_model/model.h5')

model.save(f'models/{train_date}/model.h5')