import pickle
import sklearn
import catboost

def import_model_data(path_tokenizer, path_model, path_classes):
    """ 
    Description:
        Imports model data from pickle-files
    Parameters:
        path_tokenizer (str): Full path to pickle-file
        path_model (str): Full path to pickle-file
        path_classes (str): Full path to pickle-file
    Returns:
        tokenizer (sklearn.feature_extraction.text.CountVectorizer): Tokenizer to vectorize texts
        model (catboost.core.CatBoostClassifier): Model for predicting on tokenized texts
        classes (numpy.ndarray): Object to map integers to classes
    """
    tokenizer = pickle.load(open(path_tokenizer, 'rb'))
    model = pickle.load(open(path_model, 'rb'))
    classes = pickle.load(open(path_classes, 'rb'))
    
    return tokenizer, model, classes

def predict_class(text, tokenizer, model, classes):
    """ 
    Description:
        Tokenizes and predicts class for text
    Parameters:
        text (str): Text to be classified
        tokenizer (sklearn.feature_extraction.text.CountVectorizer): Tokenizer to vectorize texts
        model (catboost.core.CatBoostClassifier): Model for predicting on tokenized texts
        classes (numpy.ndarray): Object to map integers to classes
    Returns:
        class (str): Class text has been predicted to be in
    """
    vectorized_text = tokenizer.transform([text])
    prediction_integer = model.predict(vectorized_text)
    prediction_class = classes[int(prediction_integer.item(0))]
    
    return prediction_class