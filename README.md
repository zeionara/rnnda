# Probabilistic-RNN-DA-Classifier

## How to use it on your dataset

0. Convert your dataset to required format and save it in some folder (for example `viot_data`). Fragment of the correctly formatted file:
```
летай над местностью если сработает датчик дыма сообщи|Command
доложи о состоянии урожая|Request
не убирайте листву при сильном ветре|IndirectCommand
опять пульт от телевизора потерял|IndirectCommand
ставь каждый день будильник на время|Command
распечатай показания счетчиков|Command
сделай панорамный снимок|Command
если за окном рассвет открой шторы|Command
```
1. Make metadata file  
`python -m process_all_swbd_data`  
2. Make embeddings (you may use your own embeddings - just put it in the folder `embeddings` and change script if name of your file does not correspond to template)  
`python -m generate_embeddings word2vec_ar100_dim.txt`  
3. Split all_text into train, val, test  
`python -m split_all_text`  
4. Generate pkls for subsets  
`python -m process_batch_swbd_data test`  
`python -m process_batch_swbd_data train`  
`python -m process_batch_swbd_data val`  
3. Train  
`python -m da_lstm`  
4. Observe beautiful picture  
![](https://github.com/zeionara/rnnda/raw/master/accuracy.png)

## Overview

An LSTM for Dialogue Act (DA) classification on the Switchboard Dialogue Act Corpus.
This is the implementation for the paper [Probabilistic Word Association for Dialogue Act Classification with Recurrent Neural Networks](https://www.researchgate.net/publication/326640934_Probabilistic_Word_Association_for_Dialogue_Act_Classification_with_Recurrent_Neural_Networks_19th_International_Conference_EANN_2018_Bristol_UK_September_3-5_2018_Proceedings).
The repository contains two LSTM models implemented in [Keras](https://keras.io/).
da_lstm.py uses utterance representations generated from pre-trained Word2Vec and GloVe word embeddings 
and probabilistic_lstm.py uses utterance representations generated from keywords selected for their frequency association with
certain DAs. 

Both models use the same architecture, with the ouput of the LSTM at each timestep combined using a max-pooling layer
before a final feed forward layer outputs the probability distribution over all DA labels for that utterance.

<p align="center">
<img src="/models/architecture.png">
</p>


## Datasets
The data directory contains pre-processed Switchboard DA Corpus data in raw-text (.txt) and .pkl format.
The same training and test splits as used by [Stolcke et al. (2000)](https://web.stanford.edu/~jurafsky/ws97) and an additional validation set is included.
The development set is a subset of the training set to speed up development and testing.

|Dataset    |# Transcripts  |# Utterances   |
|-----------|:-------------:|:-------------:|
|Training   |1115           |192,768        |
|Development|300            |51,611         |
|Test       |19             |4,088          |
|Validation |21             |3,196          |

## Metadata
words.txt and labels.txt contain full lists of the vocabulary and labels along with how frequently they occur.
metadata.pkl contains useful pre-processed data such as vocabulary and vocabulary size, DA label-to-index conversion dictionaries and maximum utterance length.

- num_utterances = Total number of utterance in the full corpus.
- max_utterance_len = Number of words in the longest utterance in the corpus.
- vocabulary = List of tuples (word, word frequency).
- vocabulary_size = Number of words in the vocabulary.
- index_to_word = Dictionary mapping vocabulary index to word.
- word_to_index = Dictionary mapping vocabulary word to index.
- labels = List of tuples (label, label frequency).
- num_labels = Number of labels used from the Switchboard data.
- label_to_index = Dictionary mappings label to index.
- index_to_label = Dictionary mapping index to label.

## Usage
#### Traditional Word Embeddings
To run da_lstm.py an embedding matrix must first be created from pre-trained embeddings such as word2vec or GloVe.
In the paper the model was tested on GloVe embeddings trained on Wikipedia data and Word2Vec trained on Google News.
The Word2Vec embeddings trained on the Switchboard corpus are included with this repository.
To generate the matrix simply run generate_embeddings.py after specifying the embeddings filename and directory (default = 'embeddings').
Then run da_lstm.py after specifying the name of the .pkl embeddings file generated by generate_embeddings.py.

#### Probabilistic Word Embeddings
To run probabilistic_lstm.py a probability matrix must first be created from the raw switchboard data.
Run generate_word_frequencies.py specifying the frequency threshold (freq_thresh) i.e. how many times a word may appear in the corpus to be considered (default = 2).
Then run probabilistic_lstm.py specifying the same word frequency (word_frequency) parameter.

#### Utility Files
- process_all_swbd_data.py - processes the entire corpus into raw-text and generates the metadata.pkl file.
- process_batch_swbd_data.py - processes only a specified list of transcripts from a text file i.e. test_split.txt.
- utilities.py - contains utility functions for saving and loading data and models as well as processing data for use at runtime.
- swda.py - contains utility functions for loading and iterating the switchboard transcripts and utterances in .csv format.
This file is part of the repository developed by Christopher Potts, and is available [here](https://github.com/cgpotts/swda).
