# Overview
This proof of concept is a microservice built for AWS. It is intended to serve sponsored content and automatically sunset/sunrise media asset when a specified play count is reached. 

The individual implementing this service should be familiar with the following technologies outlined under the requirements section.

### Requirements
- JWPlayer account
- Python **3.6**
- Javascript
- Amazon Web Sevices
    - Lambda
    - API Gateway
    - RDS (Postgres)
    - SQL

### Installation
##### JWPlayer Dashboard
Each sponsored video should contain the following custom fields. 
- aggregate_plays = 0
    - This will be a running count of total plays and self increment
- daily_plays = *Number of total plays per day*
    - example: *daily_plays:5000*
- sponsored = **true**
    - This flags the video as sponsored and that tracking should occur. 

Then add sponsored video to a manual playlist and include it as **promoted content** in a recommendation playlist. 

##### AWS
- Setup a RDS Postgres Database
    - Create Table
    ```SQL
    CREATE TABLE medias(
        id SERIAL PRIMARY KEY,
        media_id VARCHAR(8) NOT NULL UNIQUE,
        media_count INTEGER NOT NULL
    )
    ```
    - Add Stored Procedure **create_media**
    ```SQL
    CREATE OR REPLACE PROCEDURE create_media(
        media_id character(8),
        receiver int, 
        amount dec
    )
    LANGUAGE plpgsql    
    AS $$
    BEGIN
        INSERT INTO medias(media_id, media_count)
        VALUES(_id, 1);

        SELECT media_count FROM medias
        WHERE media_id = _id
        INTO _total;
        
    END;$$
    ```
    - Add Stored Procedure **play_count**
    ```SQL
    CREATE OR REPLACE PROCEDURE play_count(
        _id character(8),
        inout _total int DEFAULT NULL
    )
    LANGUAGE plpgsql    
    AS $$
    BEGIN
        UPDATE medias
        SET media_count = media_count + 1
        WHERE media_id = _id;

        SELECT media_count FROM medias
        WHERE media_id = _id
        INTO _total;

    END;$$
    ```
- Lambda
    - Create a Lambda function
    - ZIP this project repo and install into the new function as zip. 
    - Make sure the function is configured to call lambda.handler
- API Gateway
    - REST API
    - Create Resource
        - Select Configure as proxy resource
        - Enter Resource Name
        - Enter Resource Path
        - Enable API Gateway CORS
    - Select Lambda function created above
    - Deploy

##### Frontend

Configuring the web player.
1. Host the branding.js plugin on your websever.
2. Configure the **plugins** node within the player setup. 
3. Pass in the **endpoint** URL from the API Gateway configuration above. 

This will tell the web player to load the branding.js plugin and deliver events to your endpoint. 
```HTML
<div id="player"></div>
<script src="https://cdn.jwplayer.com/libraries/dVoq0QmS.js"></script>
<script>
    jwplayer("player").setup({
        "playlist": "https://cdn.jwplayer.com/v2/playlists/GYVXiNeU?related_media_id=ZG6eWbJg",
        "plugins": {
            "https://MY_WEB_SERVER/branding.js": {
                "endpoint": "https://us-west-2.amazonaws.com/MY_CUSTOM/ENDPOINT"
            }
        }
    })
</script>
```

### Usage
With the AWS services live and the web player configured to use the plugin, each time a play session occurs the plugin will look for the **sponsored** custom parameter and call the endpoint when sent to **true**. 

### Known Limitations
For demonstration purposes, security precautions were not taken into consideration.  

In a production implementation, it's highly advised to subnet the Postgres DB and Lambda function in a Virtual Private Cloud.  Ensure your DB has no public access to it. 

Lock down your API Gateway to pass in an Authorization header and/or update CORS headers to only accept traffic from known domains. 

**NOTE**
Not included is the creation of a cronjob to reset the media_count value for each media id back to **0** and remove the sunset dates for each sponsored media in the JWPlayer dashboard.  This is required to replay sponsored content for the duration of the compaign.