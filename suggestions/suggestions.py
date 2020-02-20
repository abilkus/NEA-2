import pandas as pd 
import warnings
warnings.simplefilter("ignore")  
# Get the data 
column_names = ['user_id', 'item_id', 'rating', 'timestamp'] 
  
path = 'https://media.geeksforgeeks.org/wp-content/uploads/file.tsv'
  
df = pd.read_csv(path, sep='\t', names=column_names) 
  
# Check the head of the data 
print(df.head())
print()
# Check out all the movies and their respective IDs 
movie_titles = pd.read_csv('https://media.geeksforgeeks.org/wp-content/uploads/Movie_Id_Titles.csv') 
movie_titles.head() 
df = pd.merge(df, movie_titles, on='item_id') 
print(df.head())
print() 
print(df.describe())
ratings = pd.DataFrame(df.groupby('title')['rating'].mean())
print(ratings.head())
print()
ratings = ratings.sort_values('rating', ascending = False)
print(ratings.head())
print()


test1 = df[df["user_id"] == 0]
test3 = test1[test1["rating"] == 5]

test4 = test3["title"][0][:100]

print(test4 + "\n")
#print(test5 + "\n")
print(test3)
#print(test5)

movie_matrix = df.pivot_table(index='user_id', columns='title', values='rating')
movie_matrix.head()
test4_user_rating = movie_matrix[test4]
similar_to_test4=movie_matrix.corrwith(test4_user_rating)
print(similar_to_test4.head())
print()

corr_test4 = pd.DataFrame(similar_to_test4, columns=['correlation'])
corr_test4.dropna(inplace=True)
print(corr_test4.head())
print()
print("Hello")
for i in corr_test4:
    for j in corr_test4:
        print(corr_test4[i][j])
    print("Test")
