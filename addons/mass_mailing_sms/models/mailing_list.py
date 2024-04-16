#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classMailingList(models.Model):
    _inherit='mailing.list'

    def_compute_contact_nbr(self):
        ifself.env.context.get('mailing_sms')andself.ids:
            self.env.cr.execute('''
selectlist_id,count(*)
frommailing_contact_list_relr
leftjoinmailing_contactcon(r.contact_id=c.id)
leftjoinphone_blacklistblonc.phone_sanitized=bl.numberandbl.active
where
    list_idin%s
    ANDCOALESCE(r.opt_out,FALSE)=FALSE
    ANDc.phone_sanitizedISNOTNULL
    ANDbl.idISNULL
groupbylist_id''',(tuple(self.ids),))
            data=dict(self.env.cr.fetchall())
            formailing_listinself:
                mailing_list.contact_nbr=data.get(mailing_list.id,0)
            return
        returnsuper(MailingList,self)._compute_contact_nbr()

    defaction_view_contacts(self):
        ifself.env.context.get('mailing_sms'):
            action=self.env["ir.actions.actions"]._for_xml_id("mass_mailing_sms.mailing_contact_action_sms")
            action['domain']=[('list_ids','in',self.ids)]
            context=dict(self.env.context,search_default_filter_valid_sms_recipient=1,default_list_ids=self.ids)
            action['context']=context
            returnaction
        returnsuper(MailingList,self).action_view_contacts()
