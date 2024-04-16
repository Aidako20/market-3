#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models

classCompany(models.Model):
    _inherit="res.company"

    l10n_ch_isr_preprinted_account=fields.Boolean(string='Preprintedaccount',compute='_compute_l10n_ch_isr',inverse='_set_l10n_ch_isr')
    l10n_ch_isr_preprinted_bank=fields.Boolean(string='Preprintedbank',compute='_compute_l10n_ch_isr',inverse='_set_l10n_ch_isr')
    l10n_ch_isr_print_bank_location=fields.Boolean(string='Printbanklocation',default=False,help='Booleanoptionfieldindicatingwhetherornotthealternatelayout(theoneprintingbanknameandaddress)mustbeusedwhengeneratinganISR.')
    l10n_ch_isr_scan_line_left=fields.Float(string='Scanlinehorizontaloffset(mm)',compute='_compute_l10n_ch_isr',inverse='_set_l10n_ch_isr')
    l10n_ch_isr_scan_line_top=fields.Float(string='Scanlineverticaloffset(mm)',compute='_compute_l10n_ch_isr',inverse='_set_l10n_ch_isr')

    def_compute_l10n_ch_isr(self):
        get_param=self.env['ir.config_parameter'].sudo().get_param
        forcompanyinself:
            company.l10n_ch_isr_preprinted_account=bool(get_param('l10n_ch.isr_preprinted_account',default=False))
            company.l10n_ch_isr_preprinted_bank=bool(get_param('l10n_ch.isr_preprinted_bank',default=False))
            company.l10n_ch_isr_scan_line_top=float(get_param('l10n_ch.isr_scan_line_top',default=0))
            company.l10n_ch_isr_scan_line_left=float(get_param('l10n_ch.isr_scan_line_left',default=0))

    def_set_l10n_ch_isr(self):
        set_param=self.env['ir.config_parameter'].sudo().set_param
        forcompanyinself:
            set_param("l10n_ch.isr_preprinted_account",company.l10n_ch_isr_preprinted_account)
            set_param("l10n_ch.isr_preprinted_bank",company.l10n_ch_isr_preprinted_bank)
            set_param("l10n_ch.isr_scan_line_top",company.l10n_ch_isr_scan_line_top)
            set_param("l10n_ch.isr_scan_line_left",company.l10n_ch_isr_scan_line_left)
