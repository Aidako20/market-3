#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classResPartner(models.Model):
    """Inheritres.partnerobjecttoaddNPWPfieldandKodeTransaksi"""
    _inherit="res.partner"

    country_code=fields.Char(related='country_id.code',string='CountryCode')
    l10n_id_pkp=fields.Boolean(string="IDPKP",compute='_compute_l10n_id_pkp',store=True,readonly=False)
    l10n_id_nik=fields.Char(string='NIK')
    l10n_id_tax_address=fields.Char('TaxAddress')
    l10n_id_tax_name=fields.Char('TaxName')
    l10n_id_kode_transaksi=fields.Selection([
            ('01','01KepadaPihakyangBukanPemungutPPN(CustomerBiasa)'),
            ('02','02KepadaPemungutBendaharawan(DinasKepemerintahan)'),
            ('03','03KepadaPemungutSelainBendaharawan(BUMN)'),
            ('04','04DPPNilaiLain(PPN1%)'),
            ('05','05BesaranTertentu'),
            ('06','06PenyerahanLainnya(TurisAsing)'),
            ('07','07PenyerahanyangPPN-nyaTidakDipungut(KawasanEkonomiKhusus/Batam)'),
            ('08','08PenyerahanyangPPN-nyaDibebaskan(ImporBarangTertentu)'),
            ('09','09PenyerahanAktiva(Pasal16DUUPPN)'),
        ],string='KodeTransaksi',help='Duadigitpertamanomorpajak')

    @api.depends('vat','country_code')
    def_compute_l10n_id_pkp(self):
        forrecordinself:
            record.l10n_id_pkp=record.vatandrecord.country_code=='ID'


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    l10n_id_tax_address=fields.Char('TaxAddress',related='company_id.partner_id.l10n_id_tax_address',readonly=False)
    l10n_id_tax_name=fields.Char('TaxName',related='company_id.partner_id.l10n_id_tax_address',readonly=False)
