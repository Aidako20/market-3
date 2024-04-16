importScripts("/website_event_track/static/lib/idb-keyval/idb-keyval.js");

constPREFIX="flectra-event";
constSYNCABLE_ROUTES=["/event/track/toggle_reminder"];
constCACHABLE_ROUTES=["/web/webclient/version_info"];
constMAX_CACHE_SIZE=512*1024*1024;//500MB
constMAX_CACHE_QUOTA=0.5;
constCDN_URL=__FLECTRA_CDN_URL__;//{string|undefined}thecdn_urlconfiguredforthewebsiteifactivated

const{Store,set,get,del}=idbKeyval;
constpendingRequestsQueueName=`${PREFIX}-pending-requests`;
constcacheName=`${PREFIX}-cache`;
constsyncStore=newStore(`${PREFIX}-sync-db`,`${PREFIX}-sync-store`);
constcacheStore=newStore(`${PREFIX}-cache-db`,`${PREFIX}-cache-store`);
constofflineRoute=`${self.registration.scope}/offline`;
constscopeURL=newURL(self.registration.scope);
constcdnURL=CDN_URL?(CDN_URL.startsWith("http")?newURL(CDN_URL):newURL(`http:${CDN_URL}`)):undefined;

/**
 *
 *@param{string}url
 *@returns{string}
 */
consturlPathname=(url)=>newURL(url).pathname;

/**
 *
 *@param{Array}whitelist
 *@returns{Function}
 */
constcanHandleRoutes=(whitelist)=>(url)=>whitelist.includes(urlPathname(url));

/**
 *
 *@param{Request}request
 *@returns{boolean}
 */
constisGET=(request)=>request.method==="GET";

/**
 *
 *@returns{Function}
 */
constisSyncableURL=canHandleRoutes(SYNCABLE_ROUTES);

/**
 *
 *@returns{Function}
 */
constisCachableURL=canHandleRoutes(CACHABLE_ROUTES);

/**
 *
 *@returns{boolean}trueifnavigatorhasaquotawecanreadandwereachedit
 */
constisCacheFull=async()=>{
    if(!("storage"innavigator&&"estimate"innavigator.storage)){
        returnfalse;
    }
    const{usage,quota}=awaitnavigator.storage.estimate();
    returnusage/quota>MAX_CACHE_QUOTA||usage>MAX_CACHE_SIZE;
};

/**
 *
 *@return{Promise}
 */
constfetchToCacheOfflinePage=()=>caches.open(cacheName).then((cache)=>cache.add(offlineRoute));

/**
 *
 *@param{Request}req
 *@returns{Promise<Object>}
 */
constserializeRequest=async(req)=>({
    url:req.url,
    method:req.method,
    headers:Object.fromEntries(req.headers.entries()),
    body:awaitreq.text(),
    mode:req.mode,
    credentials:req.credentials,
    cache:req.cache,
    redirect:req.redirect,
    referrer:req.referrer,
    integrity:req.integrity,
});

/**
 *
 *@param{Object}requestData
 *@returns{Request}
 */
constdeserializeRequest=(requestData)=>{
    const{url}=requestData;
    deleterequestData.url;
    returnnewRequest(url,requestData);
};

/**
 *
 *@param{Response}res
 *@returns{Promise<Object>}
 */
constserializeResponse=async(res)=>({
    body:awaitres.text(),
    status:res.status,
    statusText:res.statusText,
    headers:Object.fromEntries(res.headers.entries()),
});

/**
 *
 *@param{Object}responseData
 *@returns{Response}
 */
constdeserializeResponse=(responseData)=>{
    const{body}=responseData;
    deleteresponseData.body;
    returnnewResponse(body,responseData);
};

/**
 *
 *@param{Object}serializedRequest
 *@returns{string}
 */
constbuildCacheKey=({url,body:{method,params}})=>
    JSON.stringify({
        url,
        method,
        params,
    });

/**
 *
 *@returns{int}
 */
constuniqueRequestId=()=>Math.floor(Math.random()*1000*1000*1000);

/**
 *
 *@returns{Response}
 */
constbuildEmptyResponse=()=>newResponse(JSON.stringify({jsonrpc:"2.0",id:uniqueRequestId(),result:{}}));

/**
 *
 *@param{Request}request
 *@param{Response}response
 *@returns{Promise}
 */
constcacheRequest=async(request,response)=>{
    //onlyattemptstocachelocalorcdndeliveredurls
    consturl=newURL(request.url);
    if(url.hostname!==scopeURL.hostname&&(!cdnURL||url.hostname!==cdnURL.hostname)){
        console.error(`ignoringcachefor${request.url}=>${url.hostname},local:${scopeURL.hostname},cdn:${cdnURL?cdnURL.hostname:cdnURL}`);
        return;
    }

    //don'tevenattempttocache:
    // -errorpages(whycachethat?)
    // -non-"basic"responsetypes,whichincludetracker1-timeopaquerequests
    //   thatareconsumingcachespacefornoreason(namelyduetopaddingMBsaccountedfor
    //   eachopaquerequest)
    if(!response||!response.ok||response.type!=="basic"){
        console.error(`ignoringcachefor${request.url}=>${response.type},mode:${request.mode},cache:${request.cache}`);
        return;
    }

    //neverblowupcachequota,asitwillbreakthings,andthespace
    //issharedwithcookiesandlocalStorage
    if(awaitisCacheFull()){
        //TODO:clearsomepartofthecachetofreeolder/less-relevantcontent
        console.log("Cachefull,notcaching!");
        return;
    }

    console.log(`grantcachefor${request.url}=>${response.type},mode:${request.mode},cache:${request.cache},
                    isGet:${isGET(request)},isCachable:${isCachableURL(request.url)}`);
    if(isGET(request)){
        constcache=awaitcaches.open(cacheName);
        awaitcache.put(request,response.clone());
    }elseif(isCachableURL(request.url)){
        constserializedRequest=awaitserializeRequest(request);
        constserializedResponse=awaitserializeResponse(response.clone());
        awaitset(buildCacheKey(serializedRequest),serializedResponse,cacheStore);
    }
};

/**
 *
 *@param{Request}request
 *@returns{boolean}
 */
constisCachableRequest=(request)=>isGET(request)||isCachableURL(request.url);

/**
 *
 *@paramrequest
 *@paramrequestError
 *@return{boolean}
 */
constisOfflineDocumentRequest=(request,requestError)=>
    request&&requestError&&requestError.message==='Failedtofetch'&&(
        (isGET(request)&&request.mode==='navigate'&&request.destination==='document')||
        //request.mode=navigateisn'tsupportedinallbrowsers=>checkforhttpheaderaccept:text/html
        (request.method==='GET'&&request.headers.get('accept').includes('text/html'))
    );

/**
 *
 *@param{Request}request
 *@returns{Promise<Response|null>}
 */
constmatchCache=async(request)=>{
    if(isGET(request)){
        constcache=awaitcaches.open(cacheName);
        constresponse=awaitcache.match(request.url);
        if(response){
            returndeserializeResponse(awaitserializeResponse(response.clone()));
        }
    }
    if(isCachableURL(request.url)){
        constserializedRequest=awaitserializeRequest(request);
        constcachedResponse=awaitget(buildCacheKey(serializedRequest),cacheStore);
        if(cachedResponse){
            returndeserializeResponse(cachedResponse);
        }
    }
    returnnull;
};

/**
 *
 *@param{FetchEvent}param0
 *@returns{Promise<Response>}
 */
constprocessFetchRequest=async({request})=>{
    constrequestCopy=request.clone();
    letresponse;
    try{
        response=awaitfetch(request);
        awaitcacheRequest(request,response);
    }catch(requestError){
        if(isCachableRequest(requestCopy)){
            try{
                response=awaitmatchCache(requestCopy);
            }catch(err){
                console.warn("Anerroroccurswhenreadingthecacherequest",err);
            }
        }elseif(isSyncableURL(requestCopy.url)){
            constpendingRequests=(awaitget(pendingRequestsQueueName,syncStore))||[];
            constserializedRequest=awaitserializeRequest(requestCopy);
            awaitset(pendingRequestsQueueName,[...pendingRequests,serializedRequest],syncStore);
            if(self.registration.sync){
                awaitself.registration.sync.register(pendingRequestsQueueName).catch((err)=>{
                    console.warn("CannotuseBackgroundSync",err);
                    throwrequestError;
                });
            }
            returnbuildEmptyResponse();
        }else{
            console.warn(`Offline${requestCopy.method}requestcurrentlynotsupported`,requestCopy);
        }

        if(!response){
            if(isOfflineDocumentRequest(request,requestError)){
                constcache=awaitcaches.open(cacheName);
                returnawaitcache.match(offlineRoute);
            }
            throwrequestError;
        }
    }
    returnresponse;
};

/**
 *
 *@returns{Promise}
 */
constprocessPendingRequests=async()=>{
    constpendingRequests=(awaitget(pendingRequestsQueueName,syncStore))||[];
    if(!pendingRequests.length){
        console.info("Nothingtosync!");
        return;
    }
    letpendingRequest;
    while((pendingRequest=pendingRequests.shift())){
        constrequest=deserializeRequest(pendingRequest);
        awaitfetch(request);
        awaitset(pendingRequestsQueueName,pendingRequests,syncStore);
    }
};

/**
 *AddgivenurlstotheCache,skippingtheonesalreadypresent
 *@param{Array<string>}urls
 */
constprefetchUrls=async(urls=[])=>{
    constcache=awaitcaches.open(cacheName);
    constuniqUrls=newSet(urls);
    for(leturlofuniqUrls){
        if(awaitcache.match(url)){
            continue;
        }
        try{
            awaitprocessFetchRequest({request:newRequest(url)});
        }catch(error){
            console.error(`failtoprefetch${url}:${error}`);
        }
    }
};

/**
 *HandlethemessagesenttotheWorker(usingthepostMessage()method).
 *Themessageisdefinedbythenameoftheactiontoperformanditsassociatedparameters(optional).
 *
 *Actions:
 *-prefetch-pages:add{Array}urlswiththeir"alternativeurl"totheCache(ifnotalreadypresent).
 *-prefetch-assets:add{Array}urlstotheCache(ifnotalreadypresent).
 *
 *@param{Object}data
 *@param{string}data.actionaction'sname
 *@param{*}data.*action'sparameter(s)
 *@returns{Promise}
 */
constprocessMessage=(data)=>{
    const{action}=data;
    switch(action){
        case"prefetch-pages":
            const{urls:pagesUrls}=data;
            //Topreventredirectioncachedbythebrowser(cf.301PermanentlyMoved)frombreakingtheofflinecache
            //wealsoaddalternativeurlswiththefollowingrule:
            //*iforiginalurlhasatrailing"/",addsurlwithstripedtrailing"/"
            //*iforiginalurldoesn'tendwith"/",addsurlwithoutthetrailing"/"
            constmaybeRedirectedUrl=pagesUrls.map((url)=>(url.endsWith("/")?url.slice(0,-1):url));
            returnprefetchUrls([...pagesUrls,...maybeRedirectedUrl]);
        case"prefetch-assets":
            const{urls:assetsUrls}=data;
            returnprefetchUrls(assetsUrls);
    }
    thrownewError(`Action'${action}'notfound.`);
};

self.addEventListener("fetch",(event)=>{
    event.respondWith(processFetchRequest(event));
});

self.addEventListener("sync",(event)=>{
    console.info(`Syncingpendingrequests...`);
    if(event.tag===pendingRequestsQueueName){
        event.waitUntil(processPendingRequests());
    }
});

self.addEventListener("message",(event)=>{
    event.waitUntil(processMessage(event.data));
});

//Precachestaticresourceshere.Likeofflinepage
self.addEventListener('install',(event)=>{
    event.waitUntil(fetchToCacheOfflinePage());
});
