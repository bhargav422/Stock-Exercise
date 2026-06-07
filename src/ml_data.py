from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from src import predict_price

def ml_data(ticker):
    features = ['Return_1D', 'SMA_5', 'SMA_10', 'Volume_Change']
    df = predict_price.get_stock_data(ticker)
    X = df[features]
    y = df['Target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

#Train_model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

# Predict
    y_pred = model.predict(X_test)
    return y_test,y_pred

if __name__ == "__main__":
    ticker = input("Enter stock name: ")
    y_test, y_pred = ml_data(ticker)

    # Evaluate
    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
    print(classification_report(y_test, y_pred))
