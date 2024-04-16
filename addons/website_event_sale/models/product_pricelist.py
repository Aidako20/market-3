#-*-coding:utf-8-*-

fromflectraimport_,api,models

classPricelistItem(models.Model):
    _inherit="product.pricelist.item"

    @api.onchange('applied_on','product_id','product_tmpl_id','min_quantity')
    def_onchange_event_sale_warning(self):
        ifself.min_quantity>0:
            msg=''
            ifself.applied_on=='3_global'orself.applied_on=='2_product_category':
                msg=_("Apricelistitemwithapositivemin.quantitywillnotbeappliedtotheeventticketsproducts.")
            elif((self.applied_on=='1_product'andself.product_tmpl_id.event_ok)or
                    (self.applied_on=='0_product_variant'andself.product_id.event_ok)):
                msg=_("Apricelistitemwithapositivemin.quantitycannotbeappliedtothiseventticketsproduct.")
            ifmsg:
                return{'warning':
                    {
                        'title':_("Warning"),
                        'message':msg
                    }
                }
