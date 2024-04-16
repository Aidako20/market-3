#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classCouponReport(models.AbstractModel):
    _name='report.coupon.report_coupon'
    _description='SalesCouponReport'

    @api.model
    def_get_report_values(self,docids,data=None):
        docs=self.env['coupon.coupon'].browse(docids)
        return{
            'doc_ids':docs.ids,
            'doc_model':'coupon.coupon',
            'data':data,
            'docs':docs,
        }
