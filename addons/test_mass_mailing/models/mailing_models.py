#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classMailingCustomer(models.Model):
    """Amodelinheritingfrommail.threadwithapartnerfield,totest
    massmailingflowsinvolvingcheckingpartneremail."""
    _description='Mailingwithpartner'
    _name='mailing.test.customer'
    _inherit=['mail.thread']

    name=fields.Char()
    email_from=fields.Char(compute='_compute_email_from',readonly=False,store=True)
    customer_id=fields.Many2one('res.partner','Customer',tracking=True)

    @api.depends('customer_id')
    def_compute_email_from(self):
        formailinginself.filtered(lambdarec:notrec.email_fromandrec.customer_id):
            mailing.email_from=mailing.customer_id.email

    def_message_get_default_recipients(self):
        """Defaultrecipientchecksfor'partner_id',herethefieldisnamed
        'customer_id'."""
        default_recipients=super()._message_get_default_recipients()
        forrecordinself:
            ifrecord.customer_id:
                default_recipients[record.id]={
                    'email_cc':False,
                    'email_to':False,
                    'partner_ids':record.customer_id.ids,
                }
        returndefault_recipients


classMailingSimple(models.Model):
    """Modelonlyinheritingfrommail.threadtotestbasemailingfeaturesand
    performances."""
    _description='SimpleMailing'
    _name='mailing.test.simple'
    _inherit=['mail.thread']

    name=fields.Char()
    email_from=fields.Char()


classMailingUTM(models.Model):
    """Modelinheritingfrommail.threadandutm.mixinforcheckingutmofmailing
    iscaughtandsetonreply"""
    _description='Mailing:UTMenabledtotestUTMsyncwithmailing'
    _name='mailing.test.utm'
    _inherit=['mail.thread','utm.mixin']

    name=fields.Char()


classMailingBLacklist(models.Model):
    """Modelusingblacklistmechanismformassmailingfeatures."""
    _description='MailingBlacklistEnabled'
    _name='mailing.test.blacklist'
    _inherit=['mail.thread.blacklist']
    _primary_email='email_from'

    name=fields.Char()
    email_from=fields.Char()
    customer_id=fields.Many2one('res.partner','Customer',tracking=True)
    user_id=fields.Many2one('res.users','Responsible',tracking=True)

    def_message_get_default_recipients(self):
        """Defaultrecipientchecksfor'partner_id',herethefieldisnamed
        'customer_id'."""
        default_recipients=super()._message_get_default_recipients()
        forrecordinself:
            ifrecord.customer_id:
                default_recipients[record.id]={
                    'email_cc':False,
                    'email_to':False,
                    'partner_ids':record.customer_id.ids,
                }
        returndefault_recipients


classMailingOptOut(models.Model):
    """Modelusingblacklistmechanismandahijackedopt-outmechanismfor
    massmailingfeatures."""
    _description='MailingBlacklist/OptoutEnabled'
    _name='mailing.test.optout'
    _inherit=['mail.thread.blacklist']
    _primary_email='email_from'

    name=fields.Char()
    email_from=fields.Char()
    opt_out=fields.Boolean()
    customer_id=fields.Many2one('res.partner','Customer',tracking=True)
    user_id=fields.Many2one('res.users','Responsible',tracking=True)

    def_message_get_default_recipients(self):
        """Defaultrecipientchecksfor'partner_id',herethefieldisnamed
        'customer_id'."""
        default_recipients=super()._message_get_default_recipients()
        forrecordinself:
            ifrecord.customer_id:
                default_recipients[record.id]={
                    'email_cc':False,
                    'email_to':False,
                    'partner_ids':record.customer_id.ids,
                }
        returndefault_recipients

classMailingTestPartner(models.Model):
    _description='MailingModelwithpartner_id'
    _name='mailing.test.partner'
    _inherit=['mail.thread.blacklist']
    _primary_email='email_from'

    name=fields.Char()
    email_from=fields.Char()
    partner_id=fields.Many2one('res.partner','Customer')


classMailingPerformance(models.Model):
    """Averysimplemodelonlyinheritingfrommail.threadtotestpuremass
    mailingperformances."""
    _name='mailing.performance'
    _description='Mailing:baseperformance'
    _inherit=['mail.thread']

    name=fields.Char()
    email_from=fields.Char()


classMailingPerformanceBL(models.Model):
    """Modelusingblacklistmechanismformassmailingperformance."""
    _name='mailing.performance.blacklist'
    _description='Mailing:blacklistperformance'
    _inherit=['mail.thread.blacklist']
    _primary_email='email_from' #blacklistfieldtocheck

    name=fields.Char()
    email_from=fields.Char()
    user_id=fields.Many2one(
        'res.users','Responsible',
        tracking=True)
    container_id=fields.Many2one(
        'mail.test.container','MetaContainerRecord',
        tracking=True)
