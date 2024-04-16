#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,models
fromflectra.exceptionsimportUserError


classAccountMove(models.Model):
    _inherit="account.move"

    defaction_open_l10n_ph_2307_wizard(self):
        vendor_bills=self.filtered_domain([('move_type','=','in_invoice')])
        ifvendor_bills:
            wizard_action=self.env["ir.actions.act_window"]._for_xml_id("l10n_ph.view_l10n_ph_2307_wizard_act_window")
            wizard_action.update({
                'context':{'default_moves_to_export':vendor_bills.ids}
            })
            returnwizard_action
        else:
            raiseUserError(_('OnlyVendorBillsareavailable.'))
