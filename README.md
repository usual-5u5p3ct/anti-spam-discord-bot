# anti-spam-discord-bot
Anti-Spam Discord Bot for Final Year Project


This project, developed using Python, involves the creation of a bot utilizing the Discord API and training a model using the SVM algorithm in Jupyter Notebook. The trained model is utilized to detect spam messages using SMS (Short Message Service). The model, developed using Python and trained with the SVM (Support Vector Machine) algorithm, aims to accurately classify incoming SMS messages as either spam or non-spam (ham). Once the model is trained, it can be deployed to classify incoming SMS messages in real-time. When a new SMS message arrives, the model takes the message as input, processes it using the same feature extraction techniques as during training, and then makes a prediction on whether the message is spam or ham. The model's prediction is based on the patterns it has learned from the training data. By comparing the message's features to those present in the labeled dataset, the model assigns a probability or a class label indicating the likelihood of the message being spam.

Even though project already met requirements, there are still additional features are currently being implemented to enhance the project.

Spam dataset was collected from Kaggle: https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset
