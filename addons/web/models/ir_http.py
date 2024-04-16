#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importhashlib
importjson

fromflectraimportapi,models
fromflectra.httpimportrequest
fromflectra.toolsimportustr

fromflectra.addons.web.controllers.mainimportmodule_boot,HomeStaticTemplateHelpers

importflectra


classHttp(models.AbstractModel):
    _inherit='ir.http'

    defwebclient_rendering_context(self):
        return{
            'menu_data':request.env['ir.ui.menu'].load_menus(request.session.debug),
            'session_info':self.session_info(),
        }

    defsession_info(self):
        user=request.env.user
        version_info=flectra.service.common.exp_version()

        user_context=request.session.get_context()ifrequest.session.uidelse{}
        IrConfigSudo=self.env['ir.config_parameter'].sudo()
        max_file_upload_size=int(IrConfigSudo.get_param(
            'web.max_file_upload_size',
            default=128*1024*1024, #128MiB
        ))

        session_info={
            "uid":request.session.uid,
            "is_system":user._is_system()ifrequest.session.uidelseFalse,
            "is_admin":user._is_admin()ifrequest.session.uidelseFalse,
            "user_context":request.session.get_context()ifrequest.session.uidelse{},
            "db":request.session.db,
            "server_version":version_info.get('server_version'),
            "server_version_info":version_info.get('server_version_info'),
            "name":user.name,
            "username":user.login,
            "partner_display_name":user.partner_id.display_name,
            "company_id":user.company_id.idifrequest.session.uidelseNone, #YTITODO:Removethisfromtheusercontext
            "partner_id":user.partner_id.idifrequest.session.uidanduser.partner_idelseNone,
            "web.base.url":IrConfigSudo.get_param('web.base.url',default=''),
            "active_ids_limit":int(IrConfigSudo.get_param('web.active_ids_limit',default='20000')),
            "max_file_upload_size":max_file_upload_size,
        }
        ifself.env.user.has_group('base.group_user'):
            #thefollowingisonlyusefulinthecontextofawebclientbootstrapping
            #butisstillincludedinsomeothercalls(e.g.'/web/session/authenticate')
            #toavoidaccesserrorsandunnecessaryinformation,itisonlyincludedforusers
            #withaccesstothebackend('internal'-typeusers)
            mods=module_boot()
            qweb_checksum=HomeStaticTemplateHelpers.get_qweb_templates_checksum(addons=mods,debug=request.session.debug)
            lang=user_context.get("lang")
            translation_hash=request.env['ir.translation'].get_web_translations_hash(mods,lang)
            menu_json_utf8=json.dumps(request.env['ir.ui.menu'].load_menus(request.session.debug),default=ustr,sort_keys=True).encode()
            cache_hashes={
                "load_menus":hashlib.sha512(menu_json_utf8).hexdigest()[:64],#sha512/256
                "qweb":qweb_checksum,
                "translations":translation_hash,
            }
            session_info.update({
                #current_companyshouldbedefault_company
                "user_companies":{'current_company':(user.company_id.id,user.company_id.name),'allowed_companies':[(comp.id,comp.name)forcompinuser.company_ids]},
                "currencies":self.get_currencies(),
                "show_effect":True,
                "display_switch_company_menu":user.has_group('base.group_multi_company')andlen(user.company_ids)>1,
                "cache_hashes":cache_hashes,
            })
        returnsession_info

    @api.model
    defget_frontend_session_info(self):
        session_info={
            'is_admin':request.session.uidandself.env.user._is_admin()orFalse,
            'is_system':request.session.uidandself.env.user._is_system()orFalse,
            'is_website_user':request.session.uidandself.env.user._is_public()orFalse,
            'user_id':request.session.uidandself.env.user.idorFalse,
            'is_frontend':True,
        }
        ifrequest.session.uid:
            version_info=flectra.service.common.exp_version()
            session_info.update({
                'server_version':version_info.get('server_version'),
                'server_version_info':version_info.get('server_version_info')
            })
        returnsession_info

    defget_currencies(self):
        Currency=request.env['res.currency']
        currencies=Currency.search([]).read(['symbol','position','decimal_places'])
        return{c['id']:{'symbol':c['symbol'],'position':c['position'],'digits':[69,c['decimal_places']]}forcincurrencies}
