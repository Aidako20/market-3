#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classUsers(models.Model):
    _inherit='res.users'

    flectrabot_state=fields.Selection(selection_add=[
        ('onboarding_canned','Onboardingcanned'),
    ],ondelete={'onboarding_canned':lambdausers:users.write({'flectrabot_state':'disabled'})})
