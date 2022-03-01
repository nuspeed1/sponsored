import json
import psycopg2
import datetime
import requests

"""
Receives a list of querystring parameters, increments a counter for the given mediaid. 
When counter matches or exceeds daily_plays, sunset media from JW dashboard.  This removes
it from the playlist. 

A nightly cron job resets the counter in the db and removes the sunset date.  Restarting
the branded content process the next day.

VPC internet access:
https://aws.amazon.com/premiumsupport/knowledge-center/internet-access-lambda-function/
Lambda <> RDS access:
https://docs.aws.amazon.com/lambda/latest/dg/services-rds-tutorial.html
Postgres libraries:
https://medium.com/@ianbinder/postgresql-with-aws-lambda-using-python-db93b2703bf8
"""
SITE_ID = "REPLACE WITH JWPLAYER SITE ID.  USE KMS!!"
SECRET = "REPLACE WITH JWPLAYER V2 API SECRET.   USE KMS!!"
HEADERS = {"Accept": "application/json", "Authorization": SECRET}
try:
    conn = psycopg2.connect(
        host="REPLACE_WITH_HOST_URL.rds.amazonaws.com",
        port='5432',
        user='postgres',
        dbname='postgres',
        password='REPLACE_WITH_DB_PASSWORD. USE KMS!!')

except Exception as e:
    print('got error')
    print(e)

cur = conn.cursor()

def create_media(mid):
    cur.execute(f"CALL create_media ('{mid}')")
    conn.commit()

def play_count(mid):
    cur.execute(f"CALL play_count ('{mid}')")
    conn.commit()
    return cur.fetchone()

def get_jwmedia(mid):
    try:
        print(f"Sunsetting.getting {mid}")
        url = f"https://api.jwplayer.com/v2/sites/{SITE_ID}/media/{mid}/"
        res = requests.get(url, headers=HEADERS)
        return res.json()
    except Exception as e:
        print(e)

def sunset_jwmedia(mid, count):
    print(f"Sunsetting {mid}")

    data = get_jwmedia(mid)

    meta = data['metadata']

    if meta['publish_end_date']:  # content is already sunset
        print('Sunsetting.publish_end_date already set.  Skipping...')
        return

    cust_params = meta['custom_params']
    try:
        agg_plays = 0
        if 'aggregate_plays' in cust_params:
            agg_plays = int(cust_params['aggregate_plays'])

        cust_params['aggregate_plays'] = str(agg_plays + count)

        url = f"https://api.jwplayer.com/v2/sites/{SITE_ID}/media/{mid}/"
        
        t = datetime.datetime.now()

        payload = {
            "metadata": {
                "publish_end_date": t.isoformat(),
                "custom_params": cust_params
            }
        }
        print(f"Sunsetting.updating {mid}")
        print(payload)
        res = requests.patch(url, json=payload, headers=HEADERS)
        print(res.json())
    except Exception as e:
        print(e)

def handler(event, context):
    qs = event['queryStringParameters']

    media_id = qs['mediaid']
    daily_plays = int(qs['daily_plays'])
    agg_plays = int(qs['aggregate_plays'])

    count = list(play_count(media_id))[0]

    if count == None:
        print('creating media')
        create_media(media_id)
        # create new media
    elif count >= daily_plays:
        sunset_jwmedia(media_id, count)
        #sunset content

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods':'OPTIONS,GET'
        }
    }

print('connected')

payload = {'queryStringParameters':{"mediaid":'DTg4AZ5P',"daily_plays":5,"aggregate_plays":200,}}
handler(payload, {})

cur.close()
conn.close()
