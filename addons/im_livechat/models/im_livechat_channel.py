#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64
importrandom
importre

fromflectraimportapi,fields,models,modules,_


classImLivechatChannel(models.Model):
    """LivechatChannel
        Defineacommunicationchannel,whichcanbeaccessedwith'script_external'(scripttagtoputon
        externalwebsite),'script_internal'(codetobeintegratedwithflectrawebsite)orvia'web_page'link.
        Itprovidesratingtools,andaccessrulesforanonymouspeople.
    """

    _name='im_livechat.channel'
    _inherit=['rating.parent.mixin']
    _description='LivechatChannel'
    _rating_satisfaction_days=7 #includeonlylast7daystocomputesatisfaction

    def_default_image(self):
        image_path=modules.get_module_resource('im_livechat','static/src/img','default.png')
        returnbase64.b64encode(open(image_path,'rb').read())

    def_default_user_ids(self):
        return[(6,0,[self._uid])]

    #attributefields
    name=fields.Char('Name',required=True,help="Thenameofthechannel")
    button_text=fields.Char('TextoftheButton',default='HaveaQuestion?Chatwithus.',
        help="DefaulttextdisplayedontheLivechatSupportButton",translate=True)
    default_message=fields.Char('WelcomeMessage',default='HowmayIhelpyou?',
        help="Thisisanautomated'welcome'messagethatyourvisitorwillseewhentheyinitiateanewconversation.",
        translate=True)
    input_placeholder=fields.Char('ChatInputPlaceholder',help='Textthatpromptstheusertoinitiatethechat.',translate=True)
    header_background_color=fields.Char(default="#009EFB",help="Defaultbackgroundcolorofthechannelheaderonceopen")
    title_color=fields.Char(default="#FFFFFF",help="Defaulttitlecolorofthechannelonceopen")
    button_background_color=fields.Char(default="#878787",help="DefaultbackgroundcoloroftheLivechatbutton")
    button_text_color=fields.Char(default="#FFFFFF",help="DefaulttextcoloroftheLivechatbutton")

    #computedfields
    web_page=fields.Char('WebPage',compute='_compute_web_page_link',store=False,readonly=True,
        help="URLtoastaticpagewhereyouclientcandiscusswiththeoperatorofthechannel.")
    are_you_inside=fields.Boolean(string='Areyouinsidethematrix?',
        compute='_are_you_inside',store=False,readonly=True)
    script_external=fields.Text('Script(external)',compute='_compute_script_external',store=False,readonly=True)
    nbr_channel=fields.Integer('Numberofconversation',compute='_compute_nbr_channel',store=False,readonly=True)

    image_128=fields.Image("Image",max_width=128,max_height=128,default=_default_image)

    #relationnalfields
    user_ids=fields.Many2many('res.users','im_livechat_channel_im_user','channel_id','user_id',string='Operators',default=_default_user_ids)
    channel_ids=fields.One2many('mail.channel','livechat_channel_id','Sessions')
    rule_ids=fields.One2many('im_livechat.channel.rule','channel_id','Rules')

    def_are_you_inside(self):
        forchannelinself:
            channel.are_you_inside=bool(self.env.uidin[u.idforuinchannel.user_ids])

    def_compute_script_external(self):
        view=self.env['ir.model.data'].get_object('im_livechat','external_loader')
        values={
            "url":self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            "dbname":self._cr.dbname,
        }
        forrecordinself:
            values["channel_id"]=record.id
            record.script_external=view._render(values)ifrecord.idelseFalse

    def_compute_web_page_link(self):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        forrecordinself:
            record.web_page="%s/im_livechat/support/%i"%(base_url,record.id)ifrecord.idelseFalse

    @api.depends('channel_ids')
    def_compute_nbr_channel(self):
        data=self.env['mail.channel'].read_group([
            ('livechat_channel_id','in',self._ids),
            ('channel_message_ids','!=',False)],['__count'],['livechat_channel_id'],lazy=False)
        channel_count={x['livechat_channel_id'][0]:x['__count']forxindata}
        forrecordinself:
            record.nbr_channel=channel_count.get(record.id,0)

    #--------------------------
    #ActionMethods
    #--------------------------
    defaction_join(self):
        self.ensure_one()
        returnself.write({'user_ids':[(4,self._uid)]})

    defaction_quit(self):
        self.ensure_one()
        returnself.write({'user_ids':[(3,self._uid)]})

    defaction_view_rating(self):
        """Actiontodisplaytheratingrelativetothechannel,soallratingofthe
            sessionsofthecurrentchannel
            :returns:their.action'action_view_rating'withthecorrectdomain
        """
        self.ensure_one()
        action=self.env['ir.actions.act_window']._for_xml_id('im_livechat.rating_rating_action_view_livechat_rating')
        action['domain']=[('parent_res_id','=',self.id),('parent_res_model','=','im_livechat.channel')]
        returnaction

    #--------------------------
    #ChannelMethods
    #--------------------------
    def_get_available_users(self):
        """getavailableuserofagivenchannel
            :retuns:returntheres.usershavingtheirim_statusonline
        """
        self.ensure_one()
        returnself.user_ids.filtered(lambdauser:user.im_status=='online')

    def_get_livechat_mail_channel_vals(self,anonymous_name,operator,user_id=None,country_id=None):
        #partnertoaddtothemail.channel
        operator_partner_id=operator.partner_id.id
        channel_partner_to_add=[(4,operator_partner_id)]
        visitor_user=False
        ifuser_id:
            visitor_user=self.env['res.users'].browse(user_id)
            ifvisitor_userandvisitor_user.active: #validsessionuser(notpublic)
                channel_partner_to_add.append((4,visitor_user.partner_id.id))
        return{
            'channel_partner_ids':channel_partner_to_add,
            'livechat_active':True,
            'livechat_operator_id':operator_partner_id,
            'livechat_channel_id':self.id,
            'anonymous_name':Falseifuser_idelseanonymous_name,
            'country_id':country_id,
            'channel_type':'livechat',
            'name':''.join([visitor_user.display_nameifvisitor_userelseanonymous_name,operator.livechat_usernameifoperator.livechat_usernameelseoperator.name]),
            'public':'private',
            'email_send':False,
        }

    def_open_livechat_mail_channel(self,anonymous_name,previous_operator_id=None,user_id=None,country_id=None):
        """Returnamail.channelgivenalivechatchannel.Itcreatesonewithaconnectedoperator,orreturnfalseotherwise
            :paramanonymous_name:thenameoftheanonymouspersonofthechannel
            :paramprevious_operator_id:partner_id.idofthepreviousoperatorthatthisvisitorhadinthepast
            :paramuser_id:theidoftheloggedinvisitor,ifany
            :paramcountry_code:thecountryoftheanonymouspersonofthechannel
            :typeanonymous_name:str
            :return:channelheader
            :rtype:dict

            Ifthisvisitoralreadyhadanoperatorwithinthelast7days(informationstoredwiththe'im_livechat_previous_operator_pid'cookie),
            thesystemwillfirsttrytoassignthatoperatorifhe'savailable(toimproveuserexperience).
        """
        self.ensure_one()
        operator=False
        ifprevious_operator_id:
            available_users=self._get_available_users()
            #previous_operator_idisthepartner_idofthepreviousoperator,needtoconverttouser
            ifprevious_operator_idinavailable_users.mapped('partner_id').ids:
                operator=next(available_userforavailable_userinavailable_usersifavailable_user.partner_id.id==previous_operator_id)
        ifnotoperator:
            operator=self._get_random_operator()
        ifnotoperator:
            #nooneavailable
            returnFalse

        #createthesession,andaddthelinkwiththegivenchannel
        mail_channel_vals=self._get_livechat_mail_channel_vals(anonymous_name,operator,user_id=user_id,country_id=country_id)
        mail_channel=self.env["mail.channel"].with_context(mail_create_nosubscribe=False).sudo().create(mail_channel_vals)
        mail_channel._broadcast([operator.partner_id.id])
        returnmail_channel.sudo().channel_info()[0]

    def_get_random_operator(self):
        """Returnarandomoperatorfromtheavailableusersofthechannelthathavethelowestnumberofactivelivechats.
        Alivechatisconsidered'active'ifithasatleastonemessagewithinthe30minutes.

        (Someannoyingconversionshavetobemadeontheflybecausethismodelholds'res.users'asavailableoperators
        andthemail_channelmodelstoresthepartner_idoftherandomlyselectedoperator)

        :return:user
        :rtype:res.users
        """
        operators=self._get_available_users()
        iflen(operators)==0:
            returnFalse

        self.env.cr.execute("""SELECTCOUNT(DISTINCTc.id),c.livechat_operator_id
            FROMmail_channelc
            LEFTOUTERJOINmail_message_mail_channel_relrONc.id=r.mail_channel_id
            LEFTOUTERJOINmail_messagemONr.mail_message_id=m.id
            WHEREc.channel_type='livechat'
            ANDc.livechat_operator_idin%s
            ANDm.create_date>((now()attimezone'UTC')-interval'30minutes')
            GROUPBYc.livechat_operator_id
            ORDERBYCOUNT(DISTINCTc.id)asc""",(tuple(operators.mapped('partner_id').ids),))
        active_channels=self.env.cr.dictfetchall()

        #Ifinactiveoperator(s),returnoneofthem
        active_channel_operator_ids=[active_channel['livechat_operator_id']foractive_channelinactive_channels]
        inactive_operators=[operatorforoperatorinoperatorsifoperator.partner_id.idnotinactive_channel_operator_ids]
        ifinactive_operators:
            returnrandom.choice(inactive_operators)

        #Ifnoinactiveoperator,active_channelsisnotemptyaslen(operators)>0(seeabove).
        #Getthelessactiveoperatorusingtheactive_channelsfirstelement'scount(sincetheyaresorted'ascending')
        lowest_number_of_conversations=active_channels[0]['count']
        less_active_operator=random.choice([
            active_channel['livechat_operator_id']foractive_channelinactive_channels
            ifactive_channel['count']==lowest_number_of_conversations])

        #converttheselected'partner_id'toitscorrespondingres.users
        returnnext(operatorforoperatorinoperatorsifoperator.partner_id.id==less_active_operator)

    def_get_channel_infos(self):
        self.ensure_one()

        return{
            'header_background_color':self.header_background_color,
            'button_background_color':self.button_background_color,
            'title_color':self.title_color,
            'button_text_color':self.button_text_color,
            'button_text':self.button_text,
            'input_placeholder':self.input_placeholder,
            'default_message':self.default_message,
            "channel_name":self.name,
            "channel_id":self.id,
        }

    defget_livechat_info(self,username='Visitor'):
        self.ensure_one()

        ifusername=='Visitor':
            username=_('Visitor')
        info={}
        info['available']=len(self._get_available_users())>0
        info['server_url']=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        ifinfo['available']:
            info['options']=self._get_channel_infos()
            info['options']['current_partner_id']=self.env.user.partner_id.id
            info['options']["default_username"]=username
        returninfo


classImLivechatChannelRule(models.Model):
    """ChannelRules
        Rulesdefiningaccesstothechannel(countries,andurlmatching).Italsoprovidethe'autopop'
        optiontoopenautomaticallytheconversation.
    """

    _name='im_livechat.channel.rule'
    _description='LivechatChannelRules'
    _order='sequenceasc'

    regex_url=fields.Char('URLRegex',
        help="Regularexpressionspecifyingthewebpagesthisrulewillbeappliedon.")
    action=fields.Selection([('display_button','Displaythebutton'),('auto_popup','Autopopup'),('hide_button','Hidethebutton')],
        string='Action',required=True,default='display_button',
        help="*'Displaythebutton'displaysthechatbuttononthepages.\n"\
             "*'Autopopup'displaysthebuttonandautomaticallyopentheconversationpane.\n"\
             "*'Hidethebutton'hidesthechatbuttononthepages.")
    auto_popup_timer=fields.Integer('Autopopuptimer',default=0,
        help="Delay(inseconds)toautomaticallyopentheconversationwindow.Note:theselectedactionmustbe'Autopopup'otherwisethisparameterwillnotbetakenintoaccount.")
    channel_id=fields.Many2one('im_livechat.channel','Channel',
        help="Thechanneloftherule")
    country_ids=fields.Many2many('res.country','im_livechat_channel_country_rel','channel_id','country_id','Country',
        help="Therulewillonlybeappliedforthesecountries.Example:ifyouselect'Belgium'and'UnitedStates'andthatyousettheactionto'HideButton',thechatbuttonwillbehiddenonthespecifiedURLfromthevisitorslocatedinthese2countries.ThisfeaturerequiresGeoIPinstalledonyourserver.")
    sequence=fields.Integer('Matchingorder',default=10,
        help="Giventheordertofindamatchingrule.If2rulesarematchingforthegivenurl/country,theonewiththelowestsequencewillbechosen.")

    defmatch_rule(self,channel_id,url,country_id=False):
        """determineifaruleofthegivenchannelmatcheswiththegivenurl
            :paramchannel_id:theidentifierofthechannel_id
            :paramurl:theurltomatchwitharule
            :paramcountry_id:theidentifierofthecountry
            :returnstherulethatmatchesthegivencondition.Falseotherwise.
            :rtype:im_livechat.channel.rule
        """
        def_match(rules):
            forruleinrules:
                #urlmightnotbesetbecauseitcomesfromreferer,inthat
                #casematchthefirstrulewithnoregex_url
                ifre.search(rule.regex_urlor'',urlor''):
                    returnrule
            returnFalse
        #first,searchthecountryspecificrules(thefirstmatchisreturned)
        ifcountry_id:#don'tincludethecountryintheresearchifgeoIPisnotinstalled
            domain=[('country_ids','in',[country_id]),('channel_id','=',channel_id)]
            rule=_match(self.search(domain))
            ifrule:
                returnrule
        #second,fallbackontheruleswithoutcountry
        domain=[('country_ids','=',False),('channel_id','=',channel_id)]
        return_match(self.search(domain))
