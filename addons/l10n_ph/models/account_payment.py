#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,models
fromflectra.exceptionsimportUserError


classAccountPayment(models.Model):
    _inherit="account.payment"

    defaction_open_l10n_ph_2307_wizard(self):
        self.ensure_one()
        ifself.payment_type=='outbound':
            wizard_action=self.env["ir.actions.act_window"]._for_xml_id("l10n_ph.view_l10n_ph_2307_wizard_act_window")
            wizard_action.update({
                'context':{'default_moves_to_export':self.reconciled_bill_ids.ids}
            })
            returnwizard_action
        else:
            raiseUserError(_('OnlyOutboundPaymentisavailable.'))
