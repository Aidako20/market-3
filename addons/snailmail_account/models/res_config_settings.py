#-*-coding:utf-8-*-	
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.	

fromflectraimportfields,models	


classResConfigSettings(models.TransientModel):	
    _inherit='res.config.settings'	

    invoice_is_snailmail=fields.Boolean(string='SendbyPost',related='company_id.invoice_is_snailmail',readonly=False)
