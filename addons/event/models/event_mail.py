#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importrandom
importthreading

fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,tools
fromflectra.toolsimportexception_to_unicode
fromflectra.tools.translateimport_

_logger=logging.getLogger(__name__)

_INTERVALS={
    'hours':lambdainterval:relativedelta(hours=interval),
    'days':lambdainterval:relativedelta(days=interval),
    'weeks':lambdainterval:relativedelta(days=7*interval),
    'months':lambdainterval:relativedelta(months=interval),
    'now':lambdainterval:relativedelta(hours=0),
}


classEventTypeMail(models.Model):
    """Templateofevent.mailtoattachtoevent.type.Thosewillbecopied
    uponalleventscreatedinthattypetoeaseeventcreation."""
    _name='event.type.mail'
    _description='MailSchedulingonEventCategory'

    event_type_id=fields.Many2one(
        'event.type',string='EventType',
        ondelete='cascade',required=True)
    notification_type=fields.Selection([('mail','Mail')],string='Send',default='mail',required=True)
    interval_nbr=fields.Integer('Interval',default=1)
    interval_unit=fields.Selection([
        ('now','Immediately'),
        ('hours','Hours'),('days','Days'),
        ('weeks','Weeks'),('months','Months')],
        string='Unit',default='hours',required=True)
    interval_type=fields.Selection([
        ('after_sub','Aftereachregistration'),
        ('before_event','Beforetheevent'),
        ('after_event','Aftertheevent')],
        string='Trigger',default="before_event",required=True)
    template_id=fields.Many2one(
        'mail.template',string='EmailTemplate',
        domain=[('model','=','event.registration')],ondelete='restrict',
        help='Thisfieldcontainsthetemplateofthemailthatwillbeautomaticallysent')

    @api.model
    def_get_event_mail_fields_whitelist(self):
        """Whitelistoffieldsthatarecopiedfromevent_type_mail_idstoevent_mail_idswhen
        changingtheevent_type_idfieldofevent.event"""
        return['notification_type','template_id','interval_nbr','interval_unit','interval_type']


classEventMailScheduler(models.Model):
    """Eventautomatedmailing.Thismodelreplacesallexistingfieldsand
    configurationallowingtosendemailsoneventssinceFlectra9.Acronexists
    thatperiodicallychecksformailingtorun."""
    _name='event.mail'
    _rec_name='event_id'
    _description='EventAutomatedMailing'

    event_id=fields.Many2one('event.event',string='Event',required=True,ondelete='cascade')
    sequence=fields.Integer('Displayorder')
    notification_type=fields.Selection([('mail','Mail')],string='Send',default='mail',required=True)
    interval_nbr=fields.Integer('Interval',default=1)
    interval_unit=fields.Selection([
        ('now','Immediately'),
        ('hours','Hours'),('days','Days'),
        ('weeks','Weeks'),('months','Months')],
        string='Unit',default='hours',required=True)
    interval_type=fields.Selection([
        ('after_sub','Aftereachregistration'),
        ('before_event','Beforetheevent'),
        ('after_event','Aftertheevent')],
        string='Trigger',default="before_event",required=True)
    template_id=fields.Many2one(
        'mail.template',string='EmailTemplate',
        domain=[('model','=','event.registration')],ondelete='restrict',
        help='Thisfieldcontainsthetemplateofthemailthatwillbeautomaticallysent')
    scheduled_date=fields.Datetime('ScheduledSentMail',compute='_compute_scheduled_date',store=True)
    mail_registration_ids=fields.One2many('event.mail.registration','scheduler_id')
    mail_sent=fields.Boolean('MailSentonEvent',copy=False)
    done=fields.Boolean('Sent',compute='_compute_done',store=True)

    @api.depends('mail_sent','interval_type','event_id.registration_ids','mail_registration_ids')
    def_compute_done(self):
        formailinself:
            ifmail.interval_typein['before_event','after_event']:
                mail.done=mail.mail_sent
            else:
                mail.done=len(mail.mail_registration_ids)==len(mail.event_id.registration_ids)andall(mail.mail_sentformailinmail.mail_registration_ids)

    @api.depends('event_id.date_begin','interval_type','interval_unit','interval_nbr')
    def_compute_scheduled_date(self):
        formailinself:
            ifmail.interval_type=='after_sub':
                date,sign=mail.event_id.create_date,1
            elifmail.interval_type=='before_event':
                date,sign=mail.event_id.date_begin,-1
            else:
                date,sign=mail.event_id.date_end,1

            mail.scheduled_date=date+_INTERVALS[mail.interval_unit](sign*mail.interval_nbr)ifdateelseFalse

    defexecute(self):
        formailinself:
            now=fields.Datetime.now()
            ifmail.interval_type=='after_sub':
                #updateregistrationlines
                lines=[
                    (0,0,{'registration_id':registration.id})
                    forregistrationin(mail.event_id.registration_ids-mail.mapped('mail_registration_ids.registration_id'))
                ]
                iflines:
                    mail.write({'mail_registration_ids':lines})
                #executescheduleronregistrations
                mail.mail_registration_ids.execute()
            else:
                #Donotsendemailsifthemailingwasscheduledbeforetheeventbuttheeventisover
                ifnotmail.mail_sentandmail.scheduled_date<=nowandmail.notification_type=='mail'and\
                        (mail.interval_type!='before_event'ormail.event_id.date_end>now):
                    mail.event_id.mail_attendees(mail.template_id.id)
                    mail.write({'mail_sent':True})
        returnTrue

    @api.model
    def_warn_template_error(self,scheduler,exception):
        #Wewarn~oncebyhour~insteadofevery10miniftheintervalunitismorethan'hours'.
        ifrandom.random()<0.1666orscheduler.interval_unitin('now','hours'):
            ex_s=exception_to_unicode(exception)
            try:
                event,template=scheduler.event_id,scheduler.template_id
                emails=list(set([event.organizer_id.email,event.user_id.email,template.write_uid.email]))
                subject=_("WARNING:EventSchedulerErrorforevent:%s",event.name)
                body=_("""EventSchedulerfor:
  -Event:%(event_name)s(%(event_id)s)
  -Scheduled:%(date)s
  -Template:%(template_name)s(%(template_id)s)

Failedwitherror:
  -%(error)s

Youreceivethisemailbecauseyouare:
  -theorganizeroftheevent,
  -ortheresponsibleoftheevent,
  -orthelastwriterofthetemplate.
""",
                         event_name=event.name,
                         event_id=event.id,
                         date=scheduler.scheduled_date,
                         template_name=template.name,
                         template_id=template.id,
                         error=ex_s)
                email=self.env['ir.mail_server'].build_email(
                    email_from=self.env.user.email,
                    email_to=emails,
                    subject=subject,body=body,
                )
                self.env['ir.mail_server'].send_email(email)
            exceptExceptionase:
                _logger.error("Exceptionwhilesendingtracebackbyemail:%s.\nOriginalTraceback:\n%s",e,exception)
                pass

    @api.model
    defrun(self,autocommit=False):
        schedulers=self.search([
            ('event_id.active','=',True),
            ('done','=',False),
            ('scheduled_date','<=',datetime.strftime(fields.datetime.now(),tools.DEFAULT_SERVER_DATETIME_FORMAT))
        ])
        forschedulerinschedulers:
            try:
                withself.env.cr.savepoint():
                    #Preventamegaprefetchoftheregistrationidsofalltheeventsofalltheschedulers
                    self.browse(scheduler.id).execute()
            exceptExceptionase:
                _logger.exception(e)
                self.invalidate_cache()
                self._warn_template_error(scheduler,e)
            else:
                ifautocommitandnotgetattr(threading.currentThread(),'testing',False):
                    self.env.cr.commit()
        returnTrue


classEventMailRegistration(models.Model):
    _name='event.mail.registration'
    _description='RegistrationMailScheduler'
    _rec_name='scheduler_id'
    _order='scheduled_dateDESC'

    scheduler_id=fields.Many2one('event.mail','MailScheduler',required=True,ondelete='cascade')
    registration_id=fields.Many2one('event.registration','Attendee',required=True,ondelete='cascade')
    scheduled_date=fields.Datetime('ScheduledTime',compute='_compute_scheduled_date',store=True)
    mail_sent=fields.Boolean('MailSent')

    defexecute(self):
        now=fields.Datetime.now()
        todo=self.filtered(lambdareg_mail:
            notreg_mail.mail_sentand\
            reg_mail.registration_id.statein['open','done']and\
            (reg_mail.scheduled_dateandreg_mail.scheduled_date<=now)and\
            reg_mail.scheduler_id.notification_type=='mail'
        )
        forreg_mailintodo:
            organizer=reg_mail.scheduler_id.event_id.organizer_id
            company=self.env.company
            author=self.env.ref('base.user_root')
            iforganizer.email:
                author=organizer
            elifcompany.email:
                author=company.partner_id
            elifself.env.user.email:
                author=self.env.user

            email_values={
                'author_id':author.id,
            }
            ifnotreg_mail.scheduler_id.template_id.email_from:
                email_values['email_from']=author.email_formatted
            reg_mail.scheduler_id.template_id.send_mail(reg_mail.registration_id.id,email_values=email_values)
        todo.write({'mail_sent':True})

    @api.depends('registration_id','scheduler_id.interval_unit','scheduler_id.interval_type')
    def_compute_scheduled_date(self):
        formailinself:
            ifmail.registration_id:
                date_open=mail.registration_id.date_open
                date_open_datetime=date_openorfields.Datetime.now()
                mail.scheduled_date=date_open_datetime+_INTERVALS[mail.scheduler_id.interval_unit](mail.scheduler_id.interval_nbr)
            else:
                mail.scheduled_date=False
