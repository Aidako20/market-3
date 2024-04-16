#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classMailTestSimple(models.Model):
    """Averysimplemodelonlyinheritingfrommail.threadwhenonly
    communicationhistoryisnecessary."""
    _description='SimpleChatterModel'
    _name='mail.test.simple'
    _inherit=['mail.thread']

    name=fields.Char()
    email_from=fields.Char()


classMailTestGateway(models.Model):
    """Averysimplemodelonlyinheritingfrommail.threadtotestpuremass
    mailingfeaturesandbaseperformances."""
    _description='SimpleChatterModelforMailGateway'
    _name='mail.test.gateway'
    _inherit=['mail.thread.blacklist']
    _primary_email='email_from'

    name=fields.Char()
    email_from=fields.Char()
    custom_field=fields.Char()

    @api.model
    defmessage_new(self,msg_dict,custom_values=None):
        """Checkoverrideof'message_new'allowingtoupdaterecordvalues
        baseonincomingemail."""
        defaults={
            'email_from':msg_dict.get('from'),
        }
        defaults.update(custom_valuesor{})
        returnsuper().message_new(msg_dict,custom_values=defaults)


classMailTestGatewayGroups(models.Model):
    """Amodellookinglikediscussionchannels/groups(flatthreadand
    alias).Usednotablyforadvancedgatewxaytests."""
    _description='Channel/Group-likeChatterModelforMailGateway'
    _name='mail.test.gateway.groups'
    _inherit=['mail.thread.blacklist','mail.alias.mixin']
    _mail_flat_thread=False
    _primary_email='email_from'

    name=fields.Char()
    email_from=fields.Char()
    custom_field=fields.Char()
    customer_id=fields.Many2one('res.partner','Customer')

    def_alias_get_creation_values(self):
        values=super(MailTestGatewayGroups,self)._alias_get_creation_values()
        values['alias_model_id']=self.env['ir.model']._get('mail.test.gateway.groups').id
        ifself.id:
            values['alias_force_thread_id']=self.id
            values['alias_parent_thread_id']=self.id
        returnvalues


classMailTestStandard(models.Model):
    """Thismodelcanbeusedintestswhenautomaticsubscriptionandsimple
    trackingisnecessary.Mostfeaturesarepresentinasimpleway."""
    _description='StandardChatterModel'
    _name='mail.test.track'
    _inherit=['mail.thread']

    name=fields.Char()
    email_from=fields.Char()
    user_id=fields.Many2one('res.users','Responsible',tracking=True)
    container_id=fields.Many2one('mail.test.container',tracking=True)
    company_id=fields.Many2one('res.company')

    def_get_share_url(self,redirect,signup_partner,share_token):
        """Thisfunctionisrequiredforateston'mail.mail_notification_paynow'template(test_message_post/test_mail_add_signature),
        anothermodelshouldbecreatedinmaster"""
        return'/mail/view'


classMailTestActivity(models.Model):
    """Thismodelcanbeusedtotestactivitiesinadditiontosimplechatter
    features."""
    _description='ActivityModel'
    _name='mail.test.activity'
    _inherit=['mail.thread','mail.activity.mixin']

    name=fields.Char()
    date=fields.Date()
    email_from=fields.Char()
    active=fields.Boolean(default=True)

    defaction_start(self,action_summary):
        returnself.activity_schedule(
            'test_mail.mail_act_test_todo',
            summary=action_summary
        )

    defaction_close(self,action_feedback):
        self.activity_feedback(['test_mail.mail_act_test_todo'],feedback=action_feedback)


classMailTestTicket(models.Model):
    """Thismodelcanbeusedintestswhencomplexchatterfeaturesare
    requiredlikemodelingtasksortickets."""
    _description='Ticket-likemodel'
    _name='mail.test.ticket'
    _inherit=['mail.thread']

    name=fields.Char()
    email_from=fields.Char(tracking=True)
    count=fields.Integer(default=1)
    datetime=fields.Datetime(default=fields.Datetime.now)
    mail_template=fields.Many2one('mail.template','Template')
    customer_id=fields.Many2one('res.partner','Customer',tracking=2)
    user_id=fields.Many2one('res.users','Responsible',tracking=1)
    container_id=fields.Many2one('mail.test.container',tracking=True)

    def_track_template(self,changes):
        res=super(MailTestTicket,self)._track_template(changes)
        record=self[0]
        if'customer_id'inchangesandrecord.mail_template:
            res['customer_id']=(record.mail_template,{'composition_mode':'mass_mail'})
        elif'datetime'inchanges:
            res['datetime']=('test_mail.mail_test_ticket_tracking_view',{'composition_mode':'mass_mail'})
        returnres

    def_creation_subtype(self):
        ifself.container_id:
            returnself.env.ref('test_mail.st_mail_test_ticket_container_upd')
        returnsuper(MailTestTicket,self)._creation_subtype()

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'container_id'ininit_valuesandself.container_id:
            returnself.env.ref('test_mail.st_mail_test_ticket_container_upd')
        returnsuper(MailTestTicket,self)._track_subtype(init_values)


classMailTestContainer(models.Model):
    """Thismodelcanbeusedintestswhencontainerrecordslikeprojects
    orteamsarerequired."""
    _description='Project-likemodelwithalias'
    _name='mail.test.container'
    _mail_post_access='read'
    _inherit=['mail.thread','mail.alias.mixin']

    name=fields.Char()
    description=fields.Text()
    customer_id=fields.Many2one('res.partner','Customer')
    alias_id=fields.Many2one(
        'mail.alias','Alias',
        delegate=True)

    def_alias_get_creation_values(self):
        values=super(MailTestContainer,self)._alias_get_creation_values()
        values['alias_model_id']=self.env['ir.model']._get('mail.test.container').id
        ifself.id:
            values['alias_force_thread_id']=self.id
            values['alias_parent_thread_id']=self.id
        returnvalues
