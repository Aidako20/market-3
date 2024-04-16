#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classWebsiteVisitor(models.Model):
    _inherit='website.visitor'

    def_check_for_sms_composer(self):
        check=super(WebsiteVisitor,self)._check_for_sms_composer()
        ifnotcheckandself.lead_ids:
            sorted_leads=self.lead_ids.filtered(lambdal:l.mobile==self.mobileorl.phone==self.mobile)._sort_by_confidence_level(reverse=True)
            ifsorted_leads:
                returnTrue
        returncheck

    def_prepare_sms_composer_context(self):
        ifnotself.partner_idandself.lead_ids:
            leads_with_number=self.lead_ids.filtered(lambdal:l.mobile==self.mobileorl.phone==self.mobile)._sort_by_confidence_level(reverse=True)
            ifleads_with_number:
                lead=leads_with_number[0]
                return{
                    'default_res_model':'crm.lead',
                    'default_res_id':lead.id,
                    'number_field_name':'mobile'iflead.mobile==self.mobileelse'phone',
                }
        returnsuper(WebsiteVisitor,self)._prepare_sms_composer_context()
