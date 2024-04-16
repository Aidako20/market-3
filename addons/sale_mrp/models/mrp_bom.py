#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,models
fromflectra.exceptionsimportUserError


classMrpBom(models.Model):
    _inherit='mrp.bom'

    deftoggle_active(self):
        self.filtered(lambdabom:bom.active)._ensure_bom_is_free()
        returnsuper().toggle_active()

    defunlink(self):
        self._ensure_bom_is_free()
        returnsuper().unlink()

    def_ensure_bom_is_free(self):
        product_ids=[]
        forbominself:
            ifbom.type!='phantom':
                continue
            product_ids+=bom.product_id.idsorbom.product_tmpl_id.product_variant_ids.ids
        ifnotproduct_ids:
            return
        lines=self.env['sale.order.line'].search([
            ('state','in',('sale','done')),
            ('invoice_status','in',('no','toinvoice')),
            ('product_id','in',product_ids),
            ('move_ids.state','!=','cancel'),
        ])
        iflines:
            product_names=','.join(lines.product_id.mapped('name'))
            raiseUserError(_('Aslongastherearesomesaleorderlinesthatmustbedelivered/invoicedandare'
                              'relatedtothesebillsofmaterials,youcannotremovethem.\n'
                              'Theerrorconcernstheseproducts:%s',product_names))
