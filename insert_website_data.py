import pandas as pd
import pymysql
from sqlalchemy import create_engine
import get_ai_size

# Read CSV file into DataFrame
df = pd.read_csv('w0_w1.csv')
# df = pd.read_csv('web_body.csv')

# Establish database connection
db_connection = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    database='co_work'
)

# Insert data into MySQL database
engine = create_engine(
    'mysql+pymysql://root:password@localhost/co_work')
df.to_sql(name='ratio', con=engine, if_exists='append', index=False)

query = "SELECT * FROM user_body"
user_df = pd.read_sql(query, engine)
print(user_df)

query = "SELECT * FROM lative_size where product_id=201902191251"
size_df = pd.read_sql(query, engine)
print(size_df)

query = "SELECT * FROM ratio order by id desc limit 1"
ratio_df = pd.read_sql(query, engine)
print(ratio_df)


for i in range(217):
    data = {
        "user_id": user_df[i]["user_id"],
        "weight": user_df[i]["weight"],
        "height": user_df[i]["height"],
        "shape": user_df[i]["shape"],
        "product_id": 201902191251
    }
    output = get_ai_size.caculate_size(data)
    user_df[i]["size"] = output["ai_size"]

user_df

# Close connection
db_connection.close()
