#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classMailChannel(models.Model):
    _inherit='mail.channel'

    def_convert_visitor_to_lead(self,partner,channel_partners,key):
        """Whenwebsiteisinstalled,wecanlinkthecreatedleadfrom/leadcommand
         tothecurrentwebsite_visitor.Wedonotusetheleadnameasitdoesnotcorrespond
         totheleadcontactname."""
        lead=super(MailChannel,self)._convert_visitor_to_lead(partner,channel_partners,key)
        visitor_sudo=self.livechat_visitor_id.sudo()
        ifvisitor_sudo:
            visitor_sudo.write({'lead_ids':[(4,lead.id)]})
            lead.country_id=lead.country_idorvisitor_sudo.country_id
        returnlead
