(function(jwplayer){
      // The initialization function, called on player setup.
    const registerPlugin = window.jwplayerPluginJsonp || window.jwplayer().registerPlugin;
    registerPlugin('branding', '8.0', function(player, config, div) {
        console.log(config)
        console.log(div)
        console.log(player)

        const ENDPOINT = config.endpoint

        var callAPI = async function(url, type){
            let init = {"headers": {"Content-Type": 'application/json'}}
    
            
            return await fetch(url, {headers: {"Content-Type": 'application/json'}})
                    .then(res => {
                        if (!res.ok){
                            throw new Error(`Unable to fetch ${url}: ${res.statusText}`)
                        }
                        return res
                    })
        }
    
        var processEvent = function(event,asset){
            let dp = asset.daily_plays || "";
            let ap = asset.aggregate_plays || "";
    
            let id = asset.mediaid;
    
            let url = `${ENDPOINT}?daily_plays=${dp}&aggregate_plays=${ap}&mediaid=${id}&event=${event}`
            callAPI(url, asset)
        }
    
        var onStart = function(event){
            processEvent(event['type'], this)
        }
    
        var onTime = function(data){
            let dur = data['duration']
            let time = data['currentTime']
    
            console.log(`completion: ${time/dur}`)
    
            // processEvent(event['type'], this)
        }
    
        var onExit = function(event){
            player.off("time", onTime)
            processEvent(event['type'], this)
        }
    
    
        player.on("playlistItem", function(playlist, data){
            if(playlist.item.hasOwnProperty("sponsored")){

                player.once('firstFrame', onStart.bind(playlist.item))
                // jwplayer().once('complete', onExit.bind(playlist.item))
                // jwplayer().on('time', onTime.bind(playlist.item))

            }
        })
    })
})(jwplayer)