#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classLead(models.Model):
    _inherit='crm.lead'

    visitor_sessions_count=fields.Integer('#Sessions',compute="_compute_visitor_sessions_count",groups="im_livechat.im_livechat_group_user")

    @api.depends('visitor_ids.mail_channel_ids')
    def_compute_visitor_sessions_count(self):
        forleadinself:
            lead.visitor_sessions_count=len(lead.visitor_ids.mail_channel_ids)

    defaction_redirect_to_livechat_sessions(self):
        visitors=self.visitor_ids
        action=self.env["ir.actions.actions"]._for_xml_id("website_livechat.website_visitor_livechat_session_action")
        action['domain']=[('livechat_visitor_id','in',visitors.ids),('channel_message_ids','!=',False)]
        returnaction
