import rupes
import twitter
import time
import logging

# Start logging
logging.basicConfig(filename="/homec/organis2/rupes_murdoch/rupes.log", level='DEBUG')

# Connect to API
consumer_key = 'F1aosrucfBbYnJwZLfUrQLxh9'
consumer_secret = open("/homec/organis2/rupes_murdoch/private/consumer-secret.txt").read().strip()
access_key = '3008197577-8GDVTaizZa1k3vP9KfXSybO7FZfyOmUR8TTn0Re'
access_secret = open("/homec/organis2/rupes_murdoch/private/access-token-secret.txt").read().strip()
api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, 
                  access_token_key=access_key, access_token_secret=access_secret)
                  
# Get since_id
since_ref = open("/homec/organis2/rupes_murdoch/since_ref.txt", "r")
since_id = since_ref.read().strip()
since_id = long(since_id) if since_id != 'None' else None
since_ref.close()

# Get paging id. only relevant when tweeting old tweets
paging_ref = open("/homec/organis2/rupes_murdoch/paging_ref.txt", "r")
paging_id = paging_ref.read().strip()
paging_ref.close()
if paging_id == since_id or paging_id == 'None':
    paging_id = None
else: paging_id == long(paging_id)
    
logging.info("Starting script with since_id=%s and paging_id=%s" % 
    (str(since_id), str(paging_id)))

# Iterate through all the pages of tweets (going back in time)
# Until you find either the end, or the since_id
# THIS IS ONLY NECESSARY WHEN THE SCRIPT IS NEW, and tweeting tweets
# beyond the most recent

i = 0
statuses = None
returncount = 200

while True:
    if paging_id == since_id:
        paging_id = None
        logging.debug("resetting paging_id because it is the same as the since_id")
        continue
    statuses = api.GetUserTimeline(screen_name='rupertmurdoch', count=returncount, 
                          max_id=paging_id, since_id=since_id, 
                                   trim_user=True, exclude_replies=True)
   
    # This will cause inefficiencies when the bot is up to date
    if len(statuses) == 0:
        paging_id = None
        logging.debug("resetting paging_id because no results found")
        continue

    # This means we don't need to page further
    if len(statuses) < returncount:
        logging.debug("At the end")
        break
            
    time.sleep(2)
    # Protect against a never ending loop
    i += 1
    logging.debug("Page", i)
    paging_id = statuses[-1].id
    if i >= 10:
        logging.error("Unexpectedly long loop")
        break

# Save paging_id for future reference
paging_ref = open("/homec/organis2/rupes_murdoch/paging_ref.txt", "w")
paging_ref.write(str(paging_id))
paging_ref.close()
        
logging.debug("paged this time: %i " % i)
logging.debug("Length of statuses obj: %i" % len(statuses))

# Create a Deruped tweet
deruped = None
tid = None
tweet = None

# Iterate backwards until a valid tweet appears
for s in reversed(statuses):
    tweet = s.text
    tid = s.id
    deruped = rupes.derupe(tweet)
    if deruped:
        break

# Post tweet
if deruped:
    api.PostUpdate(status=deruped, in_reply_to_status_id = tid)
    logging.info("Posted \"%s\" from tweet \"%s\"" % (deruped, tweet))
else:
    logging.info("Skipping Tweet \"%s\"" % (tweet))

# Save ID of last tweet dealt with
since_ref = open("/homec/organis2/rupes_murdoch/since_ref.txt", "w")
since_ref.write(str(tid))
since_ref.close()
