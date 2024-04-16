#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
fromthreadingimportEvent
importtime

fromflectra.httpimportrequest

classEventManager(object):
    def__init__(self):
        self.events=[]
        self.sessions={}

    def_delete_expired_sessions(self,max_time=70):
        '''
        Clearssessionsthatarenolongercalled.

        :parammax_time:timeasessioncanstayunusedbeforebeingdeleted
        '''
        now=time.time()
        expired_sessions=[
            session
            forsessioninself.sessions
            ifnow-self.sessions[session]['time_request']>max_time
        ]
        forsessioninexpired_sessions:
            delself.sessions[session]

    defadd_request(self,listener):
        self.session={
            'session_id':listener['session_id'],
            'devices':listener['devices'],
            'event':Event(),
            'result':{},
            'time_request':time.time(),
        }
        self._delete_expired_sessions()
        self.sessions[listener['session_id']]=self.session
        returnself.sessions[listener['session_id']]

    defdevice_changed(self,device):
        event={
            **device.data,
            'device_identifier':device.device_identifier,
            'time':time.time(),
            'request_data':json.loads(request.params['data'])ifrequestand'data'inrequest.paramselseNone,
        }
        self.events.append(event)
        forsessioninself.sessions:
            ifdevice.device_identifierinself.sessions[session]['devices']andnotself.sessions[session]['event'].isSet():
                self.sessions[session]['result']=event
                self.sessions[session]['event'].set()


event_manager=EventManager()
