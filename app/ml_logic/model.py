from sklearn.neighbors import KNeighborsClassifier


def initialize_model():
    """
    Initialize model.
    """
    model = KNeighborsClassifier()
    return model


def train_model(model, X_train, y_train):
    """
    Train model.
    """
    model.fit(X_train, y_train)
    print("Model trained.")
    return model
