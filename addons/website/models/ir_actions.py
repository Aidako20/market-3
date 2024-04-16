#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromwerkzeugimporturls

fromflectraimportapi,fields,models
fromflectra.httpimportrequest
fromflectra.tools.jsonimportscriptsafeasjson_scriptsafe


classServerAction(models.Model):
    """Addwebsiteoptioninserveractions."""

    _name='ir.actions.server'
    _inherit='ir.actions.server'

    xml_id=fields.Char('ExternalID',compute='_compute_xml_id',help="IDoftheactionifdefinedinaXMLfile")
    website_path=fields.Char('WebsitePath')
    website_url=fields.Char('WebsiteUrl',compute='_get_website_url',help='ThefullURLtoaccesstheserveractionthroughthewebsite.')
    website_published=fields.Boolean('AvailableontheWebsite',copy=False,
                                       help='Acodeserveractioncanbeexecutedfromthewebsite,usingadedicated'
                                            'controller.Theaddressis<base>/website/action/<website_path>.'
                                            'SetthisfieldasTruetoallowuserstorunthisaction.Ifit'
                                            'issettoFalsetheactioncannotberunthroughthewebsite.')

    def_compute_xml_id(self):
        res=self.get_external_id()
        foractioninself:
            action.xml_id=res.get(action.id)

    def_compute_website_url(self,website_path,xml_id):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        link=website_pathorxml_idor(self.idand'%d'%self.id)or''
        ifbase_urlandlink:
            path='%s/%s'%('/website/action',link)
            returnurls.url_join(base_url,path)
        return''

    @api.depends('state','website_published','website_path','xml_id')
    def_get_website_url(self):
        foractioninself:
            ifaction.state=='code'andaction.website_published:
                action.website_url=action._compute_website_url(action.website_path,action.xml_id)
            else:
                action.website_url=False

    @api.model
    def_get_eval_context(self,action):
        """Overridetoaddtherequestobjectineval_context."""
        eval_context=super(ServerAction,self)._get_eval_context(action)
        ifaction.state=='code':
            eval_context['request']=request
            eval_context['json']=json_scriptsafe
        returneval_context

    @api.model
    def_run_action_code_multi(self,eval_context=None):
        """Overridetoallowreturningresponsethesamewayactionisalready
            returnedbythebasicserveractionbehavior.Notethatresponsehas
            priorityoveraction,avoidusingboth.
        """
        res=super(ServerAction,self)._run_action_code_multi(eval_context)
        returneval_context.get('response',res)


classIrActionsTodo(models.Model):
    _name='ir.actions.todo'
    _inherit='ir.actions.todo'

    defaction_launch(self):
        res=super().action_launch() #doensure_one()

        ifself.id==self.env.ref('website.theme_install_todo').id:
            #Pickathemeconsumeallir.actions.todobydefault(duetolowersequence).
            #Oncedone,were-enablethemainir.act.todo:open_menu
            self.env.ref('base.open_menu').action_open()

        returnres
