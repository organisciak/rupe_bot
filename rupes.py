import nltk
import re

def score_by_length(rated_parts):
    ''' Take a list of (phrase_part, score) tuples and score them by minimum length '''
    if len(rated_parts) < 2:
        return rated_parts
    scores = sorted([len(item[0]) for item in rated_parts])
    b = []
    for t in rated_parts:
        l = len(t[0])
        score = t[1]
        if l == scores[0]:
            score += 2
        elif l == scores[1]:
            score += 1   
        b += [(t[0], score)]
    return b

def rupe_score(phrase):
    ''' 
    Rupe scoring: Score phrases from a tweet, sometimes truncating the phrase further.
    '''
    score = 0
    # If it starts with "But" then dock points
    if re.match("^[,\s]?[Bb]ut\s", phrase):
        score -= 4
        
    # Remove Blocklist
    if phrase in ['i.e.', 'ie.', 'e.g.', 'eg.', 'More', 'More.']:
        return (phrase, -100)

    # If it includes "but" in the middle, just strip it out and add points
    if re.match(".+[,\s]but\s", phrase):
        phrase = re.split("\sbut\s", phrase)[0]
        score += 1
    return (phrase, score)

def best_part(rated_parts):
    # Fold rated tweet parts into a single suggestion
    # if parts of tweet have the same score, the earlier one takes precedence
    part = reduce(lambda x,y: y if y[1] > x[1] else x, rated_parts, (None, -100))
    n = len(part[0])
    if n < 90 and n > 5:
        return part[0]
    else:
        return None

def derupe(tweet):
    # Initialize tokenizer each time? Why not, no need to complicate a bot
    # that tweets once or twice a day
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    parts = tokenizer.tokenize(tweet)
    ratings = [rupe_score(part.strip()) for part in parts]
    length_ranked_ratings = score_by_length(ratings)
    deruped_tweet = best_part(length_ranked_ratings)
    # Abort if the new tweet is too much of the old one
    if deruped_tweet and len(deruped_tweet) > (len(tweet)-5) and len(tweet) > 10:
        return None
    return deruped_tweet
        
def main():                    
    tweet_file = open('test-tweets.txt', 'r+')
    tweets = [t.rstrip() for t in tweet_file.readlines()]
    tweet_file.close()
            
    for tweet in tweets:
        deruped_tweet = derupe(tweet)
        if deruped_tweet:
            print "ORIGINAL:  %s" % tweet
            print "NEW TWEET: %s" % deruped_tweet
            print

if __name__ == '__main__':
    main()
