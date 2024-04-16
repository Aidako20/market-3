#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_


classUoM(models.Model):
    _inherit='uom.uom'

    @api.onchange('rounding')
    def_onchange_rounding(self):
        precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
        ifself.rounding<1.0/10.0**precision:
            return{'warning':{
                'title':_('Warning!'),
                'message':_(
                    "ThisroundingprecisionishigherthantheDecimalAccuracy"
                    "(%sdigits).\nThismaycauseinconsistenciesincomputations.\n"
                    "Pleasesetaprecisionbetween%sand1."
                )%(precision,1.0/10.0**precision),
            }}
