#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,tools,_
fromflectra.exceptionsimportValidationError


classDecimalPrecision(models.Model):
    _inherit='decimal.precision'

    @api.constrains('digits')
    def_check_main_currency_rounding(self):
        ifany(precision.name=='Account'and
                tools.float_compare(self.env.company.currency_id.rounding,10**-precision.digits,precision_digits=6)==-1
                forprecisioninself):
            raiseValidationError(_("Youcannotdefinethedecimalprecisionof'Account'asgreaterthantheroundingfactorofthecompany'smaincurrency"))
        returnTrue

    @api.onchange('digits')
    def_onchange_digits(self):
        ifself.name!="ProductUnitofMeasure": #precision_get()reliesonthisname
            return
        #WearechangingtheprecisionofUOMfields;checkwhetherthe
        #precisionisequalorhigherthanexistingunitsofmeasure.
        rounding=1.0/10.0**self.digits
        dangerous_uom=self.env['uom.uom'].search([('rounding','<',rounding)])
        ifdangerous_uom:
            uom_descriptions=[
                "-%s(id=%s,precision=%s)"%(uom.name,uom.id,uom.rounding)
                foruomindangerous_uom
            ]
            return{'warning':{
                'title':_('Warning!'),
                'message':_(
                    "YouaresettingaDecimalAccuracylessprecisethantheUOMs:\n"
                    "%s\n"
                    "Thismaycauseinconsistenciesincomputations.\n"
                    "Pleaseincreasetheroundingofthoseunitsofmeasure,orthedigitsofthisDecimalAccuracy."
                 )%('\n'.join(uom_descriptions)),
            }}
