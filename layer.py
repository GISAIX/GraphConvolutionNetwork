import tensorflow as tf
from tensorflow.keras import layers
import matplotlib.pyplot as plt
from utilz import get_macro_data
import numpy as np


class GraphConvLayer(layers.Layer):

    def __init__(self,input_dim,output_dim,**kwargs):
        self.output_dim = output_dim
        self.input_dim = input_dim
        super(GraphConvLayer, self).__init__(**kwargs)
    
    def build(self,input_shape):
        shape = tf.TensorShape((input_shape[-1], self.output_dim))
        # Create a trainable weight variable for this layer.
        self.kernel = self.add_weight(name='kernel',
                                    shape=shape,
                                    initializer='uniform',
                                    trainable=True)

        # Be sure to call this at the end
        super(GraphConvLayer, self).build(input_shape)
    
    def call(self,inputs):
        #support * kernel ,support = D^(-0.5) * A' * D^(-0.5) * feature
        shape = inputs.get_shape()
        inputs = tf.reshape(inputs,[-1,self.input_dim])
        result = tf.matmul(inputs,self.kernel)
        result = tf.reshape(result,[-1,shape[1],self.output_dim])

        return tf.nn.relu(result)
    
    def compute_output_shape(self,input_shape):
        shape = tf.TensorShape(input_shape).as_list()
        shape[-1] = self.output_dim
        return tf.TensorShape(shape)
    
    def get_config(self):
        base_config = super(GraphConvLayer, self).get_config()
        base_config['output_dim'] = self.output_dim
        return base_config

    @classmethod
    def from_config(cls, config):
        return cls(**config)

class GraphConvLayer2(layers.Layer):
    def __init__(self,input_dim,output_dim,**kwargs):
        self.output_dim = output_dim
        self.input_dim = input_dim
        super(GraphConvLayer, self).__init__(**kwargs)
    
    def build(self,input_shape):
        shape = tf.TensorShape((input_shape[-1], self.output_dim))
        # Create a trainable weight variable for this layer.
        self.kernel = self.add_weight(name='kernel',
                                    shape=shape,
                                    initializer='uniform',
                                    trainable=True)

        # Be sure to call this at the end
        super(GraphConvLayer, self).build(input_shape)
    
    def call(self,inputs):
        #support * kernel ,support = D^(-0.5) * A' * D^(-0.5) * feature
        shape = inputs.get_shape()
        inputs = tf.reshape(inputs,[-1,self.input_dim])
        result = tf.matmul(inputs,self.kernel)
        result = tf.reshape(result,[-1,shape[1],self.output_dim])

        return tf.nn.relu(result)
    
    def compute_output_shape(self,input_shape):
        shape = tf.TensorShape(input_shape).as_list()
        shape[-1] = self.output_dim
        return tf.TensorShape(shape)
    
    def get_config(self):
        base_config = super(GraphConvLayer, self).get_config()
        base_config['output_dim'] = self.output_dim
        return base_config

    @classmethod
    def from_config(cls, config):
        return cls(**config)
def NN():

    model = tf.keras.Sequential()
    model.add(layers.Flatten())

    model.add(layers.Dense(32,activation="relu"))
    model.add(layers.Dense(16,activation="relu"))
    model.add(layers.Dense(1))

    model.compile(optimizer=tf.train.AdamOptimizer(0.001),
                loss='mean_squared_error',metrics=['mae'])

    data_dict = get_macro_data()
    
    data = data_dict["Adj"] + data_dict["P"]
    data = np.asarray(data)

    labels = data_dict["accuracy"]
    labels = np.asarray(labels)

    # val_data = np.random.random((100, 32))
    # val_labels = np.random.random((100, 10))

    history = model.fit(data[:3000], labels[:3000], epochs=100, batch_size=32,
    validation_split=0.2)

    plt.plot(history.history['mean_absolute_error'])
    plt.plot(history.history['val_mean_absolute_error'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.show()
def GCN():

    data_dict = get_macro_data()
    
    A = data_dict["Adj"]
    D = data_dict["D"]
    feature = data_dict["P"]
    features = np.sum(feature,axis=2)


    data = np.asarray(A)
    datashape = np.shape(data)

    
    A_bar = A + np.eye(datashape[1],datashape[2])
    D_bar = D + np.eye(datashape[1],datashape[2])

    for i in range(len(D_bar)):
        for j in range(len(D_bar[0])):
            D_bar[i][j][j] = 1/np.sqrt(D_bar[i][j][j])
    
    supports = []
    for i in range(len(A_bar)):
        support = np.matmul(np.matmul(D_bar[i],A_bar[i]),D_bar[i])
        support = np.matmul(support,features[i])
        supports.append(np.reshape(support,[12,1]))
    supports = np.asarray(supports)

    labels = data_dict["accuracy"]
    labels = np.reshape(labels,(len(labels),1))

    indice = [i for i in range(len(supports))]
    np.random.shuffle(indice)

    shuffled_supports = []
    shuffled_labels = []
    for i in indice:
        shuffled_supports.append(supports[i])
        shuffled_labels.append(labels[i])

    shuffled_supports = np.asarray(shuffled_supports)
    shuffled_labels = np.asarray(shuffled_labels)
    # need to make feature as data
    # need to compute D^(-0.5) and A+I
    model = tf.keras.Sequential()

    model.add(GraphConvLayer(1,8))
    model.add(layers.Flatten())
    model.add(layers.Dense(32,activation="relu"))
    model.add(layers.Dense(16,activation="relu"))
    model.add(layers.Dense(1))


    model.compile(optimizer=tf.train.AdamOptimizer(0.01),
                loss='mse',metrics=['mae'])


    # val_data = np.random.random((100, 32))
    # val_labels = np.random.random((100, 10))

    history = model.fit(shuffled_supports[:3000], shuffled_labels[:3000], 
            epochs=100, batch_size=32,
            validation_split=0.2)

    plt.plot(history.history['mean_absolute_error'])
    plt.plot(history.history['val_mean_absolute_error'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.show()



if __name__ == "__main__":
    #GCN()
    NN()