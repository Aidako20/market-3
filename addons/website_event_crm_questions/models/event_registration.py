#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_


classEventRegistration(models.Model):
    _inherit='event.registration'

    def_get_lead_description_registration(self,prefix='',line_suffix=''):
        """Addthequestionsandanswerslinkedtotheregistrationsintothedescriptionofthelead."""
        reg_description=super(EventRegistration,self)._get_lead_description_registration(prefix=prefix,line_suffix=line_suffix)
        ifnotself.registration_answer_ids:
            returnreg_description

        answer_descriptions=[]
        foranswerinself.registration_answer_ids:
            answer_value=answer.value_answer_id.nameifanswer.question_type=="simple_choice"elseanswer.value_text_box
            answer_value="\n".join(["   %s"%lineforlineinanswer_value.split('\n')])
            answer_descriptions.append(" -%s\n%s"%(answer.question_id.title,answer_value))
        return"%s\n%s\n%s"%(reg_description,_("Questions"),'\n'.join(answer_descriptions))

    def_get_lead_description_fields(self):
        res=super(EventRegistration,self)._get_lead_description_fields()
        res.append('registration_answer_ids')
        returnres
