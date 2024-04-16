#-*-coding:utf-8-*-

fromflectraimportmodels,fields


classResCompany(models.Model):
    _inherit='res.company'

    def_get_default_nomenclature(self):
        returnself.env.ref('barcodes.default_barcode_nomenclature',raise_if_not_found=False)

    nomenclature_id=fields.Many2one(
        'barcode.nomenclature',
        string="Nomenclature",
        default=_get_default_nomenclature,
    )
