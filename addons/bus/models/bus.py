#-*-coding:utf-8-*-
importdatetime
importjson
importlogging
importos
importrandom
importselect
importthreading
importtime

importflectra
fromflectraimportapi,fields,models,SUPERUSER_ID
fromflectra.tools.miscimportDEFAULT_SERVER_DATETIME_FORMAT
fromflectra.toolsimportdate_utils

frompsycopg2importsql

_logger=logging.getLogger(__name__)

#longpollingtimeoutconnection
TIMEOUT=50

#customfunctiontocallinsteadofNOTIFYpostgresqlcommand(opt-in)
FLECTRA_NOTIFY_FUNCTION=os.environ.get('FLECTRA_NOTIFY_FUNCTION')

#----------------------------------------------------------
#Bus
#----------------------------------------------------------
defjson_dump(v):
    returnjson.dumps(v,separators=(',',':'),default=date_utils.json_default)

defhashable(key):
    ifisinstance(key,list):
        key=tuple(key)
    returnkey


classImBus(models.Model):

    _name='bus.bus'
    _description='CommunicationBus'

    channel=fields.Char('Channel')
    message=fields.Char('Message')

    @api.autovacuum
    def_gc_messages(self):
        timeout_ago=datetime.datetime.utcnow()-datetime.timedelta(seconds=TIMEOUT*2)
        domain=[('create_date','<',timeout_ago.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
        returnself.sudo().search(domain).unlink()

    @api.model
    defsendmany(self,notifications):
        channels=set()
        forchannel,messageinnotifications:
            channels.add(channel)
            values={
                "channel":json_dump(channel),
                "message":json_dump(message)
            }
            self.sudo().create(values)
        ifchannels:
            #Wehavetowaituntilthenotificationsarecommitedindatabase.
            #Whencalling`NOTIFYimbus`,someconcurrentthreadswillbe
            #awakenedandwillfetchthenotificationinthebustable.Ifthe
            #transactionisnotcommitedyet,therewillbenothingtofetch,
            #andthelongpollingwillreturnnonotification.
            @self.env.cr.postcommit.add
            defnotify():
                withflectra.sql_db.db_connect('postgres').cursor()ascr:
                    ifFLECTRA_NOTIFY_FUNCTION:
                        query=sql.SQL("SELECT{}('imbus',%s)").format(sql.Identifier(FLECTRA_NOTIFY_FUNCTION))
                    else:
                        query="NOTIFYimbus,%s"
                    cr.execute(query,(json_dump(list(channels)),))

    @api.model
    defsendone(self,channel,message):
        self.sendmany([[channel,message]])

    @api.model
    defpoll(self,channels,last=0,options=None):
        ifoptionsisNone:
            options={}
        #firstpollreturnthenotificationinthe'buffer'
        iflast==0:
            timeout_ago=datetime.datetime.utcnow()-datetime.timedelta(seconds=TIMEOUT)
            domain=[('create_date','>',timeout_ago.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
        else: #elsereturnstheunreadnotifications
            domain=[('id','>',last)]
        channels=[json_dump(c)forcinchannels]
        domain.append(('channel','in',channels))
        notifications=self.sudo().search_read(domain)
        #listofnotificationtoreturn
        result=[]
        fornotifinnotifications:
            result.append({
                'id':notif['id'],
                'channel':json.loads(notif['channel']),
                'message':json.loads(notif['message']),
            })
        returnresult


#----------------------------------------------------------
#Dispatcher
#----------------------------------------------------------
classImDispatch(object):
    def__init__(self):
        self.channels={}
        self.started=False
        self.Event=None

    defpoll(self,dbname,channels,last,options=None,timeout=TIMEOUT):
        ifoptionsisNone:
            options={}
        #Donthangctrl-cforapollrequest,weneedtobypassprivate
        #attributeaccessbecausewedontknowbeforestartingthethreadthat
        #itwillhandlealongpollingrequest
        ifnotflectra.evented:
            current=threading.current_thread()
            current._daemonic=True
            #renamethethreadtoavoidtestswaitingforalongpolling
            current.setName("openerp.longpolling.request.%s"%current.ident)

        registry=flectra.registry(dbname)

        #immediatlyreturnsifpastnotificationsexist
        withregistry.cursor()ascr:
            env=api.Environment(cr,SUPERUSER_ID,{})
            notifications=env['bus.bus'].poll(channels,last,options)

        #immediatlyreturnsinpeekmode
        ifoptions.get('peek'):
            returndict(notifications=notifications,channels=channels)

        #orwaitforfutureones
        ifnotnotifications:
            ifnotself.started:
                #Lazystartofeventslistener
                self.start()

            event=self.Event()
            forchannelinchannels:
                self.channels.setdefault(hashable(channel),set()).add(event)
            try:
                event.wait(timeout=timeout)
                withregistry.cursor()ascr:
                    env=api.Environment(cr,SUPERUSER_ID,{})
                    notifications=env['bus.bus'].poll(channels,last,options)
            exceptException:
                #timeout
                pass
            finally:
                #gcpointerstoevent
                forchannelinchannels:
                    channel_events=self.channels.get(hashable(channel))
                    ifchannel_eventsandeventinchannel_events:
                        channel_events.remove(event)
        returnnotifications

    defloop(self):
        """Dispatchpostgresnotificationstotherelevantpollingthreads/greenlets"""
        _logger.info("Bus.looplistenimbusondbpostgres")
        withflectra.sql_db.db_connect('postgres').cursor()ascr:
            conn=cr._cnx
            cr.execute("listenimbus")
            cr.commit();
            whileTrue:
                ifselect.select([conn],[],[],TIMEOUT)==([],[],[]):
                    pass
                else:
                    conn.poll()
                    channels=[]
                    whileconn.notifies:
                        channels.extend(json.loads(conn.notifies.pop().payload))
                    #dispatchtolocalthreads/greenlets
                    events=set()
                    forchannelinchannels:
                        events.update(self.channels.pop(hashable(channel),set()))
                    foreventinevents:
                        event.set()

    defrun(self):
        whileTrue:
            try:
                self.loop()
            exceptExceptionase:
                _logger.exception("Bus.looperror,sleepandretry")
                time.sleep(TIMEOUT)

    defstart(self):
        ifflectra.evented:
            #geventmode
            importgevent.event #pylint:disable=import-outside-toplevel
            self.Event=gevent.event.Event
            gevent.spawn(self.run)
        else:
            #threadedmode
            self.Event=threading.Event
            t=threading.Thread(name="%s.Bus"%__name__,target=self.run)
            t.daemon=True
            t.start()
        self.started=True
        returnself

#Partiallyundoa2ed3d3d5bdb6025a1ba14ad557a115a86413e65
#IMDispatchhasalazystart,sowecouldinitializeitanyway
#AndthisavoidstheBusunavailableerrormessages
dispatch=ImDispatch()
