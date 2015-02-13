import rupes
import twitter
import time
import logging

def main():
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

    logging.info("Starting script with since_id=%s" % str(since_id))

    returncount = 200
    statuses = api.GetUserTimeline(screen_name='rupertmurdoch', count=returncount, 
                          since_id=since_id, trim_user=True, exclude_replies=True)

    if len(statuses) == 0:
        # logging.debug("No new statuses")
        return

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

if __name__=='__main__':
    main()
