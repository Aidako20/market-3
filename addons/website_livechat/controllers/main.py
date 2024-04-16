#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp,_
fromflectra.httpimportrequest
fromflectra.addons.im_livechat.controllers.mainimportLivechatController


classWebsiteLivechat(LivechatController):

    @http.route('/livechat',type='http',auth="public",website=True,sitemap=True)
    defchannel_list(self,**kw):
        #displaythelistofthechannel
        channels=request.env['im_livechat.channel'].search([('website_published','=',True)])
        values={
            'channels':channels
        }
        returnrequest.render('website_livechat.channel_list_page',values)

    @http.route('/livechat/channel/<model("im_livechat.channel"):channel>',type='http',auth='public',website=True,sitemap=True)
    defchannel_rating(self,channel,**kw):
        #getthelast100ratingsandtherepartitionpergrade
        domain=[
            ('res_model','=','mail.channel'),('res_id','in',channel.sudo().channel_ids.ids),
            ('consumed','=',True),('rating','>=',1),
        ]
        ratings=request.env['rating.rating'].sudo().search(domain,order='create_datedesc',limit=100)
        repartition=channel.sudo().channel_ids.rating_get_grades(domain=domain)

        #computepercentage
        percentage=dict.fromkeys(['great','okay','bad'],0)
        forgradeinrepartition:
            percentage[grade]=round(repartition[grade]*100.0/sum(repartition.values()),1)ifsum(repartition.values())else0

        #filteronlyontheteamusersthatworkedonthelast100ratingsandgettheirdetailedstat
        ratings_per_partner={partner_id:dict(great=0,okay=0,bad=0)
                               forpartner_idinratings.mapped('rated_partner_id.id')}
        total_ratings_per_partner=dict.fromkeys(ratings.mapped('rated_partner_id.id'),0)
        #keep10forbackwardcompatibility
        rating_texts={10:'great',5:'great',3:'okay',1:'bad'}

        forratinginratings:
            partner_id=rating.rated_partner_id.id
            ratings_per_partner[partner_id][rating_texts[rating.rating]]+=1
            total_ratings_per_partner[partner_id]+=1

        forpartner_id,ratinginratings_per_partner.items():
            fork,vinratings_per_partner[partner_id].items():
                ratings_per_partner[partner_id][k]=round(100*v/total_ratings_per_partner[partner_id],1)

        #thevaluedicttorenderthetemplate
        values={
            'main_object':channel,
            'channel':channel,
            'ratings':ratings,
            'team':channel.sudo().user_ids,
            'percentage':percentage,
            'ratings_per_user':ratings_per_partner
        }
        returnrequest.render("website_livechat.channel_page",values)

    @http.route('/im_livechat/get_session',type="json",auth='public',cors="*")
    defget_session(self,channel_id,anonymous_name,previous_operator_id=None,**kwargs):
        """Overridetousevisitornameinsteadof'Visitor'wheneveravisitorstartalivechatsession."""
        visitor_sudo=request.env['website.visitor']._get_visitor_from_request()
        ifvisitor_sudo:
            anonymous_name=visitor_sudo.with_context(lang=visitor_sudo.lang_id.code).display_name
        returnsuper(WebsiteLivechat,self).get_session(channel_id,anonymous_name,previous_operator_id=previous_operator_id,**kwargs)
