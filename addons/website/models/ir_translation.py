#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels

classIrTranslation(models.Model):
    _inherit="ir.translation"

    def_load_module_terms(self,modules,langs,overwrite=False):
        """Addmissingwebsitespecifictranslation"""
        res=super()._load_module_terms(modules,langs,overwrite=overwrite)

        ifnotlangsornotmodules:
            returnres

        ifoverwrite:
            conflict_clause="""
                   ONCONFLICT{}
                   DOUPDATESET(name,lang,res_id,src,type,value,module,state,comments)=
                       (EXCLUDED.name,EXCLUDED.lang,EXCLUDED.res_id,EXCLUDED.src,EXCLUDED.type,
                        EXCLUDED.value,EXCLUDED.module,EXCLUDED.state,EXCLUDED.comments)
                WHEREEXCLUDED.valueISNOTNULLANDEXCLUDED.value!=''
            """;
        else:
            conflict_clause="ONCONFLICTDONOTHING"

        #Addspecificviewtranslations
        self.env.cr.execute("""
            INSERTINTOir_translation(name,lang,res_id,src,type,value,module,state,comments)
            SELECTDISTINCTON(specific.id,t.lang,md5(src))t.name,t.lang,specific.id,t.src,t.type,t.value,t.module,t.state,t.comments
              FROMir_translationt
             INNERJOINir_ui_viewgeneric
                ONt.type='model_terms'ANDt.name='ir.ui.view,arch_db'ANDt.res_id=generic.id
             INNERJOINir_ui_viewspecific
                ONgeneric.key=specific.key
             WHEREt.langIN%sandt.moduleIN%s
               ANDgeneric.website_idISNULLANDgeneric.type='qweb'
               ANDspecific.website_idISNOTNULL"""+conflict_clause.format(
                   "(type,name,lang,res_id,md5(src))"
        ),(tuple(langs),tuple(modules)))

        default_menu=self.env.ref('website.main_menu',raise_if_not_found=False)
        ifnotdefault_menu:
            returnres

        #Addspecificmenutranslations
        self.env.cr.execute("""
            INSERTINTOir_translation(name,lang,res_id,src,type,value,module,state,comments)
            SELECTDISTINCTON(s_menu.id,t.lang)t.name,t.lang,s_menu.id,t.src,t.type,t.value,t.module,t.state,t.comments
              FROMir_translationt
             INNERJOINwebsite_menuo_menu
                ONt.type='model'ANDt.name='website.menu,name'ANDt.res_id=o_menu.id
             INNERJOINwebsite_menus_menu
                ONo_menu.name=s_menu.nameANDo_menu.url=s_menu.url
             INNERJOINwebsite_menuroot_menu
                ONs_menu.parent_id=root_menu.idANDroot_menu.parent_idISNULL
             WHEREt.langIN%sandt.moduleIN%s
               ANDo_menu.website_idISNULLANDo_menu.parent_id=%s
               ANDs_menu.website_idISNOTNULL"""+conflict_clause.format(
                   "(type,lang,name,res_id)WHEREtype='model'"
        ),(tuple(langs),tuple(modules),default_menu.id))

        returnres
