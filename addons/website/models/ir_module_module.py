#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importos
fromcollectionsimportOrderedDict

fromflectraimportapi,fields,models
fromflectra.addons.base.models.ir_modelimportMODULE_UNINSTALL_FLAG
fromflectra.exceptionsimportMissingError
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classIrModuleModule(models.Model):
    _name="ir.module.module"
    _description='Module'
    _inherit=_name

    #Theorderisimportantbecauseofdependencies(pageneedview,menuneedpage)
    _theme_model_names=OrderedDict([
        ('ir.ui.view','theme.ir.ui.view'),
        ('website.page','theme.website.page'),
        ('website.menu','theme.website.menu'),
        ('ir.attachment','theme.ir.attachment'),
    ])
    _theme_translated_fields={
        'theme.ir.ui.view':[('theme.ir.ui.view,arch','ir.ui.view,arch_db')],
        'theme.website.menu':[('theme.website.menu,name','website.menu,name')],
    }

    image_ids=fields.One2many('ir.attachment','res_id',
                                domain=[('res_model','=',_name),('mimetype','=like','image/%')],
                                string='Screenshots',readonly=True)
    #forkanbanview
    is_installed_on_current_website=fields.Boolean(compute='_compute_is_installed_on_current_website')

    def_compute_is_installed_on_current_website(self):
        """
            Computeforeverythemein``self``ifthecurrentwebsiteisusingitornot.

            Thismethoddoesnottakedependenciesintoaccount,becauseifitdid,itwouldshow
            thecurrentwebsiteashavingmultipledifferentthemesinstalledatthesametime,
            whichwouldbeconfusingfortheuser.
        """
        formoduleinself:
            module.is_installed_on_current_website=module==self.env['website'].get_current_website().theme_id

    defwrite(self,vals):
        """
            Overridetocorrectlyupgradethemesafterupgrade/installationofmodules.

            #Install

                Ifthisthemewasn'tinstalledbefore,thenloaditforeverywebsite
                forwhichitisinthestream.

                eg.Theveryfirstinstallationofathemeonawebsitewilltriggerthis.

                eg.Ifawebsiteusestheme_Aandweinstallsale,thentheme_A_salewillbe
                    autoinstalled,andinthiscaseweneedtoloadtheme_A_saleforthewebsite.

            #Upgrade

                Thereare2casestohandlewhenupgradingatheme:

                *Whenclickingonthethemeupgradebuttonontheinterface,
                    inwhichcasetherewillbeanhttprequestmade.

                    ->Wewanttoupgradethecurrentwebsiteonly,notanyother.

                *Whenupgradingwith-u,inwhichcasenorequestshouldbeset.

                    ->Wewanttoupgradeeverywebsiteusingthistheme.
        """
        ifrequestandrequest.context.get('apply_new_theme'):
            self=self.with_context(apply_new_theme=True)

        formoduleinself:
            ifmodule.name.startswith('theme_')andvals.get('state')=='installed':
                _logger.info('Module%shasbeenloadedasthemetemplate(%s)'%(module.name,module.state))

                ifmodule.statein['toinstall','toupgrade']:
                    websites_to_update=module._theme_get_stream_website_ids()

                    ifmodule.state=='toupgrade'andrequest:
                        Website=self.env['website']
                        current_website=Website.get_current_website()
                        websites_to_update=current_websiteifcurrent_websiteinwebsites_to_updateelseWebsite

                    forwebsiteinwebsites_to_update:
                        module._theme_load(website)

        returnsuper(IrModuleModule,self).write(vals)

    def_get_module_data(self,model_name):
        """
            Returneverythemetemplatemodeloftype``model_name``foreverythemein``self``.

            :parammodel_name:stringwiththetechnicalnameofthemodelforwhichtogetdata.
                (thenamemustbeoneofthekeyspresentin``_theme_model_names``)
            :return:recordsetofthemetemplatemodels(oftypedefinedby``model_name``)
        """
        theme_model_name=self._theme_model_names[model_name]
        IrModelData=self.env['ir.model.data']
        records=self.env[theme_model_name]

        formoduleinself:
            imd_ids=IrModelData.search([('module','=',module.name),('model','=',theme_model_name)]).mapped('res_id')
            records|=self.env[theme_model_name].with_context(active_test=False).browse(imd_ids)
        returnrecords

    def_update_records(self,model_name,website):
        """
            Thismethod:

            -Findandupdateexistingrecords.

                Foreachmodel,overwritethefieldsthataredefinedinthetemplate(exceptfew
                casessuchasactive)butkeepinheritedmodelstonotlosecustomizations.

            -Createnewrecordsfromtemplatesforthosethatdidn'texist.

            -Removethemodelsthatexistedbeforebutarenotinthetemplateanymore.

                See_theme_cleanupformoreinformation.


            Thereisaspecial'while'looparoundthe'for'tobeablequeuebackmodelsattheend
            oftheiterationwhentheyhaveunmetdependencies.Hopefullythedependencywillbe
            foundafterallmodelshavebeenprocessed,butifit'snotthecaseanerrormessagewillbeshown.


            :parammodel_name:stringwiththetechnicalnameofthemodeltohandle
                (thenamemustbeoneofthekeyspresentin``_theme_model_names``)
            :paramwebsite:``website``modelforwhichtherecordshavetobeupdated

            :raiseMissingError:ifthereisamissingdependency.
        """
        self.ensure_one()

        remaining=self._get_module_data(model_name)
        last_len=-1
        while(len(remaining)!=last_len):
            last_len=len(remaining)
            forrecinremaining:
                rec_data=rec._convert_to_base_model(website)
                ifnotrec_data:
                    _logger.info('Recordqueued:%s'%rec.display_name)
                    continue

                find=rec.with_context(active_test=False).mapped('copy_ids').filtered(lambdam:m.website_id==website)

                #specialcaseforattachment
                #ifmoduleBoverrideattachmentfromdependenceA,weupdateit
                ifnotfindandmodel_name=='ir.attachment':
                    #Inmaster,auniqueconstraintover(theme_template_id,website_id)
                    #willbeintroduced,thusensuringunicityof'find'
                    find=rec.copy_ids.search([('key','=',rec.key),('website_id','=',website.id),("original_id","=",False)])

                iffind:
                    imd=self.env['ir.model.data'].search([('model','=',find._name),('res_id','=',find.id)])
                    ifimdandimd.noupdate:
                        _logger.info('Noupdatesetfor%s(%s)'%(find,imd))
                    else:
                        #atupdate,ignoreactivefield
                        if'active'inrec_data:
                            rec_data.pop('active')
                        ifmodel_name=='ir.ui.view'and(find.arch_updatedorfind.arch==rec_data['arch']):
                            rec_data.pop('arch')
                        find.update(rec_data)
                        self._post_copy(rec,find)
                else:
                    new_rec=self.env[model_name].create(rec_data)
                    self._post_copy(rec,new_rec)

                remaining-=rec

        iflen(remaining):
            error='Error-Remaining:%s'%remaining.mapped('display_name')
            _logger.error(error)
            raiseMissingError(error)

        self._theme_cleanup(model_name,website)

    def_post_copy(self,old_rec,new_rec):
        self.ensure_one()
        translated_fields=self._theme_translated_fields.get(old_rec._name,[])
        for(src_field,dst_field)intranslated_fields:
            self._cr.execute("""INSERTINTOir_translation(lang,src,name,res_id,state,value,type,module)
                                SELECTt.lang,t.src,%s,%s,t.state,t.value,t.type,t.module
                                FROMir_translationt
                                WHEREname=%s
                                  ANDres_id=%s
                                ONCONFLICTDONOTHING""",
                             (dst_field,new_rec.id,src_field,old_rec.id))

    def_theme_load(self,website):
        """
            Foreverytypeofmodelin``self._theme_model_names``,andforeverythemein``self``:
            create/updaterealmodelsforthewebsite``website``basedonthethemetemplatemodels.

            :paramwebsite:``website``modelonwhichtoloadthethemes
        """
        formoduleinself:
            _logger.info('Loadtheme%sforwebsite%sfromtemplate.'%(module.mapped('name'),website.id))

            formodel_nameinself._theme_model_names:
                module._update_records(model_name,website)

            ifself._context.get('apply_new_theme'):
                #Boththethemeinstallandupgradeflowendsuphere.
                #The_post_copy()issupposedtobecalledonlywhenthetheme
                #isinstalledforthefirsttimeonawebsite.
                #Itwillbasicallyselectsomeheaderandfootertemplate.
                #Wedon'twantthesystemtoselectagainthethemefooteror
                #headertemplatewhenthatthemeisupdatedlater.Itcould
                #erasethechangetheusermadeafterthethemeinstall.
                self.env['theme.utils'].with_context(website_id=website.id)._post_copy(module)

    def_theme_unload(self,website):
        """
            Foreverytypeofmodelin``self._theme_model_names``,andforeverythemein``self``:
            removerealmodelsthatweregeneratedbasedonthethemetemplatemodels
            forthewebsite``website``.

            :paramwebsite:``website``modelonwhichtounloadthethemes
        """
        formoduleinself:
            _logger.info('Unloadtheme%sforwebsite%sfromtemplate.'%(self.mapped('name'),website.id))

            formodel_nameinself._theme_model_names:
                template=self._get_module_data(model_name)
                models=template.with_context(**{'active_test':False,MODULE_UNINSTALL_FLAG:True}).mapped('copy_ids').filtered(lambdam:m.website_id==website)
                models.unlink()
                self._theme_cleanup(model_name,website)

    def_theme_cleanup(self,model_name,website):
        """
            Removeorphanmodelsoftype``model_name``fromthecurrentthemeand
            forthewebsite``website``.

            Weneedtocomputeitthiswaybecauseiftheupgrade(ordeletion)ofathememodule
            removesamodeltemplate,theninthemodelitselfthevariable
            ``theme_template_id``willbesettoNULLandthereferencetothethemebeingremoved
            willbelost.Howeverwedowanttheophantobedeletedfromthewebsitewhen
            weupgradeordeletethethemefromthewebsite.

            ``website.page``and``website.menu``don'thave``key``fieldsowedon'tcleanthem.
            TODOinmaster:addafield``theme_id``onthemodelstomorecleanlycomputeorphans.

            :parammodel_name:stringwiththetechnicalnameofthemodeltocleanup
                (thenamemustbeoneofthekeyspresentin``_theme_model_names``)
            :paramwebsite:``website``modelforwhichthemodelshavetobecleaned

        """
        self.ensure_one()
        model=self.env[model_name]

        ifmodel_namein('website.page','website.menu'):
            returnmodel
        #useactive_testtoalsounlinkarchivedmodels
        #anduseMODULE_UNINSTALL_FLAGtoalsounlinkinheritedmodels
        orphans=model.with_context(**{'active_test':False,MODULE_UNINSTALL_FLAG:True}).search([
            ('key','=like',self.name+'.%'),
            ('website_id','=',website.id),
            ('theme_template_id','=',False),
        ])
        orphans.unlink()

    def_theme_get_upstream(self):
        """
            Returninstalledupstreamthemes.

            :return:recordsetofthemes``ir.module.module``
        """
        self.ensure_one()
        returnself.upstream_dependencies(exclude_states=('',)).filtered(lambdax:x.name.startswith('theme_'))

    def_theme_get_downstream(self):
        """
            Returninstalleddownstreamthemesthatstartswiththesamename.

            eg.Fortheme_A,thiswillreturntheme_A_sale,butnottheme_BevenifthemeB
                dependsontheme_A.

            :return:recordsetofthemes``ir.module.module``
        """
        self.ensure_one()
        returnself.downstream_dependencies().filtered(lambdax:x.name.startswith(self.name))

    def_theme_get_stream_themes(self):
        """
            Returnsallthethemesinthestreamofthecurrenttheme.

            Firstfindallitsdownstreamthemes,andalloftheupstreamthemesofboth
            sortedbytheirlevelinhierarchy,upfirst.

            :return:recordsetofthemes``ir.module.module``
        """
        self.ensure_one()
        all_mods=self+self._theme_get_downstream()
        fordown_modinself._theme_get_downstream()+self:
            forup_modindown_mod._theme_get_upstream():
                all_mods=up_mod|all_mods
        returnall_mods

    def_theme_get_stream_website_ids(self):
        """
            Websitesforwhichthistheme(self)isinthestream(upordown)oftheirtheme.

            :return:recordsetofwebsites``website``
        """
        self.ensure_one()
        websites=self.env['website']
        forwebsiteinwebsites.search([('theme_id','!=',False)]):
            ifselfinwebsite.theme_id._theme_get_stream_themes():
                websites|=website
        returnwebsites

    def_theme_upgrade_upstream(self):
        """Upgradetheupstreamdependenciesofatheme,andinstallitifnecessary."""
        definstall_or_upgrade(theme):
            iftheme.state!='installed':
                theme.button_install()
            themes=theme+theme._theme_get_upstream()
            themes.filtered(lambdam:m.state=='installed').button_upgrade()

        self._button_immediate_function(install_or_upgrade)

    @api.model
    def_theme_remove(self,website):
        """
            Removefrom``website``itscurrenttheme,includingallthethemesinthestream.

            Theorderofremovalwillbereverseofinstallationtohandledependenciescorrectly.

            :paramwebsite:``website``modelforwhichthethemeshavetoberemoved
        """
        #_theme_removeistheentrypointofanychangeofthemeforawebsite
        #(eitherremovalorinstallationofathemeanditsdependencies).In
        #eithercase,weneedtoresetsomedefaultconfigurationbefore.
        self.env['theme.utils'].with_context(website_id=website.id)._reset_default_config()

        ifnotwebsite.theme_id:
            return

        forthemeinreversed(website.theme_id._theme_get_stream_themes()):
            theme._theme_unload(website)
        website.theme_id=False

    defbutton_choose_theme(self):
        """
            Removeanyexistingthemeonthecurrentwebsiteandinstallthetheme``self``instead.

            Theactualloadingofthethemeonthecurrentwebsitewillbedone
            automaticallyon``write``thankstotheupgradeand/orinstall.

            Wheninstallatinganewtheme,upgradetheupstreamchainfirsttomakesure
            wehavethelatestversionofthedependenciestopreventinconsistencies.

            :return:dictwiththenextactiontoexecute
        """
        self.ensure_one()
        website=self.env['website'].get_current_website()

        self._theme_remove(website)

        #website.theme_idmustbesetbeforeupgrade/installtotriggertheloadin``write``
        website.theme_id=self

        #thiswillinstall'self'ifitisnotinstalledyet
        ifrequest:
            context=dict(request.context)
            context['apply_new_theme']=True
            request.context=context
        self._theme_upgrade_upstream()

        active_todo=self.env['ir.actions.todo'].search([('state','=','open')],limit=1)
        ifactive_todo:
            returnactive_todo.action_launch()
        else:
            returnwebsite.button_go_website(mode_edit=True)

    defbutton_remove_theme(self):
        """Removethecurrentthemeofthecurrentwebsite."""
        website=self.env['website'].get_current_website()
        self._theme_remove(website)

    defbutton_refresh_theme(self):
        """
            Refreshthecurrentthemeofthecurrentwebsite.

            Torefreshit,weonlyneedtoupgradethemodules.
            Indeedthe(re)loadingofthethemewillbedoneautomaticallyon``write``.
        """
        website=self.env['website'].get_current_website()
        website.theme_id._theme_upgrade_upstream()

    @api.model
    defupdate_list(self):
        res=super(IrModuleModule,self).update_list()
        self.update_theme_images()
        returnres

    @api.model
    defupdate_theme_images(self):
        IrAttachment=self.env['ir.attachment']
        existing_urls=IrAttachment.search_read([['res_model','=',self._name],['type','=','url']],['url'])
        existing_urls={url_wrapped['url']forurl_wrappedinexisting_urls}

        themes=self.env['ir.module.module'].with_context(active_test=False).search([
            ('category_id','child_of',self.env.ref('base.module_category_theme').id),
        ],order='name')

        forthemeinthemes:
            terp=self.get_module_info(theme.name)
            images=terp.get('images',[])
            forimageinimages:
                image_path='/'+os.path.join(theme.name,image)
                ifimage_pathnotinexisting_urls:
                    image_name=os.path.basename(image_path)
                    IrAttachment.create({
                        'type':'url',
                        'name':image_name,
                        'url':image_path,
                        'res_model':self._name,
                        'res_id':theme.id,
                    })

    def_check(self):
        super()._check()
        View=self.env['ir.ui.view']
        website_views_to_adapt=getattr(self.pool,'website_views_to_adapt',[])
        ifwebsite_views_to_adapt:
            forview_replayinwebsite_views_to_adapt:
                cow_view=View.browse(view_replay[0])
                View._load_records_write_on_cow(cow_view,view_replay[1],view_replay[2])
            self.pool.website_views_to_adapt.clear()
