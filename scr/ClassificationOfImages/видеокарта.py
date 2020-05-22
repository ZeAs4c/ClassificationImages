# -*- coding: utf-8 -*-
"""Untitled15.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eg-CRRwjoxaAgB-UKqk0Qbs0nRMG9Tn6
"""

# Подгружаем библиотеки.

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

# Настройки гиперпараметров.

NUM_EPOCHS = 20 # Количество эпох.
BATCH_SIZE = 256 # Количество картинок за эпоху.
LEARNING_RATE = 0.001 # Скорость обучения (Доля градиента, по которой веса обновляются на каждой итерации цикла обучения.)

# Загрузка данных.

(train_x, train_y), (test_x, test_y) = tf.keras.datasets.mnist.load_data()

# Смотрим что у нас в дата сете.
print(train_x.shape, train_x.dtype)

print(train_x.shape, train_x.dtype)
print(train_y.shape, train_y.dtype)
print(test_x.shape, test_x.dtype)
print(test_y.shape, test_y.dtype)

# Преобразуем данные, которые у нас загружены для сохраниния правильного размера вектора при подаче в обучении.

train_x = train_x.reshape(-1, 28, 28, 1).astype(np.float32)/255.
test_x = test_x.reshape(-1, 28, 28, 1).astype(np.float32)/255.

train_y = train_y.astype(np.int32)
test_y = test_y.astype(np.int32)

# Еще раз смотри что теперь у нас в датасете.
print(train_x.shape, train_x.dtype)
print(train_y.shape, train_y.dtype)
print(test_x.shape, test_x.dtype)
print(test_y.shape, test_y.dtype)

# Для примера возьмем 100 картинок.
test_samples = train_x[:100,...]

# Выведем на экран, посмотреть наши картинки (смотрим что у нас в дата сете).
fig = plt.figure(figsize=(5, 20))
for j in range(test_samples.shape[0]):
    ax = fig.add_subplot(20, 5, j+1)
    ax.imshow(test_samples[j, :, :, 0], cmap="BuPu") # или cmap = "red".
    plt.xticks([]), plt.yticks([])
plt.show()

# Преобразуем данные в датасет, который мы будем подавать.

train_ds = tf.data.Dataset.from_tensor_slices((train_x, train_y))
train_ds = train_ds.shuffle(buffer_size=train_x.shape[0])
train_ds = train_ds.repeat(NUM_EPOCHS)
train_ds = train_ds.batch(BATCH_SIZE)

# Создаем модель (которая была показана на картинке в вебинаре) ее функциями.

class klon(tf.keras.Model):

    def __init__(self):
        super(klon, self).__init__()
        self.Conv1 = tf.compat.v1.layers.Conv2D(32, (5, 5), activation= tf.nn.relu, padding= "same")
        self.Conv2 = tf.compat.v1.layers.Conv2D(64, (5, 5), activation= tf.nn.relu, padding= "same")
        self.Fc1 = tf.compat.v1.layers.Dense(256, activation= tf.nn.sigmoid)
        self.Fc2 = tf.compat.v1.layers.Dense(10, activation= tf.nn.softmax)
        self.MaxPooling = tf.compat.v1.layers.MaxPooling2D((2, 2), (2, 2), padding="same")

    def __call__(self, inp):
        out = self.Conv1(inp)
        out = self.MaxPooling(out)
        out = self.Conv2(out)
        out = self.MaxPooling(out)
        out = tf.compat.v1.layers.flatten(out)
        out = self.Fc1(out)
        out = self.Fc2(out)
        return out

model = klon()

# Функция для вычисления ошибки сети.
def loss(logits, labels):
    return tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=labels))

# Создаем функицю точности.

def accuracy(logits, labels):
    predictions = tf.argmax(logits, axis=1, output_type=tf.int32)
    return tf.reduce_mean(tf.cast(tf.equal(predictions, labels), dtype=tf.float32))

# Устанавливаем оптимизатор.

optimizer = tf.compat.v1.train.AdamOptimizer(LEARNING_RATE)

# Задаем глобальный шаг.
global_step = tf.compat.v1.train.get_or_create_global_step()

for (images, labels) in train_ds:

    # Прямое распространение.
    
    with tf.GradientTape() as tape:
        logits = model(images)
        loss_value = loss(logits, labels)
        
    # Обратное распространение.
    
    grads = tape.gradient(loss_value, model.variables)
    optimizer.apply_gradients(zip(grads, model.variables), global_step=global_step)

    if global_step.numpy() % 200 == 0:
        test_logits = model(test_x[:512, ...])
        accuracy_value = accuracy(test_logits, test_y[:512, ...])
        print(f"[{global_step.numpy()}] Accuracy {accuracy_value.numpy()*100}")

# Подсчитываем финальную точность.

test_logits = model(test_x)
accuracy_value = accuracy(test_logits, test_y).numpy()
print(f"Final Accuracy:{accuracy_value*100}%")

# Создаем функицю проверки цифры.

def test_digit(sample):

    sample = sample[np.newaxis, ...]
    logits = model(sample)
    prediction = tf.nn.softmax(logits)
    ans = np.argmax(prediction)

    fig = plt.figure(figsize=(12, 4))

    ax = fig.add_subplot(1, 2, 1)
    ax.imshow(sample[0, :, :, 0], cmap=plt.cm.binary)
    plt.xticks([]), plt.xticks([])

    ax = fig.add_subplot(1, 2, 2)
    bar_list = ax.bar(np.arange(10), prediction[0], align="center")
    bar_list[ans].set_color("g")
    ax.set_xticks(np.arange(10))
    ax.set_xlim([-1, 10])
    ax.grid(True)

    plt.show()

    print(f"Predicted:{ans}")

# Выводим картинку случайно выбранной цифры и предсказания нейросети.

import random

idx = random.randint(0, test_x.shape[0])
sample = test_x[idx, ...]
test_digit(sample)

print(f"Right answer:{test_y[idx]}")