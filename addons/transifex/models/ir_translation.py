#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromconfigparserimportConfigParser
fromos.pathimportjoinasopj
importos
importwerkzeug.urls

importflectra
fromflectraimportmodels,fields


classIrTranslation(models.Model):

    _inherit='ir.translation'

    transifex_url=fields.Char("TransifexURL",compute='_get_transifex_url',help="ProposeamodificationintheofficialversionofFlectra")

    def_get_transifex_url(self):
        """ConstructtransifexURLbasedonthemoduleonconfiguration"""
        #e.g.'https://www.transifex.com/flectra/'
        base_url=self.env['ir.config_parameter'].sudo().get_param('transifex.project_url')

        tx_config_file=ConfigParser()
        tx_sections=[]
        foraddon_pathinflectra.addons.__path__:
            tx_path=opj(addon_path,'.tx','config')
            ifos.path.isfile(tx_path):
                tx_config_file.read(tx_path)
                #firstsectionis[main],after[flectra-11.sale]
                tx_sections.extend(tx_config_file.sections()[1:])

            #parentdirectoryad.tx/configisrootdirectoryinflectra/flectra
            tx_path=opj(addon_path,os.pardir,'.tx','config')
            ifos.path.isfile(tx_path):
                tx_config_file.read(tx_path)
                tx_sections.extend(tx_config_file.sections()[1:])

        ifnotbase_urlornottx_sections:
            self.update({'transifex_url':False})
        else:
            base_url=base_url.rstrip('/')

            #willprobablybethesameforallterms,avoidmultiplesearches
            translation_languages=list(set(self.mapped('lang')))
            languages=self.env['res.lang'].with_context(active_test=False).search(
                [('code','in',translation_languages)])

            language_codes=dict((l.code,l.iso_code)forlinlanguages)

            #.tx/configfilescontainstheprojectreference
            #usinginifiles
            translation_modules=set(self.mapped('module'))
            project_modules={}
            formoduleintranslation_modules:
                forsectionintx_sections:
                    iflen(section.split(':'))!=6:
                        #oldformat['main','flectra-16.base',...]
                        tx_project,tx_mod=section.split(".")
                    else:
                        #tx_config_file.sections():['main','o:flectra:p:flectra-16:r:base',...]
                        _,_,_,tx_project,_,tx_mod=section.split(':')
                    iftx_mod==module:
                        project_modules[module]=tx_project

            fortranslationinself:
                ifnottranslation.moduleornottranslation.srcortranslation.lang=='en_US':
                    #customorsourceterm
                    translation.transifex_url=False
                    continue

                lang_code=language_codes.get(translation.lang)
                ifnotlang_code:
                    translation.transifex_url=False
                    continue

                project=project_modules.get(translation.module)
                ifnotproject:
                    translation.transifex_url=False
                    continue

                #e.g.https://www.transifex.com/flectra/flectra-10/translate/#fr/sale/42?q=text:'Sale+Order'
                src=werkzeug.urls.url_quote_plus(translation.src[:50].replace("\n","").replace("'","\\'"))
                src=f"'{src}'"if"+"insrcelsesrc
                translation.transifex_url="%(url)s/%(project)s/translate/#%(lang)s/%(module)s/42?q=%(src)s"%{
                    'url':base_url,
                    'project':project,
                    'lang':lang_code,
                    'module':translation.module,
                    'src':f"text%3A{src}",
                }
