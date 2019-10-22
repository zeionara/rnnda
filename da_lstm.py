import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import datetime
import time
from keras.models import load_model
from utilities import *
from keras import Sequential
from keras.layers import LSTM, TimeDistributed, Dense, GlobalMaxPooling1D, Embedding
from keras.optimizers import RMSprop

resource_dir = 'viot_data/'
embeddings_dir = "embeddings/"
embedding_filename = "word2vec_ar100"#'word2vec_GoogleNews'
model_dir = 'models/'
model_name = "embeddings-model-new"

# Load metadata
metadata = load_data(resource_dir + "metadata.pkl")
embeddings_dimension = 100
print(embeddings_dir + embedding_filename + '_' + str(embeddings_dimension) + 'dim.pkl')
embeddings = load_data(embeddings_dir + embedding_filename + '_' + str(embeddings_dimension) + 'dim.pkl')

# Load Training and test sets
train_data = load_data(resource_dir + 'train_data.pkl')
train_x, train_y = generate_embeddings(train_data, metadata)

test_data = load_data(resource_dir + 'test_data.pkl')
test_x, test_y = generate_embeddings(test_data, metadata)

val_data = load_data(resource_dir + 'val_data.pkl')
val_x, val_y = generate_embeddings(val_data, metadata)

# Parameters
vocabulary_size = metadata['vocabulary_size']
num_labels = metadata['num_labels']
max_utterance_len = metadata['max_utterance_len']
embedding_matrix = embeddings['embedding_matrix']
batch_size = 200
hidden_layer = 128
learning_rate = 0.001
num_epoch = 10
model_name = model_name + " -" + \
             " Epochs=" + str(num_epoch) + \
             " Hidden Layers=" + str(hidden_layer)

print("------------------------------------")
print("Using parameters...")
print("Vocabulary size: ", vocabulary_size)
print("Number of labels: ", num_labels)
print("Embeddings dimension: ", embeddings_dimension)
print("Batch size: ", batch_size)
print("Hidden layer size: ", hidden_layer)
print("learning rate: ", learning_rate)
print("Epochs: ", num_epoch)

# Build the model
print("------------------------------------")
print('Build model...')
model = Sequential()
model.add(Embedding(vocabulary_size, embeddings_dimension, input_length=max_utterance_len, weights=[embedding_matrix], mask_zero=False))
model.add(LSTM(hidden_layer, dropout=0.3, return_sequences=True, kernel_initializer='random_uniform', recurrent_initializer='glorot_uniform'))
model.add(TimeDistributed(Dense(hidden_layer, input_shape=(max_utterance_len, hidden_layer))))
model.add(GlobalMaxPooling1D())
model.add(Dense(num_labels, activation='softmax'))

optimizer = RMSprop(lr=learning_rate, decay=0.001)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
print(model.summary())

# Train the model
print("------------------------------------")
print("Training model...")

start_time = time.time()
print("Training started: " + datetime.datetime.now().strftime("%b %d %T") + " for", num_epoch, "epochs")

history = model.fit(train_x, train_y, epochs=num_epoch, batch_size=batch_size, validation_data=(test_x, test_y), verbose=2)

# Save model and history
model.save(model_dir + model_name + '.hdf5', overwrite=True)
save_data(model_dir + model_name + ' History.pkl', history.history)

end_time = time.time()
print("Training took " + str(('%.3f' % (end_time - start_time))) + " seconds for", num_epoch, "epochs")
# Plot training accuracy  and loss
fig = plot_history(history.history, model_name)
fig.show()
fig.savefig(model_dir + model_name + ' Accuracy and Loss.png')

# Evaluate the model
print("------------------------------------")
print("Evaluating model...")
model = load_model(model_dir + model_name + '.hdf5')

# Test set
test_scores = model.evaluate(test_x, test_y, batch_size=batch_size, verbose=2)
print("Test data: ")
print("Loss: ", test_scores[0], " Accuracy: ", test_scores[1])

# Validation set
val_scores = model.evaluate(val_x, val_y, batch_size=batch_size, verbose=2)
print("Validation data: ")
print("Loss: ", val_scores[0], " Accuracy: ", val_scores[1])

test_predictions = batch_prediction(model, test_data, test_x, test_y, metadata, batch_size, verbose=False)
val_predictions = batch_prediction(model, val_data, val_x, val_y, metadata, batch_size, verbose=False)

# Generate confusion matrix
test_matrix = generate_confusion_matrix(test_data, test_predictions, metadata, verbose=False)
val_matrix = generate_confusion_matrix(val_data, val_predictions, metadata, verbose=False)

# Plot confusion matrices

# class_names = ['non-opinion', 'backchannel', 'opinion', 'abandoned', 'agree']
# fig = plot_confusion_matrix(test_matrix, class_names, title='Test', matrix_size=5, normalize=True)

class_names = [class_name[0] for class_name in metadata['labels']]
fig = plot_confusion_matrices(test_matrix, val_matrix, class_names, title_a='Test', title_b='Validation', matrix_size=5, normalize=True)
plt.savefig("accuracy.png")
fig.show()
fig.savefig(model_dir + model_name + ' Confusion Matrix.png', transparent=True)
