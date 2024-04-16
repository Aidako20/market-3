#-*-coding:utf-8-*-	
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.	

fromflectraimportfields,models	


classResConfigSettings(models.TransientModel):	
    _inherit='res.config.settings'	

    snailmail_color=fields.Boolean(string='PrintInColor',related='company_id.snailmail_color',readonly=False)
    snailmail_cover=fields.Boolean(string='AddaCoverPage',related='company_id.snailmail_cover',readonly=False)
    snailmail_duplex=fields.Boolean(string='PrintBothsides',related='company_id.snailmail_duplex',readonly=False)
