#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api


classProductPackaging(models.Model):
    _inherit='product.packaging'


    def_get_default_length_uom(self):
        #TODOmasterdelete
        returnself.env['product.template']._get_length_uom_name_from_ir_config_parameter()

    def_get_default_weight_uom(self):
        returnself.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    height=fields.Integer('Height')
    width=fields.Integer('Width')
    packaging_length=fields.Integer('Length')
    max_weight=fields.Float('MaxWeight',help='Maximumweightshippableinthispackaging')
    shipper_package_code=fields.Char('PackageCode')
    package_carrier_type=fields.Selection([('none','Nocarrierintegration')],string='Carrier',default='none')
    weight_uom_name=fields.Char(string='Weightunitofmeasurelabel',compute='_compute_weight_uom_name',default=_get_default_weight_uom)
    length_uom_name=fields.Char(string='Lengthunitofmeasurelabel',compute='_compute_length_uom_name')

    _sql_constraints=[
        ('positive_height','CHECK(height>=0)','Heightmustbepositive'),
        ('positive_width','CHECK(width>=0)','Widthmustbepositive'),
        ('positive_length','CHECK(packaging_length>=0)','Lengthmustbepositive'),
        ('positive_max_weight','CHECK(max_weight>=0.0)','MaxWeightmustbepositive'),
    ]

    @api.onchange('package_carrier_type')
    def_onchange_carrier_type(self):
        carrier_id=self.env['delivery.carrier'].search([('delivery_type','=',self.package_carrier_type)],limit=1)
        ifcarrier_id:
            self.shipper_package_code=carrier_id._get_default_custom_package_code()
        else:
            self.shipper_package_code=False


    def_compute_length_uom_name(self):
        #FIXMEThisvariabledoesnotimpactanylogic,itisonlyusedforthepackagingdisplayontheformview.
        # However,itgeneratessomeconfusionfortheuserssincethisUoMwillbeignoredwhensendingtherequests
        # tothecarrierserver:thedimensionswillbeexpressedwithanotherUoMandtherewon'tbeanyconversion.
        # Forinstance,withFedex,theUoMusedwiththepackagedimensionswilldependontheUoMof
        # `fedex_weight_unit`.WithUPS,wewillusetheUoMdefinedon`ups_package_dimension_unit`
        self.length_uom_name=""

    def_compute_weight_uom_name(self):
        forpackaginginself:
            packaging.weight_uom_name=self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()
