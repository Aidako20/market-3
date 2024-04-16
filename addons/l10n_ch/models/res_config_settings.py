#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    l10n_ch_isr_preprinted_account=fields.Boolean(string='Preprintedaccount',
        related="company_id.l10n_ch_isr_preprinted_account",readonly=False)
    l10n_ch_isr_preprinted_bank=fields.Boolean(string='Preprintedbank',
        related="company_id.l10n_ch_isr_preprinted_bank",readonly=False)
    l10n_ch_isr_print_bank_location=fields.Boolean(string="PrintbankonISR",
        related="company_id.l10n_ch_isr_print_bank_location",readonly=False,
        required=True)
    l10n_ch_isr_scan_line_left=fields.Float(string='Horizontaloffset',
        related="company_id.l10n_ch_isr_scan_line_left",readonly=False)
    l10n_ch_isr_scan_line_top=fields.Float(string='Verticaloffset',
        related="company_id.l10n_ch_isr_scan_line_top",readonly=False)
