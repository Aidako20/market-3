flectra.define('bus.CrossTab',function(require){
"usestrict";

varLongpolling=require('bus.Longpolling');

varsession=require('web.session');

/**
 *CrossTab
 *
 *Thisisanextensionofthelongpollingbuswithbrowsercross-tabsynchronization.
 *ItusesaMaster/SlaveswithLeaderElectionarchitecture:
 *-asingletabhandleslongpolling.
 *-tabsaresynchronizedbymeansofthelocalstorage.
 *
 *localStorageusedkeysare:
 *-{LOCAL_STORAGE_PREFIX}.{sanitizedOrigin}.channels:sharedpublicchannellisttolistenduringthepoll
 *-{LOCAL_STORAGE_PREFIX}.{sanitizedOrigin}.options:sharedoptions
 *-{LOCAL_STORAGE_PREFIX}.{sanitizedOrigin}.notification:thereceivednotificationsfromthelastpoll
 *-{LOCAL_STORAGE_PREFIX}.{sanitizedOrigin}.tab_list:listofopenedtabids
 *-{LOCAL_STORAGE_PREFIX}.{sanitizedOrigin}.tab_master:generatedidofthemastertab
 *
 *trigger:
 *-window_focus:whenthewindowisfocused
 *-notification:whenanotificationisreceivefromthelongpolling
 *-become_master:whenthistabbecamethemaster
 *-no_longer_master:whenthistabisnotlongerthemaster(theuserswithtab)
 */
varCrossTabBus=Longpolling.extend({
    //constants
    TAB_HEARTBEAT_PERIOD:10000,//10seconds
    MASTER_TAB_HEARTBEAT_PERIOD:1500,//1.5seconds
    HEARTBEAT_OUT_OF_DATE_PERIOD:5000,//5seconds
    HEARTBEAT_KILL_OLD_PERIOD:15000,//15seconds
    LOCAL_STORAGE_PREFIX:'bus',

    //properties
    _isMasterTab:false,
    _isRegistered:false,

    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        varnow=newDate().getTime();
        //usedtoprefixlocalStoragekeys
        this._sanitizedOrigin=session.origin.replace(/:\/{0,2}/g,'_');
        //preventscollisionsbetweendifferenttabsandintests
        this._id=_.uniqueId(this.LOCAL_STORAGE_PREFIX)+':'+now;
        if(this._callLocalStorage('getItem','last_ts',0)+50000<now){
            this._callLocalStorage('removeItem','last');
        }
        this._lastNotificationID=this._callLocalStorage('getItem','last',0);
        this.call('local_storage','onStorage',this,this._onStorage);
    },
    destroy:function(){
        this._super();
        clearTimeout(this._heartbeatTimeout);
    },
    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------
    /**
     *Sharethebuschannelswiththeotherstabbythelocalstorage
     *
     *@override
     */
    addChannel:function(){
        this._super.apply(this,arguments);
        this._callLocalStorage('setItem','channels',this._channels);
    },
    /**
     *Sharethebuschannelswiththeotherstabbythelocalstorage
     *
     *@override
     */
    deleteChannel:function(){
        this._super.apply(this,arguments);
        this._callLocalStorage('setItem','channels',this._channels);
    },
    /**
     *@return{string}
     */
    getTabId:function(){
        returnthis._id;
    },
    /**
     *Tellswhetherthisbusisrelatedtothemastertab.
     *
     *@returns{boolean}
     */
    isMasterTab:function(){
        returnthis._isMasterTab;
    },
    /**
     *Usethelocalstoragetosharethelongpollingfromthemastertab.
     *
     *@override
     */
    startPolling:function(){
        if(this._isActive===null){
            this._heartbeat=this._heartbeat.bind(this);
        }
        if(!this._isRegistered){
            this._isRegistered=true;

            varpeers=this._callLocalStorage('getItem','peers',{});
            peers[this._id]=newDate().getTime();
            this._callLocalStorage('setItem','peers',peers);

            this._registerWindowUnload();

            if(!this._callLocalStorage('getItem','master')){
                this._startElection();
            }

            this._heartbeat();

            if(this._isMasterTab){
                this._callLocalStorage('setItem','channels',this._channels);
                this._callLocalStorage('setItem','options',this._options);
            }else{
                this._channels=this._callLocalStorage('getItem','channels',this._channels);
                this._options=this._callLocalStorage('getItem','options',this._options);
            }
            return; //startPollingwillbecalledagainontabregistration
        }

        if(this._isMasterTab){
            this._super.apply(this,arguments);
        }
    },
    /**
     *Sharetheoptionwiththelocalstorage
     *
     *@override
     */
    updateOption:function(){
        this._super.apply(this,arguments);
        this._callLocalStorage('setItem','options',this._options);
    },
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------
    /**
     *Calllocal_storageservice
     *
     *@private
     *@param{string}method(getItem,setItem,removeItem,on)
     *@param{string}key
     *@param{any}param
     *@returnsserviceinformation
     */
    _callLocalStorage:function(method,key,param){
        returnthis.call('local_storage',method,this._generateKey(key),param);
    },
    /**
     *GenerateslocalStoragekeysprefixedbybus.(LOCAL_STORAGE_PREFIX=thename
     *ofthisaddon),andthesanitizedorigin,topreventkeysfrom
     *conflictingwhenseveralbusinstances(pollingdifferentorigins)
     *co-exist.
     *
     *@private
     *@param{string}key
     *@returnskeyprefixedwiththeorigin
     */
    _generateKey:function(key){
        returnthis.LOCAL_STORAGE_PREFIX+'.'+this._sanitizedOrigin+'.'+key;
    },
    /**
     *@override
     *@returns{integer}numberofmillisecondssince1January197000:00:00
     */
    _getLastPresence:function(){
        returnthis._callLocalStorage('getItem','lastPresence')||this._super();
    },
    /**
     *Checkallthetime(accordingtotheconstants)ifthetabisthemastertaband
     *checkifitisactive.Usethelocalstorageforthischecks.
     *
     *@private
     *@see_startElectionmethod
     */
    _heartbeat:function(){
        varnow=newDate().getTime();
        varheartbeatValue=parseInt(this._callLocalStorage('getItem','heartbeat',0));
        varpeers=this._callLocalStorage('getItem','peers',{});

        if((heartbeatValue+this.HEARTBEAT_OUT_OF_DATE_PERIOD)<now){
            //Heartbeatisoutofdate.Electingnewmaster
            this._startElection();
            heartbeatValue=parseInt(this._callLocalStorage('getItem','heartbeat',0));
        }

        if(this._isMasterTab){
            //walkthroughallpeersandkillold
            varcleanedPeers={};
            for(varpeerNameinpeers){
                if(peers[peerName]+this.HEARTBEAT_KILL_OLD_PERIOD>now){
                    cleanedPeers[peerName]=peers[peerName];
                }
            }

            if(heartbeatValue!==this.lastHeartbeat){
                //someoneelseisalsomaster...
                //itshouldnothappen,exceptinsomeraceconditionsituation.
                this._isMasterTab=false;
                this.lastHeartbeat=0;
                peers[this._id]=now;
                this._callLocalStorage('setItem','peers',peers);
                this.stopPolling();
                this.trigger('no_longer_master');
            }else{
                this.lastHeartbeat=now;
                this._callLocalStorage('setItem','heartbeat',now);
                this._callLocalStorage('setItem','peers',cleanedPeers);
            }
        }else{
            //updateownheartbeat
            peers[this._id]=now;
            this._callLocalStorage('setItem','peers',peers);
        }

        //WritelastPresenceinlocalstorageifithasbeenupdatedsincelastheartbeat
        varhbPeriod=this._isMasterTab?this.MASTER_TAB_HEARTBEAT_PERIOD:this.TAB_HEARTBEAT_PERIOD;
        if(this._lastPresenceTime+hbPeriod>now){
            this._callLocalStorage('setItem','lastPresence',this._lastPresenceTime);
        }

        this._heartbeatTimeout=setTimeout(this._heartbeat.bind(this),hbPeriod);
    },
    /**
     *@private
     */
    _registerWindowUnload:function(){
        $(window).on('unload.'+this._id,this._onUnload.bind(this));
    },
    /**
     *Checkwiththelocalstorageifthecurrenttabisthemastertab.
     *Ifthistabbecamethemaster,trigger'become_master'event
     *
     *@private
     */
    _startElection:function(){
        if(this._isMasterTab){
            return;
        }
        //checkwho'snext
        varnow=newDate().getTime();
        varpeers=this._callLocalStorage('getItem','peers',{});
        varheartbeatKillOld=now-this.HEARTBEAT_KILL_OLD_PERIOD;
        varnewMaster;
        for(varpeerNameinpeers){
            //checkfordeadpeers
            if(peers[peerName]<heartbeatKillOld){
                continue;
            }
            newMaster=peerName;
            break;
        }

        if(newMaster===this._id){
            //we'renextinqueue.Electingasmaster
            this.lastHeartbeat=now;
            this._callLocalStorage('setItem','heartbeat',this.lastHeartbeat);
            this._callLocalStorage('setItem','master',true);
            this._isMasterTab=true;
            this.startPolling();
            this.trigger('become_master');

            //removingmasterpeerfromqueue
            deletepeers[newMaster];
            this._callLocalStorage('setItem','peers',peers);
        }
    },
    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------
    /**
     *@override
     */
    _onFocusChange:function(params){
        this._super.apply(this,arguments);
        this._callLocalStorage('setItem','focus',params.focus);
    },
    /**
     *Ifit'sthemastertab,thenotificationsaresbroadcastedtoothertabsbythe
     *localstorage.
     *
     *@override
     */
    _onPoll:function(notifications){
        varnotifs=this._super(notifications);
        if(this._isMasterTab&&notifs.length){
            this._callLocalStorage('setItem','last',this._lastNotificationID);
            this._callLocalStorage('setItem','last_ts',newDate().getTime());
            this._callLocalStorage('setItem','notification',notifs);
        }
    },
    /**
     *Handlerwhenthelocalstorageisupdated
     *
     *@private
     *@param{FlectraEvent}event
     *@param{string}event.key
     *@param{string}event.newValue
     */
    _onStorage:function(e){
        varvalue=JSON.parse(e.newValue);
        varkey=e.key;

        if(this._isRegistered&&key===this._generateKey('master')&&!value){
            //masterwasunloaded
            this._startElection();
        }

        //lastnotificationidchanged
        if(key===this._generateKey('last')){
            this._lastNotificationID=value||0;
        }
        //notificationschanged
        elseif(key===this._generateKey('notification')){
            if(!this._isMasterTab){
                this.trigger("notification",value);
            }
        }
        //updatechannels
        elseif(key===this._generateKey('channels')){
            this._channels=value;
        }
        //updateoptions
        elseif(key===this._generateKey('options')){
            this._options=value;
        }
        //updatefocus
        elseif(key===this._generateKey('focus')){
            this._isFlectraFocused=value;
            this.trigger('window_focus',this._isFlectraFocused);
        }
    },
    /**
     *Handlerwhenunloadthewindow
     *
     *@private
     */
    _onUnload:function(){
        //unloadpeer
        varpeers=this._callLocalStorage('getItem','peers')||{};
        deletepeers[this._id];
        this._callLocalStorage('setItem','peers',peers);

        //unloadmaster
        if(this._isMasterTab){
            this._callLocalStorage('removeItem','master');
        }
    },
});

returnCrossTabBus;

});

