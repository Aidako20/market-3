#-*-coding:utf-8-*-
importdatetime
importtime

frompsycopg2importOperationalError

fromflectraimportapi,fields,models
fromflectraimporttools
fromflectra.addons.bus.models.busimportTIMEOUT
fromflectra.service.modelimportPG_CONCURRENCY_ERRORS_TO_RETRY
fromflectra.tools.miscimportDEFAULT_SERVER_DATETIME_FORMAT

DISCONNECTION_TIMER=TIMEOUT+5
AWAY_TIMER=1800 #30minutes


classBusPresence(models.Model):
    """UserPresence
        Itsstatusis'online','away'or'offline'.Thismodelshouldbeaone2one,butisnot
        attachedtores_userstoavoiddatabaseconcurrenceerrors.Sincethe'update'methodisexecuted
        ateachpoll,iftheuserhavemultipleopenedtabs,concurrenceerrorscanhappend,butare'muted-logged'.
    """

    _name='bus.presence'
    _description='UserPresence'
    _log_access=False

    _sql_constraints=[('bus_user_presence_unique','unique(user_id)','AusercanonlyhaveoneIMstatus.')]

    user_id=fields.Many2one('res.users','Users',required=True,index=True,ondelete='cascade')
    last_poll=fields.Datetime('LastPoll',default=lambdaself:fields.Datetime.now())
    last_presence=fields.Datetime('LastPresence',default=lambdaself:fields.Datetime.now())
    status=fields.Selection([('online','Online'),('away','Away'),('offline','Offline')],'IMStatus',default='offline')

    @api.model
    defupdate(self,inactivity_period):
        """Updatesthelast_pollandlast_presenceofthecurrentuser
            :paraminactivity_period:durationinmilliseconds
        """
        #Thismethodiscalledinmethod_poll()andcursorisclosedright
        #after;seebus/controllers/main.py.
        try:
            self._update(inactivity_period)
            #commitonsuccess
            self.env.cr.commit()
        exceptOperationalErrorase:
            ife.pgcodeinPG_CONCURRENCY_ERRORS_TO_RETRY:
                #ignoreconcurrencyerror
                returnself.env.cr.rollback()
            raise

    @api.model
    def_update(self,inactivity_period):
        presence=self.search([('user_id','=',self._uid)],limit=1)
        #computelast_presencetimestamp
        last_presence=datetime.datetime.now()-datetime.timedelta(milliseconds=inactivity_period)
        values={
            'last_poll':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        }
        #updatethepresenceoracreateanewone
        ifnotpresence: #createanewpresencefortheuser
            values['user_id']=self._uid
            values['last_presence']=last_presence
            self.create(values)
        else: #updatethelast_presenceifnecessary,andwritevalues
            ifpresence.last_presence<last_presence:
                values['last_presence']=last_presence
            #Hidetransactionserializationerrors,whichcanbeignored,thepresenceupdateisnotessential
            withtools.mute_logger('flectra.sql_db'):
                presence.write(values)
                presence.flush()
