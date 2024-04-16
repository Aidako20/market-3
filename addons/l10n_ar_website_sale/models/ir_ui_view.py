#-*-coding:utf-8-*-
fromflectraimport_,api,models
fromflectra.exceptionsimportValidationError


classView(models.Model):
    _inherit='ir.ui.view'

    @api.constrains('active','key','website_id')
    def_check_active(self):
        forrecordinself:
            ifrecord.key=='website_sale.address_b2b'andrecord.website_id:
                ifrecord.website_id.company_id.country_id.code=="AR"andnotrecord.active:
                    raiseValidationError(_("B2BfieldsmustalwaysbedisplayedwithArgentinianwebsite."))
