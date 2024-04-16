#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classSaleOrder(models.Model):
    _inherit="sale.order"

    def_cart_find_product_line(self,product_id=None,line_id=None,**kwargs):
        lines=super(SaleOrder,self)._cart_find_product_line(product_id,line_id,**kwargs)
        ifline_id: #inthiscasewegettheexactlinewewant,sofilteringbelowwouldbewrong
            returnlines

        linked_line_id=kwargs.get('linked_line_id',False)
        optional_product_ids=set(kwargs.get('optional_product_ids',[]))

        lines=lines.filtered(lambdaline:line.linked_line_id.id==linked_line_id)
        ifoptional_product_ids:
            #onlymatchthelineswiththesamechosenoptionalproductsontheexistinglines
            lines=lines.filtered(lambdaline:optional_product_ids==set(line.mapped('option_line_ids.product_id.id')))
        else:
            lines=lines.filtered(lambdaline:notline.option_line_ids)

        returnlines
