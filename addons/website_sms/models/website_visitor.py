#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_
fromflectra.exceptionsimportUserError


classWebsiteVisitor(models.Model):
    _inherit='website.visitor'

    def_check_for_sms_composer(self):
        """Purposeofthismethodistoactualizevisitormodelpriortocontacting
        him.Usednotablyforinheritancepurpose,whendealingwithleadsthat
        couldupdatethevisitormodel."""
        returnbool(self.partner_idand(self.partner_id.mobileorself.partner_id.phone))

    def_prepare_sms_composer_context(self):
        return{
            'default_res_model':'res.partner',
            'default_res_id':self.partner_id.id,
            'default_composition_mode':'comment',
            'default_number_field_name':'mobile'ifself.partner_id.mobileelse'phone',
        }

    defaction_send_sms(self):
        self.ensure_one()
        ifnotself._check_for_sms_composer():
            raiseUserError(_("Therearenocontactand/ornophoneormobilenumberslinkedtothisvisitor."))
        visitor_composer_ctx=self._prepare_sms_composer_context()

        compose_ctx=dict(self.env.context)
        compose_ctx.update(**visitor_composer_ctx)
        return{
            "name":_("SendSMSTextMessage"),
            "type":"ir.actions.act_window",
            "res_model":"sms.composer",
            "view_mode":'form',
            "context":compose_ctx,
            "target":"new",
        }
