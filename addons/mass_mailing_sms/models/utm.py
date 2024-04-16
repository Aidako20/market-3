#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classUtmCampaign(models.Model):
    _inherit='utm.campaign'

    mailing_sms_ids=fields.One2many(
        'mailing.mailing','campaign_id',
        domain=[('mailing_type','=','sms')],
        string='MassSMS')
    mailing_sms_count=fields.Integer('NumberofMassSMS',compute="_compute_mailing_sms_count")

    @api.depends('mailing_sms_ids')
    def_compute_mailing_sms_count(self):
        forcampaigninself:
            campaign.mailing_sms_count=len(campaign.mailing_sms_ids)

    defaction_create_mass_sms(self):
        action=self.env["ir.actions.actions"]._for_xml_id("mass_mailing.action_create_mass_mailings_from_campaign")
        action['context']={
            'default_campaign_id':self.id,
            'default_mailing_type':'sms',
            'search_default_assigned_to_me':1,
            'search_default_campaign_id':self.id,
            'default_user_id':self.env.user.id,
        }
        returnaction

    defaction_redirect_to_mailing_sms(self):
        action=self.env["ir.actions.actions"]._for_xml_id("mass_mailing_sms.mailing_mailing_action_sms")
        action['context']={
            'default_campaign_id':self.id,
            'default_mailing_type':'sms',
            'search_default_assigned_to_me':1,
            'search_default_campaign_id':self.id,
            'default_user_id':self.env.user.id,
        }
        action['domain']=[('mailing_type','=','sms')]
        returnaction
