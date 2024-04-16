#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromflectraimportapi,models,fields,tools

BLACKLIST_MAX_BOUNCED_LIMIT=5


classMailThread(models.AbstractModel):
    """UpdateMailThreadtoaddthesupportofbouncemanagementinmassmailingtraces."""
    _inherit='mail.thread'

    @api.model
    def_message_route_process(self,message,message_dict,routes):
        """Overridetoupdatetheparentmailingtraces.Theparentisfound
        byusingtheReferencesheaderoftheincomingmessageandlookingfor
        matchingmessage_idinmailing.trace."""
        ifroutes:
            #evenif'reply_to'inref(cfrmail/mail_thread)thatindicatesanewthreadredirection
            #(akabypassaliasconfigurationingateway)consideritasareplyforstatisticspurpose
            thread_references=message_dict['references']ormessage_dict['in_reply_to']
            msg_references=tools.mail_header_msgid_re.findall(thread_references)
            ifmsg_references:
                self.env['mailing.trace'].set_opened(mail_message_ids=msg_references)
                self.env['mailing.trace'].set_replied(mail_message_ids=msg_references)
        returnsuper(MailThread,self)._message_route_process(message,message_dict,routes)

    defmessage_post_with_template(self,template_id,**kwargs):
        #avoidhavingmessagesendthrough`message_post*`methodsbeingimplicitlyconsideredas
        #mass-mailing
        no_massmail=self.with_context(
            default_mass_mailing_name=False,
            default_mass_mailing_id=False,
        )
        returnsuper(MailThread,no_massmail).message_post_with_template(template_id,**kwargs)

    @api.model
    def_routing_handle_bounce(self,email_message,message_dict):
        """Inaddition,anautoblacklistrulecheckiftheemailcanbeblacklisted
        toavoidsendingmailsindefinitelytothisemailaddress.
        Thisrulechecksiftheemailbouncedtoomuch.Ifthisisthecase,
        theemailaddressisaddedtotheblacklistinordertoavoidcontinuing
        tosendmass_mailtothatemailaddress.Ifitbouncedtoomuchtimes
        inthelastmonthandthebouncedareatleastseparatedbyoneweek,
        toavoidblacklistsomeonebecauseofatemporarymailservererror,
        thentheemailisconsideredasinvalidandisblacklisted."""
        super(MailThread,self)._routing_handle_bounce(email_message,message_dict)

        bounced_email=message_dict['bounced_email']
        bounced_msg_id=message_dict['bounced_msg_id']
        bounced_partner=message_dict['bounced_partner']

        ifbounced_msg_id:
            self.env['mailing.trace'].set_bounced(mail_message_ids=bounced_msg_id)
        ifbounced_email:
            three_months_ago=fields.Datetime.to_string(datetime.datetime.now()-datetime.timedelta(weeks=13))
            stats=self.env['mailing.trace'].search(['&',('bounced','>',three_months_ago),('email','=ilike',bounced_email)]).mapped('bounced')
            iflen(stats)>=BLACKLIST_MAX_BOUNCED_LIMITand(notbounced_partnerorany(p.message_bounce>=BLACKLIST_MAX_BOUNCED_LIMITforpinbounced_partner)):
                ifmax(stats)>min(stats)+datetime.timedelta(weeks=1):
                    blacklist_rec=self.env['mail.blacklist'].sudo()._add(bounced_email)
                    blacklist_rec._message_log(
                        body='Thisemailhasbeenautomaticallyblacklistedbecauseoftoomuchbounced.')

    @api.model
    defmessage_new(self,msg_dict,custom_values=None):
        """Overridesmail_threadmessage_newthatiscalledbythemailgateway
            throughmessage_process.
            Thisoverrideupdatesthedocumentaccordingtotheemail.
        """
        defaults={}

        ifisinstance(self,self.pool['utm.mixin']):
            thread_references=msg_dict.get('references','')ormsg_dict.get('in_reply_to','')
            msg_references=tools.mail_header_msgid_re.findall(thread_references)
            ifmsg_references:
                traces=self.env['mailing.trace'].search([('message_id','in',msg_references)],limit=1)
                iftraces:
                    defaults['campaign_id']=traces.campaign_id.id
                    defaults['source_id']=traces.mass_mailing_id.source_id.id
                    defaults['medium_id']=traces.mass_mailing_id.medium_id.id

        ifcustom_values:
            defaults.update(custom_values)

        returnsuper(MailThread,self).message_new(msg_dict,custom_values=defaults)
