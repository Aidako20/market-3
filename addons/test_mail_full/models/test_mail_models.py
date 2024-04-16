#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classMailTestPortal(models.Model):
    """Amodelintheritingfrommail.threadwithsomefieldsusedforportal
    sharing,likeapartner,..."""
    _description='ChatterModelforPortal'
    _name='mail.test.portal'
    _inherit=[
        'mail.thread',
        'portal.mixin',
    ]

    name=fields.Char()
    partner_id=fields.Many2one('res.partner','Customer')

    def_compute_access_url(self):
        self.access_url=False
        forrecordinself.filtered('id'):
            record.access_url='/my/test_portal/%s'%self.id


classMailTestSMS(models.Model):
    """Amodelinheritingfrommail.threadwithsomefieldsusedforSMS
    gateway,likeapartner,aspecificmobilephone,..."""
    _description='ChatterModelforSMSGateway'
    _name='mail.test.sms'
    _inherit=['mail.thread']
    _order='nameasc,idasc'

    name=fields.Char()
    subject=fields.Char()
    email_from=fields.Char()
    phone_nbr=fields.Char()
    mobile_nbr=fields.Char()
    customer_id=fields.Many2one('res.partner','Customer')

    def_sms_get_partner_fields(self):
        return['customer_id']

    def_sms_get_number_fields(self):
        return['phone_nbr','mobile_nbr']


classMailTestSMSBL(models.Model):
    """Amodelinheritingfrommail.thread.phoneallowingtotestautoformatting
    ofphonenumbers,blacklist,..."""
    _description='SMSMailingBlacklistEnabled'
    _name='mail.test.sms.bl'
    _inherit=['mail.thread.phone']
    _order='nameasc,idasc'

    name=fields.Char()
    subject=fields.Char()
    email_from=fields.Char()
    phone_nbr=fields.Char()
    mobile_nbr=fields.Char()
    customer_id=fields.Many2one('res.partner','Customer')

    def_sms_get_partner_fields(self):
        return['customer_id']

    def_sms_get_number_fields(self):
        #TDEnote:shouldoverride_phone_get_number_fieldsbutokassmsindependencies
        return['phone_nbr','mobile_nbr']


classMailTestSMSOptout(models.Model):
    """Modelusingblacklistmechanismandahijackedopt-outmechanismfor
    massmailingfeatures."""
    _description='SMSMailingBlacklist/OptoutEnabled'
    _name='mail.test.sms.bl.optout'
    _inherit=['mail.thread.phone']
    _order='nameasc,idasc'

    name=fields.Char()
    subject=fields.Char()
    email_from=fields.Char()
    phone_nbr=fields.Char()
    mobile_nbr=fields.Char()
    customer_id=fields.Many2one('res.partner','Customer')
    opt_out=fields.Boolean()

    def_sms_get_partner_fields(self):
        return['customer_id']

    def_sms_get_number_fields(self):
        #TDEnote:shouldoverride_phone_get_number_fieldsbutokassmsindependencies
        return['phone_nbr','mobile_nbr']


classMailTestSMSPartner(models.Model):
    """Amodellikesaleorderhavingonlyacustomer,notspecificphone
    ormobilefields."""
    _description='ChatterModelforSMSGateway(Partneronly)'
    _name='mail.test.sms.partner'
    _inherit=['mail.thread']

    name=fields.Char()
    customer_id=fields.Many2one('res.partner','Customer')
    opt_out=fields.Boolean()

    def_sms_get_partner_fields(self):
        return['customer_id']

    def_sms_get_number_fields(self):
        return[]


classMailTestSMSPartner2Many(models.Model):
    """Amodellikesaleorderhavingonlyacustomer,notspecificphone
    ormobilefields."""
    _description='ChatterModelforSMSGateway(M2MPartnersonly)'
    _name='mail.test.sms.partner.2many'
    _inherit=['mail.thread']

    name=fields.Char()
    customer_ids=fields.Many2many('res.partner',string='Customers')
    opt_out=fields.Boolean()

    def_sms_get_partner_fields(self):
        return['customer_ids']

    def_sms_get_number_fields(self):
        return[]
