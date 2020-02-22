import csv
import sys
import random
number = 1
csv_file = csv.reader(open('reviews.csv', "r"), delimiter=",")
print("Debug")
x=[]
for row in csv_file:
    x.append(row)

def get_user_reviews(x):
    reviews = []
    for i in x:
        if i[2] == str(number):
            reviews.append(i)
    return reviews

def date_check(reviews):
    biggestdate = "01/01/0001"
    reviewToUse = []
    print(biggestdate)
    print()
    print()
    print()
    print(reviews)
    for i in reviews:
        print("Date Check")
        print(i)
        print("Test")
        
        if i[3]>=biggestdate:
            print(biggestdate)
            print(i[3])
            print()
            print()
            biggestdate = i[3]
            reviewToUse.append(i)
    return reviewToUse

def review_check(reviewToUse):
    print(reviewToUse)
    stars = reviewToUse[0][3]
    print(stars)
    return stars
def music_check(reviewToUse):
    music = reviewToUse[0][1]
    print(music + "Hello")
    return music
def other_reviews(number, stars, music, x):
    otherReviews = []
    choices = []
    for i in x:
        print(i)
        print(str(stars))
        print(str(number))
        if i[1] == str(music) and i[3] == str(stars) and i[2]!= str(number):
            otherReviews.append(i)
            choices.append(i[0])
            print("Hello")
    return otherReviews, choices

def suggest(number, x):
    reviews = get_user_reviews(x)
    reviewToUse = date_check(reviews)
    stars = review_check(reviewToUse)
    music = music_check(reviewToUse)
    otherReviews, choices = other_reviews(number ,stars, music, x)
    print(otherReviews)
    FinalChoices = []
    if len(choices) > 0 and len(choices) <= 5:
        for i in choices:
            FinalChoices.append(i)
    elif len(choices) > 5:
        for i in range(0,5):
            choice = random.choice(choices)
            choices.remove(choice)
            FinalChoices.append(choice)
    for i in otherReviews:
        for j in FinalChoices:
            if i[0] == j:
                print(i)

suggest(number, x)



