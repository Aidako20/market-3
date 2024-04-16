#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.addons.website.modelsimportir_http


classResPartner(models.Model):
    _inherit='res.partner'

    last_website_so_id=fields.Many2one('sale.order',compute='_compute_last_website_so_id',string='LastOnlineSalesOrder')

    def_compute_last_website_so_id(self):
        SaleOrder=self.env['sale.order']
        forpartnerinself:
            is_public=any(u._is_public()foruinpartner.with_context(active_test=False).user_ids)
            website=ir_http.get_request_website()
            ifwebsiteandnotis_public:
                partner.last_website_so_id=SaleOrder.search([
                    ('partner_id','=',partner.id),
                    ('website_id','=',website.id),
                    ('state','=','draft'),
                ],order='write_datedesc',limit=1)
            else:
                partner.last_website_so_id=SaleOrder #NotinawebsitecontextorpublicUser
