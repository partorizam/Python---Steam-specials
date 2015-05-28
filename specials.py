__author__ = 'Marc Khristian Partoriza'
__date__   = '15/04/2015'
__class__  = 'ICS313'

######Program Description######
#This program creates a mash-up page using the discounted information#
#of games on Steam's Specials page, and reviews from GameSpot's page #
###############################

import requests
import urllib2
import re
import string

######Regex Expressions######
#GamesListPattern (pattern)
gamesListPattern = '<span class="title">.+<\/span>'
#DiscountsPatern (pattern2)
discountsPattern = '<span>-\d+%<\/span>'
#SteamGameURL (pattern3)
steamGameURLs = 'http:\/\/store.steampowered.com\/app\/\d+\/\?snr=1_7_7_204_150_1'
#ReviewsPattern (pattern4)
reviewsPattern = '\/reviews\/.+/"'
#RatingScorePattern 1 & 2 (pattern 5 & 6)
ratingScorePattern1 = '<span itemprop="ratingValue">\d\.?\d?'
ratingScorePattern2 = '<div class="gs-score__cell">\s*\d\.?\d?'
#############################



#Get html from Steam's Specials web page
html = urllib2.urlopen('http://store.steampowered.com/search/?specials=1').read()

#Using gamesListPattern, find all the game names and put them in list 'uglyGameList'
#uglyGameList obtains html elements and unnecessary special characters in the values
uglyGameList = re.findall(gamesListPattern, html)

gameList = []
#For every game in uglyGameList, add the proper game name to gameList
for game in uglyGameList:
    #Removes html elements and special characters
    actualGameName = game[20:-7]
    gameList.append((filter(lambda x: x in string.printable, actualGameName)).replace(" ", "+"))

#Using discountsPattern, find all the discounts and put them in list 'uglyDiscounts'
#uglyDiscounts obtains html elements in the values
uglyDiscounts = re.findall(discountsPattern, html)

discounts = []
#For every discount in the uglyDiscounts, add the proper discount to 'discounts'
for discount in uglyDiscounts:
    actualDiscount = discount[7:-8]
    discounts.append(int(actualDiscount))

#Using steamGameURLs, find all Steam game URLs and add them to list 'urls'
urls = re.findall(steamGameURLs, html)

#For every game in gameList, get their review score on GameSpot.com
scores = []
gameReviews = []
for game in gameList:
    #Get the URL for searching the review on GameSpot and read it
    searchUrl = "http://GameSpot.com/search/?q=" + game + "%5B%5D=review"
    html2 = urllib2.urlopen(searchUrl).read()

    #Get the URL for the actual review pages on game, if any.
    #reviews[0] is the first link, which is most likely the 'game' review page.
    reviews = re.findall(reviewsPattern, html2)

    #Compare game name and review name to make sure we aren't getting a review for another game.
    if len(reviews) > 0:
        comparingGameName = re.sub('\W', '', game).lower()
        comparingReviewName = re.sub('\W', '', reviews[0]).lower()

    if(comparingGameName in comparingReviewName):
        #If there are review pages, check if they are of the 'game' we want
        if len(reviews) > 0 :
            #Open and read the review html page
            tempUrl = "http://Gamespot.com" + reviews[0]
            response3 = urllib2.urlopen(tempUrl[:-1])
            html3 = response3.read()

            #The score is in either ratingScorePattern1scores or ratingScorePattern2scores depending on the HTML page.
            #First check ratingScorePattern1, if there are no results, check ratingScorePattern2.
            #Add the score to the list 'score' when the score is found.
            ratingScorePattern1scores = re.findall(ratingScorePattern1, html3)
            if len(ratingScorePattern1scores) < 1:
                #Removes html elements
                score = re.findall(ratingScorePattern2, html3)[0]
                score = score[28:]
                score = score.replace(" ","")
                scores.append(score)
                gameReviews.append(tempUrl)
            else:
                #Removes html elements
                score = ratingScorePattern1scores[0]
                score = score[29:]
                scores.append(score)
                gameReviews.append(tempUrl)

        #If there are no review pages, append "no reviews" to 'scores'
        else:
            scores.append("")
            gameReviews.append("http://www.gamespot.com")
    else:
        scores.append("")
        gameReviews.append("http://www.gamespot.com")

#Zips the three lists together, and sorts the three according to discounts (ascending)
zipped = zip(scores, gameList, discounts, gameReviews, urls)
zipped.sort(reverse = True)
scores, gameList, discounts, gameReviews, urls = zip(*zipped)

#The first part of the mash up web page
mashUpWebPage = """<!DOCTYPE html>
<html lang="en">
        <style></style>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>Steam Special Sale Games with GameSpot Review Scores</title>
    </head>
    <body>
        <h1>Steam Special Sale Games with GameSpot Review Scores</h1>
    <table>
        <tbody>
            <tr>
                <th>Game</th>
                <th>Discount</th>
                <th>GameSpot Score</th>
            </tr>"""

#Adding the rows to the mash up web page
for index, game in enumerate(gameList):
    if(discounts[index] >= 50):
        mashUpWebPage += """
                    <tr>
                        <th>
                            <a href="%s">%s</a>
                        </th>
                        <th>
                            -%s%%
                        </th>
                        <th>
                            <a href = "%s">%s</a>
                        </th>
                    </tr>""" % (urls[index], game.replace("+"," "), discounts[index], gameReviews[index], scores[index])

#The ending part of the mash up web page
mashUpWebPage += """
        </tbody>
    </table>
</body>
</html>"""

#Write the mashUpWebPage string to an html file
f = open('rankings.html','w')
f.write(mashUpWebPage)
f.close()











