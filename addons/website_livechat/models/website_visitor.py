#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta
importjson

fromflectraimportmodels,api,fields,_
fromflectra.exceptionsimportUserError
fromflectra.httpimportrequest
fromflectra.tools.sqlimportcolumn_exists,create_column


classWebsiteVisitor(models.Model):
    _inherit='website.visitor'

    livechat_operator_id=fields.Many2one('res.partner',compute='_compute_livechat_operator_id',store=True,string='Speakingwith')
    livechat_operator_name=fields.Char('OperatorName',related="livechat_operator_id.name")
    mail_channel_ids=fields.One2many('mail.channel','livechat_visitor_id',
                                       string="Visitor'slivechatchannels",readonly=True)
    session_count=fields.Integer('#Sessions',compute="_compute_session_count")

    def_auto_init(self):
        #Skipthecomputationofthefield`livechat_operator_id`atthemoduleinstallation
        #Wecanassumenolivechatoperatorattributedtovisitorifitwasnotinstalled
        ifnotcolumn_exists(self.env.cr,"website_visitor","livechat_operator_id"):
            create_column(self.env.cr,"website_visitor","livechat_operator_id","int4")

        returnsuper()._auto_init()

    @api.depends('mail_channel_ids.livechat_active','mail_channel_ids.livechat_operator_id')
    def_compute_livechat_operator_id(self):
        results=self.env['mail.channel'].search_read(
            [('livechat_visitor_id','in',self.ids),('livechat_active','=',True)],
            ['livechat_visitor_id','livechat_operator_id']
        )
        visitor_operator_map={int(result['livechat_visitor_id'][0]):int(result['livechat_operator_id'][0])forresultinresults}
        forvisitorinself:
            visitor.livechat_operator_id=visitor_operator_map.get(visitor.id,False)

    @api.depends('mail_channel_ids')
    def_compute_session_count(self):
        sessions=self.env['mail.channel'].search([('livechat_visitor_id','in',self.ids)])
        session_count=dict.fromkeys(self.ids,0)
        forsessioninsessions.filtered(lambdac:c.channel_message_ids):
            session_count[session.livechat_visitor_id.id]+=1
        forvisitorinself:
            visitor.session_count=session_count.get(visitor.id,0)

    defaction_send_chat_request(self):
        """Sendachatrequesttowebsite_visitor(s).
        Thiscreatesachat_requestandamail_channelwithlivechatactiveflag.
        Butforthevisitortogetthechatrequest,theoperatorstillhastospeaktothevisitor.
        Thevisitorwillreceivethechatrequestthenexttimehenavigatestoawebsitepage.
        (see_handle_webpage_dispatchfornextstep)"""
        #checkifvisitorisavailable
        unavailable_visitors_count=self.env['mail.channel'].search_count([('livechat_visitor_id','in',self.ids),('livechat_active','=',True)])
        ifunavailable_visitors_count:
            raiseUserError(_('Recipientsarenotavailable.Pleaserefreshthepagetogetlatestvisitorsstatus.'))
        #checkifuserisavailableasoperator
        forwebsiteinself.mapped('website_id'):
            ifnotwebsite.channel_id:
                raiseUserError(_('NoLivechatChannelallowsyoutosendachatrequestforwebsite%s.',website.name))
        self.website_id.channel_id.write({'user_ids':[(4,self.env.user.id)]})
        #Createchat_requestsandlinkedmail_channels
        mail_channel_vals_list=[]
        forvisitorinself:
            operator=self.env.user
            country=visitor.country_id
            visitor_name="%s(%s)"%(visitor.display_name,country.name)ifcountryelsevisitor.display_name
            channel_partner_to_add=[(4,operator.partner_id.id)]
            ifvisitor.partner_id:
                channel_partner_to_add.append((4,visitor.partner_id.id))
            else:
                channel_partner_to_add.append((4,self.env.ref('base.public_partner').id))
            mail_channel_vals_list.append({
                'channel_partner_ids':channel_partner_to_add,
                'livechat_channel_id':visitor.website_id.channel_id.id,
                'livechat_operator_id':self.env.user.partner_id.id,
                'channel_type':'livechat',
                'public':'private',
                'email_send':False,
                'country_id':country.id,
                'anonymous_name':visitor_name,
                'name':','.join([visitor_name,operator.livechat_usernameifoperator.livechat_usernameelseoperator.name]),
                'livechat_visitor_id':visitor.id,
                'livechat_active':True,
            })
        ifmail_channel_vals_list:
            mail_channels=self.env['mail.channel'].create(mail_channel_vals_list)
            #Openemptychattertoallowtheoperatortostartchattingwiththevisitor.
            values={
                'fold_state':'open',
                'is_minimized':True,
            }
            mail_channels_uuid=mail_channels.mapped('uuid')
            domain=[('partner_id','=',self.env.user.partner_id.id),('channel_id.uuid','in',mail_channels_uuid)]
            channel_partners=self.env['mail.channel.partner'].search(domain)
            channel_partners.write(values)
            mail_channels_info=mail_channels.channel_info('send_chat_request')
            notifications=[]
            formail_channel_infoinmail_channels_info:
                notifications.append([(self._cr.dbname,'res.partner',operator.partner_id.id),mail_channel_info])
            self.env['bus.bus'].sendmany(notifications)

    def_link_to_visitor(self,target,keep_unique=True):
        """Copysessionsofthesecondaryvisitorstothemainpartnervisitor."""
        iftarget.partner_id:
            target.mail_channel_ids|=self.mail_channel_ids
        super(WebsiteVisitor,self)._link_to_visitor(target,keep_unique=keep_unique)

    def_link_to_partner(self,partner,update_values=None):
        """Adaptpartnerinmembersofrelatedlivechats"""
        ifpartner:
            self.mail_channel_ids.channel_partner_ids=[
                (3,self.env.ref('base.public_partner').id),
                (4,partner.id),
            ]
        super(WebsiteVisitor,self)._link_to_partner(partner,update_values=update_values)

    def_create_visitor(self):
        visitor=super(WebsiteVisitor,self)._create_visitor()
        mail_channel_uuid=json.loads(request.httprequest.cookies.get('im_livechat_session','{}')).get('uuid')
        ifmail_channel_uuid:
            mail_channel=request.env["mail.channel"].sudo().search([("uuid","=",mail_channel_uuid)])
            mail_channel.write({
                'livechat_visitor_id':visitor.id,
                'anonymous_name':visitor.display_name
            })
        returnvisitor
