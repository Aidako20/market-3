#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_
fromflectra.exceptionsimportValidationError


classCouponProgram(models.Model):
    _name='coupon.program'
    _inherit=['coupon.program','website.multi.mixin']

    @api.constrains('promo_code','website_id')
    def_check_promo_code_constraint(self):
        """Onlycasewheremultiplesamecodecouldcoexistsisiftheyallbelongtotheirownwebsite.
            Iftheprogramiswebsitegeneric,weshouldensurethereisnogenericandnospecific(evenforotherwebsite)already
            Iftheprogramiswebsitespecific,weshouldensurethereisnoexistingcodeforthiswebsiteorFalse
        """
        forprograminself.filtered(lambdap:p.promo_code):
            domain=[('id','!=',program.id),('promo_code','=',program.promo_code)]
            ifprogram.website_id:
                domain+=program.website_id.website_domain()
            ifself.search(domain):
                raiseValidationError(_('Theprogramcodemustbeuniquebywebsite!'))

    def_filter_programs_on_website(self,order):
        returnself.filtered(lambdaprogram:notprogram.website_idorprogram.website_id.id==order.website_id.id)

    @api.model
    def_filter_programs_from_common_rules(self,order,next_order=False):
        programs=self._filter_programs_on_website(order)
        returnsuper(CouponProgram,programs)._filter_programs_from_common_rules(order,next_order)

    def_check_promo_code(self,order,coupon_code):
        ifself.website_idandself.website_id!=order.website_id:
            return{'error':'Thispromocodeisnotvalidonthiswebsite.'}
        returnsuper()._check_promo_code(order,coupon_code)
