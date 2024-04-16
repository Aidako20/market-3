#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_


classMailBot(models.AbstractModel):
    _inherit='mail.bot'

    def_get_answer(self,record,body,values,command):
        flectrabot_state=self.env.user.flectrabot_state
        ifself._is_bot_in_private_channel(record):
            ifflectrabot_state=="onboarding_attachement"andvalues.get("attachment_ids"):
                self.env.user.flectrabot_failed=False
                self.env.user.flectrabot_state="onboarding_canned"
                return_("That'sme!🎉<br/>Trytyping<spanclass=\"o_flectrabot_command\">:</span>tousecannedresponses.")
            elifflectrabot_state=="onboarding_canned"andvalues.get("canned_response_ids"):
                self.env.user.flectrabot_failed=False
                self.env.user.flectrabot_state="idle"
                return_("Good,youcancustomizecannedresponsesinthelivechatapplication.<br/><br/><b>It'stheendofthisoverview</b>,enjoydiscoveringFlectra!")
            #repeatquestionifneeded
            elifflectrabot_state=='onboarding_canned'andnotself._is_help_requested(body):
                self.env.user.flectrabot_failed=True
                return_("Notsurewhatyouaredoing.Please,type<spanclass=\"o_flectrabot_command\">:</span>andwaitforthepropositions.Selectoneofthemandpressenter.")
        returnsuper(MailBot,self)._get_answer(record,body,values,command)
