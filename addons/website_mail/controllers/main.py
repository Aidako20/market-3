#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimporthttp
fromflectra.httpimportrequest


classWebsiteMail(http.Controller):

    @http.route(['/website_mail/follow'],type='json',auth="public",website=True)
    defwebsite_message_subscribe(self,id=0,object=None,message_is_follower="on",email=False,**post):
        #TDEFIXME:checkthismethodwithnewfollowers
        res_id=int(id)
        is_follower=message_is_follower=='on'
        record=request.env[object].browse(res_id).exists()
        ifnotrecord:
            returnFalse

        record.check_access_rights('read')
        record.check_access_rule('read')

        #searchpartner_id
        ifrequest.env.user!=request.website.user_id:
            partner_ids=request.env.user.partner_id.ids
        else:
            #mail_threadmethod
            partner_ids=[p.idforpinrequest.env['mail.thread'].sudo()._mail_find_partner_from_emails([email],records=record.sudo())ifp]
            ifnotpartner_idsornotpartner_ids[0]:
                name=email.split('@')[0]
                partner_ids=request.env['res.partner'].sudo().create({'name':name,'email':email}).ids
        #addorremovefollower
        ifis_follower:
            record.sudo().message_unsubscribe(partner_ids)
            returnFalse
        else:
            #addpartnertosession
            request.session['partner_id']=partner_ids[0]
            record.sudo().message_subscribe(partner_ids)
            returnTrue

    @http.route(['/website_mail/is_follower'],type='json',auth="public",website=True)
    defis_follower(self,records,**post):
        """Givenalistof`models`containingalistofres_ids,return
            theres_idsforwhichtheuserisfollowerandsomepracticalinfo.

            :paramrecords:dictofmodelscontainingrecordIDS,eg:{
                    'res.model':[1,2,3..],
                    'res.model2':[1,2,3..],
                    ..
                }

            :returns:[
                    {'is_user':True/False,'email':'admin@yourcompany.example.com'},
                    {'res.model':[1,2],'res.model2':[1]}
                ]
        """
        user=request.env.user
        partner=None
        public_user=request.website.user_id
        ifuser!=public_user:
            partner=request.env.user.partner_id
        elifrequest.session.get('partner_id'):
            partner=request.env['res.partner'].sudo().browse(request.session.get('partner_id'))

        res={}
        ifpartner:
            formodelinrecords:
                mail_followers_ids=request.env['mail.followers'].sudo().read_group([
                    ('res_model','=',model),
                    ('res_id','in',records[model]),
                    ('partner_id','=',partner.id)
                ],['res_id','follow_count:count(id)'],['res_id'])
                #`read_group`willfilterouttheoneswithoutcountresult
                forminmail_followers_ids:
                    res.setdefault(model,[]).append(m['res_id'])

        return[{
            'is_user':user!=public_user,
            'email':partner.emailifpartnerelse"",
        },res]
