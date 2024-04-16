#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
importlogging

fromflectraimportapi,models

_logger=logging.getLogger(__name__)


classAccountChartTemplate(models.Model):
    _inherit='account.chart.template'

    def_load(self,sale_tax_rate,purchase_tax_rate,company):
        res=super(AccountChartTemplate,self)._load(sale_tax_rate,purchase_tax_rate,company)
        #Copychartofaccounttranslationswhenloadingchartofaccount
        forchart_templateinself.filtered('spoken_languages'):
            external_id=self.env['ir.model.data'].search([
                ('model','=','account.chart.template'),
                ('res_id','=',chart_template.id),
            ],order='id',limit=1)
            module=external_idandself.env.ref('base.module_'+external_id.module)
            ifmoduleandmodule.state=='installed':
                langs=chart_template._get_langs()
                iflangs:
                    chart_template._process_single_company_coa_translations(company.id,langs)
        returnres

    defprocess_translations(self,langs,in_field,in_ids,out_ids):
        """
        ThismethodcopiestranslationsvaluesoftemplatesintonewAccounts/Taxes/Journalsforlanguagesselected

        :paramlangs:Listoflanguagestoloadfornewrecords
        :paramin_field:Nameofthetranslatablefieldofsourcetemplates
        :paramin_ids:Recordsetofidsofsourceobject
        :paramout_ids:Recordsetofidsofdestinationobject

        :return:True
        """
        xlat_obj=self.env['ir.translation']
        #findthesourcefromAccountTemplate
        forlanginlangs:
            #findthevaluefromTranslation
            value=xlat_obj._get_ids(in_ids._name+','+in_field,'model',lang,in_ids.ids)
            counter=0
            forelementinin_ids.with_context(lang=None):
                ifvalue[element.id]:
                    #copyTranslationfromSourcetoDestinationobject
                    xlat_obj._set_ids(
                        out_ids._name+','+in_field,
                        'model',
                        lang,
                        out_ids[counter].ids,
                        value[element.id],
                        element[in_field]
                    )
                else:
                    _logger.info('Language:%s.Translationfromtemplate:thereisnotranslationavailablefor%s!'%(lang,element[in_field]))
                counter+=1
        returnTrue

    defprocess_coa_translations(self):
        company_obj=self.env['res.company']
        forchart_template_idinself:
            langs=chart_template_id._get_langs()
            iflangs:
                company_ids=company_obj.search([('chart_template_id','=',chart_template_id.id)])
                forcompanyincompany_ids:
                    chart_template_id._process_single_company_coa_translations(company.id,langs)
        returnTrue

    def_process_single_company_coa_translations(self,company_id,langs):
        #writeaccount.accounttranslationsintherealCOA
        self._process_accounts_translations(company_id,langs,'name')
        #writeaccount.grouptranslations
        self._process_account_group_translations(company_id,langs,'name')
        #copyaccount.taxnametranslations
        self._process_taxes_translations(company_id,langs,'name')
        #copyaccount.taxdescriptiontranslations
        self._process_taxes_translations(company_id,langs,'description')
        #copyaccount.fiscal.positiontranslations
        self._process_fiscal_pos_translations(company_id,langs,'name')

    def_get_langs(self):
        ifnotself.spoken_languages:
            return[]

        installed_langs=dict(self.env['res.lang'].get_installed())
        langs=[]
        forlanginself.spoken_languages.split(';'):
            iflangnotininstalled_langs:
                #thelanguageisnotinstalled,sowedon'tneedtoloaditstranslations
                continue
            else:
                langs.append(lang)
        returnlangs

    def_process_accounts_translations(self,company_id,langs,field):
        in_ids,out_ids=self._get_template_from_model(company_id,'account.account')
        returnself.process_translations(langs,field,in_ids,out_ids)

    def_process_account_group_translations(self,company_id,langs,field):
        in_ids,out_ids=self._get_template_from_model(company_id,'account.group')
        returnself.process_translations(langs,field,in_ids,out_ids)

    def_process_taxes_translations(self,company_id,langs,field):
        in_ids,out_ids=self._get_template_from_model(company_id,'account.tax')
        returnself.process_translations(langs,field,in_ids,out_ids)

    def_process_fiscal_pos_translations(self,company_id,langs,field):
        in_ids,out_ids=self._get_template_from_model(company_id,'account.fiscal.position')
        returnself.process_translations(langs,field,in_ids,out_ids)

    def_get_template_from_model(self,company_id,model):
        """Findtherecordsandtheirmatchingtemplate"""
        #generatedrecordshaveanexternalidwiththeformat<companyid>_<templatexmlid>
        grouped_out_data=defaultdict(lambda:self.env['ir.model.data'])
        forimdinself.env['ir.model.data'].search([
                ('model','=',model),
                ('name','=like',str(company_id)+'_%')
            ]):
            grouped_out_data[imd.module]+=imd

        in_records=self.env[model+'.template']
        out_records=self.env[model]
        formodule,out_dataingrouped_out_data.items():
            #templatesandrecordsmayhavebeencreatedinadifferentorder
            #reorderthembasedonexternalidnames
            expected_in_xml_id_names={xml_id.name.partition(str(company_id)+'_')[-1]:xml_idforxml_idinout_data}

            in_xml_ids=self.env['ir.model.data'].search([
                ('model','=',model+'.template'),
                ('module','=',module),
                ('name','in',list(expected_in_xml_id_names))
            ])
            in_xml_ids={xml_id.name:xml_idforxml_idinin_xml_ids}

            forname,xml_idinexpected_in_xml_id_names.items():
                #ignorenonconformingcustomizeddata
                ifnamenotinin_xml_ids:
                    continue
                in_records+=self.env[model+'.template'].browse(in_xml_ids[name].res_id)
                out_records+=self.env[model].browse(xml_id.res_id)

        return(in_records,out_records)

classBaseLanguageInstall(models.TransientModel):
    """InstallLanguage"""
    _inherit="base.language.install"

    deflang_install(self):
        self.ensure_one()
        already_installed=self.langin[codeforcode,_inself.env['res.lang'].get_installed()]
        res=super(BaseLanguageInstall,self).lang_install()
        ifalready_installed:
            #updateoftranslationsinsteadofnewinstallation
            #skiptoavoidduplicatingthetranslations
            returnres

        #CoAinmultilangmode
        forcoainself.env['account.chart.template'].search([('spoken_languages','!=',False)]):
            ifself.langincoa.spoken_languages.split(';'):
                #companiesonwhichitisinstalled
                forcompanyinself.env['res.company'].search([('chart_template_id','=',coa.id)]):
                    #writeaccount.accounttranslationsintherealCOA
                    coa._process_accounts_translations(company.id,[self.lang],'name')
                    #writeaccount.grouptranslations
                    coa._process_account_group_translations(company.id,[self.lang],'name')
                    #copyaccount.taxnametranslations
                    coa._process_taxes_translations(company.id,[self.lang],'name')
                    #copyaccount.taxdescriptiontranslations
                    coa._process_taxes_translations(company.id,[self.lang],'description')
                    #copyaccount.fiscal.positiontranslations
                    coa._process_fiscal_pos_translations(company.id,[self.lang],'name')
        returnres
