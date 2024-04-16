#-*-coding:utf-8-*-

fromflectraimporthttp
fromflectra.addons.http_routing.models.ir_httpimportunslug
fromflectra.httpimportrequest


classWebsitePartnerPage(http.Controller):

    #DonotusesemanticcontrollerduetoSUPERUSER_ID
    @http.route(['/partners/<partner_id>'],type='http',auth="public",website=True)
    defpartners_detail(self,partner_id,**post):
        _,partner_id=unslug(partner_id)
        ifpartner_id:
            partner_sudo=request.env['res.partner'].sudo().browse(partner_id)
            is_website_publisher=request.env['res.users'].has_group('website.group_website_publisher')
            ifpartner_sudo.exists()and(partner_sudo.website_publishedoris_website_publisher):
                values={
                    'main_object':partner_sudo,
                    'partner':partner_sudo,
                    'edit_page':False
                }
                returnrequest.render("website_partner.partner_page",values)
        returnrequest.not_found()
