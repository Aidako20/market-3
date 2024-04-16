#-*-coding:ascii-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models
fromflectra.addons.http_routing.models.ir_httpimportslug,unslug_url


classIrUiView(models.Model):
    _inherit=["ir.ui.view"]

    @api.model
    def_prepare_qcontext(self):
        qcontext=super(IrUiView,self)._prepare_qcontext()
        qcontext['slug']=slug
        qcontext['unslug_url']=unslug_url
        returnqcontext
