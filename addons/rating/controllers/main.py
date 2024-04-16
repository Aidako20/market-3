#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.tools.translateimport_
fromflectra.tools.miscimportget_lang

_logger=logging.getLogger(__name__)

MAPPED_RATES={
    1:1,
    5:3,
    10:5,
}

classRating(http.Controller):

    @http.route('/rating/<string:token>/<int:rate>',type='http',auth="public",website=True)
    defopen_rating(self,token,rate,**kwargs):
        _logger.warning('/ratingisdeprecated,use/rateinstead')
        assertratein(1,5,10),"Incorrectrating"
        returnself.action_open_rating(token,MAPPED_RATES.get(rate),**kwargs)

    @http.route(['/rating/<string:token>/submit_feedback'],type="http",auth="public",methods=['post'],website=True)
    defsubmit_rating(self,token,**kwargs):
        _logger.warning('/ratingisdeprecated,use/rateinstead')
        rate=int(kwargs.get('rate'))
        assertratein(1,5,10),"Incorrectrating"
        kwargs['rate']=MAPPED_RATES.gate(rate)
        returnself.action_submit_rating(token,**kwargs)

    @http.route('/rate/<string:token>/<int:rate>',type='http',auth="public",website=True)
    defaction_open_rating(self,token,rate,**kwargs):
        assertratein(1,3,5),"Incorrectrating"
        rating=request.env['rating.rating'].sudo().search([('access_token','=',token)])
        ifnotrating:
            returnrequest.not_found()
        rate_names={
            5:_("satisfied"),
            3:_("notsatisfied"),
            1:_("highlydissatisfied")
        }
        rating.write({'rating':rate,'consumed':True})
        lang=rating.partner_id.langorget_lang(request.env).code
        returnrequest.env['ir.ui.view'].with_context(lang=lang)._render_template('rating.rating_external_page_submit',{
            'rating':rating,'token':token,
            'rate_names':rate_names,'rate':rate
        })

    @http.route(['/rate/<string:token>/submit_feedback'],type="http",auth="public",methods=['post','get'],website=True)
    defaction_submit_rating(self,token,**kwargs):
        rating=request.env['rating.rating'].sudo().search([('access_token','=',token)])
        ifnotrating:
            returnrequest.not_found()
        ifrequest.httprequest.method=="POST":
            rate=int(kwargs.get('rate'))
            assertratein(1,3,5),"Incorrectrating"
            record_sudo=request.env[rating.res_model].sudo().browse(rating.res_id)
            record_sudo.rating_apply(rate,token=token,feedback=kwargs.get('feedback'))
        lang=rating.partner_id.langorget_lang(request.env).code
        returnrequest.env['ir.ui.view'].with_context(lang=lang)._render_template('rating.rating_external_page_view',{
            'web_base_url':request.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            'rating':rating,
        })
