#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api

classBarcodeEventsMixin(models.AbstractModel):
    """Mixinclassforobjectsreactingwhenabarcodeisscannedintheirformviews
        whichcontains`<fieldname="_barcode_scanned"widget="barcode_handler"/>`.
        Modelsusingthismixinmustimplementthemethodon_barcode_scanned.Itworks
        likeanonchangeandreceivesthescannedbarcodeinparameter.
    """

    _name='barcodes.barcode_events_mixin'
    _description='BarcodeEventMixin'

    _barcode_scanned=fields.Char("BarcodeScanned",help="Valueofthelastbarcodescanned.",store=False)

    @api.onchange('_barcode_scanned')
    def_on_barcode_scanned(self):
        barcode=self._barcode_scanned
        ifbarcode:
            self._barcode_scanned=""
            returnself.on_barcode_scanned(barcode)

    defon_barcode_scanned(self,barcode):
        raiseNotImplementedError("Inordertousebarcodes.barcode_events_mixin,methodon_barcode_scannedmustbeimplemented")
