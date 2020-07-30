import pandas as pd
from sklearn.model_selection import train_test_split

# ...
dataset = '/opt/ml/processing/input/dataset.csv'
output = '/opt/ml/processing/output'
seed = 998877

churn = pd.read_csv(dataset)

def do_some_mad_data_science(churn_df):
    # removing highly correlated features
    churn_df = churn.drop(['Day Charge', 'Eve Charge', 'Night Charge', 'Intl Charge'], axis=1)
    # one-hot encoding categorical values
    model_data = pd.get_dummies(churn)
    return model_data

def preprocess_train(churn_df):
    model_data = do_some_mad_data_science(churn_df)
    # fixing the target variable and moving to the first column
    model_data = pd.concat([model_data['Churn?_True.'], model_data.drop(['Churn?_False.', 'Churn?_True.'], axis=1)], axis=1)
    # splitting the dataset to train, test and validate
    train, test = train_test_split(model_data, test_size=0.15, seed=seed)
    train, validation = train_test_split(train, test_size=0.15, seed=seed)
    return train, test, validation

def preprocess_serve(churn_df):
    return do_some_mad_data_science(churn_df)

def write_data(folder, df):
    os.makedirs('{}/{}'.format(output, folder))
    df.to_csv('{}/{}/{}.csv'.format(output, folder, folder))

if __name__ == '__main__':
    churn_df = pd.read_csv(dataset)
    train, test, validate = preprocess_train(churn_df)
    try:
        # saving data locally
        write_data('train', train)
        write_data('test', test)
        write_data('validation', validation)
    except:
        print('Something bad happened during writing down the output')
    print('Finishing preprocessing for training job')
