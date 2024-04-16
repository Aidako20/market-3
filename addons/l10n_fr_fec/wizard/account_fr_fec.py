#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

#Copyright(C)2013-2015Akretion(http://www.akretion.com)

importbase64
importio

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,AccessDenied
fromflectra.toolsimportfloat_is_zero,pycompat
fromflectra.tools.miscimportget_lang
fromstdnum.frimportsiren


classAccountFrFec(models.TransientModel):
    _name='account.fr.fec'
    _description='FicherEchangeInformatise'

    date_from=fields.Date(string='StartDate',required=True)
    date_to=fields.Date(string='EndDate',required=True)
    fec_data=fields.Binary('FECFile',readonly=True)
    filename=fields.Char(string='Filename',size=256,readonly=True)
    test_file=fields.Boolean()
    export_type=fields.Selection([
        ('official','OfficialFECreport(postedentriesonly)'),
        ('nonofficial','Non-officialFECreport(postedandunpostedentries)'),
        ],string='ExportType',required=True,default='official')

    @api.onchange('test_file')
    def_onchange_export_file(self):
        ifnotself.test_file:
            self.export_type='official'

    def_do_query_unaffected_earnings(self):
        '''Computethesumofendingbalancesforallaccountsthatareofatypethatdoesnotbringforwardthebalanceinnewfiscalyears.
            Thisisneededbecausewehavetodisplayonlyonelinefortheinitialbalanceofallexpense/revenueaccountsintheFEC.
        '''

        sql_query='''
        SELECT
            'OUV'ASJournalCode,
            'Balanceinitiale'ASJournalLib,
            'OUVERTURE/'||%sASEcritureNum,
            %sASEcritureDate,
            '120/129'ASCompteNum,
            'Benefice(perte)reporte(e)'ASCompteLib,
            ''ASCompAuxNum,
            ''ASCompAuxLib,
            '-'ASPieceRef,
            %sASPieceDate,
            '/'ASEcritureLib,
            replace(CASEWHENCOALESCE(sum(aml.balance),0)<=0THEN'0,00'ELSEto_char(SUM(aml.balance),'000000000000000D99')END,'.',',')ASDebit,
            replace(CASEWHENCOALESCE(sum(aml.balance),0)>=0THEN'0,00'ELSEto_char(-SUM(aml.balance),'000000000000000D99')END,'.',',')ASCredit,
            ''ASEcritureLet,
            ''ASDateLet,
            %sASValidDate,
            ''ASMontantdevise,
            ''ASIdevise
        FROM
            account_move_lineaml
            LEFTJOINaccount_moveamONam.id=aml.move_id
            JOINaccount_accountaaONaa.id=aml.account_id
            LEFTJOINaccount_account_typeaatONaa.user_type_id=aat.id
        WHERE
            am.date<%s
            ANDam.company_id=%s
            ANDaat.include_initial_balanceISNOTTRUE
        '''
        #Forofficialreport:onlyusepostedentries
        ifself.export_type=="official":
            sql_query+='''
            ANDam.state='posted'
            '''
        company=self.env.company
        formatted_date_from=fields.Date.to_string(self.date_from).replace('-','')
        date_from=self.date_from
        formatted_date_year=date_from.year
        self._cr.execute(
            sql_query,(formatted_date_year,formatted_date_from,formatted_date_from,formatted_date_from,self.date_from,company.id))
        listrow=[]
        row=self._cr.fetchone()
        listrow=list(row)
        returnlistrow

    def_get_company_legal_data(self,company):
        """
        Dom-TomareexcludedfromtheEU'sfiscalterritory
        ThoseregionsdonothaveSIREN
        sources:
            https://www.service-public.fr/professionnels-entreprises/vosdroits/F23570
            http://www.douane.gouv.fr/articles/a11024-tva-dans-les-dom

        *Returnsthesirenifthecompanyisfrenchoranemptysirenfordom-tom
        *Fornon-frenchcompanies->returnsthecompletevatnumber
        """
        dom_tom_group=self.env.ref('l10n_fr.dom-tom')
        is_dom_tom=company.country_id.codeindom_tom_group.country_ids.mapped('code')
        ifnotcompany.vatoris_dom_tom:
            return''
        elifcompany.country_id.code=='FR'andlen(company.vat)>=13andsiren.is_valid(company.vat[4:13]):
            returncompany.vat[4:13]
        else:
            returncompany.vat

    defgenerate_fec(self):
        self.ensure_one()
        ifnot(self.env.is_admin()orself.env.user.has_group('account.group_account_user')):
            raiseAccessDenied()
        #WechoosetoimplementtheflatfileinsteadoftheXML
        #filefor2reasons:
        #1)theXSDfileimposetohavethelabelontheaccount.move
        #butFlectrahasthelabelontheaccount.move.line,sothat'sa
        #problem!
        #2)CSVfilesareeasiertoread/useforaregularaccountant.
        #Soitwillbeeasierfortheaccountanttocheckthefilebefore
        #sendingittothefiscaladministration
        today=fields.Date.today()
        ifself.date_from>todayorself.date_to>today:
            raiseUserError(_('Youcouldnotsetthestartdateortheenddateinthefuture.'))
        ifself.date_from>=self.date_to:
            raiseUserError(_('Thestartdatemustbeinferiortotheenddate.'))

        company=self.env.company
        company_legal_data=self._get_company_legal_data(company)

        header=[
            u'JournalCode',   #0
            u'JournalLib',    #1
            u'EcritureNum',   #2
            u'EcritureDate',  #3
            u'CompteNum',     #4
            u'CompteLib',     #5
            u'CompAuxNum',    #6 Weusepartner.id
            u'CompAuxLib',    #7
            u'PieceRef',      #8
            u'PieceDate',     #9
            u'EcritureLib',   #10
            u'Debit',         #11
            u'Credit',        #12
            u'EcritureLet',   #13
            u'DateLet',       #14
            u'ValidDate',     #15
            u'Montantdevise', #16
            u'Idevise',       #17
            ]

        rows_to_write=[header]
        #INITIALBALANCE
        unaffected_earnings_xml_ref=self.env.ref('account.data_unaffected_earnings')
        unaffected_earnings_line=True #usedtomakesurethatweaddtheunaffectedearninginitialbalanceonlyonce
        ifunaffected_earnings_xml_ref:
            #computethebenefit/lossoflastyeartoaddintheinitialbalanceofthecurrentyearearningsaccount
            unaffected_earnings_results=self._do_query_unaffected_earnings()
            unaffected_earnings_line=False

        sql_query='''
        SELECT
            'OUV'ASJournalCode,
            'Balanceinitiale'ASJournalLib,
            'OUVERTURE/'||%sASEcritureNum,
            %sASEcritureDate,
            MIN(aa.code)ASCompteNum,
            replace(replace(MIN(aa.name),'|','/'),'\t','')ASCompteLib,
            ''ASCompAuxNum,
            ''ASCompAuxLib,
            '-'ASPieceRef,
            %sASPieceDate,
            '/'ASEcritureLib,
            replace(CASEWHENsum(aml.balance)<=0THEN'0,00'ELSEto_char(SUM(aml.balance),'000000000000000D99')END,'.',',')ASDebit,
            replace(CASEWHENsum(aml.balance)>=0THEN'0,00'ELSEto_char(-SUM(aml.balance),'000000000000000D99')END,'.',',')ASCredit,
            ''ASEcritureLet,
            ''ASDateLet,
            %sASValidDate,
            ''ASMontantdevise,
            ''ASIdevise,
            MIN(aa.id)ASCompteID
        FROM
            account_move_lineaml
            LEFTJOINaccount_moveamONam.id=aml.move_id
            JOINaccount_accountaaONaa.id=aml.account_id
            LEFTJOINaccount_account_typeaatONaa.user_type_id=aat.id
        WHERE
            am.date<%s
            ANDam.company_id=%s
            ANDaat.include_initial_balance='t'
        '''

        #Forofficialreport:onlyusepostedentries
        ifself.export_type=="official":
            sql_query+='''
            ANDam.state='posted'
            '''

        sql_query+='''
        GROUPBYaml.account_id,aat.type
        HAVINGaat.typenotin('receivable','payable')
        '''
        formatted_date_from=fields.Date.to_string(self.date_from).replace('-','')
        date_from=self.date_from
        formatted_date_year=date_from.year
        currency_digits=2

        self._cr.execute(
            sql_query,(formatted_date_year,formatted_date_from,formatted_date_from,formatted_date_from,self.date_from,company.id))

        forrowinself._cr.fetchall():
            listrow=list(row)
            account_id=listrow.pop()
            ifnotunaffected_earnings_line:
                account=self.env['account.account'].browse(account_id)
                ifaccount.user_type_id.id==self.env.ref('account.data_unaffected_earnings').id:
                    #addthebenefit/lossofpreviousfiscalyeartothefirstunaffectedearningsaccountfound.
                    unaffected_earnings_line=True
                    current_amount=float(listrow[11].replace(',','.'))-float(listrow[12].replace(',','.'))
                    unaffected_earnings_amount=float(unaffected_earnings_results[11].replace(',','.'))-float(unaffected_earnings_results[12].replace(',','.'))
                    listrow_amount=current_amount+unaffected_earnings_amount
                    iffloat_is_zero(listrow_amount,precision_digits=currency_digits):
                        continue
                    iflistrow_amount>0:
                        listrow[11]=str(listrow_amount).replace('.',',')
                        listrow[12]='0,00'
                    else:
                        listrow[11]='0,00'
                        listrow[12]=str(-listrow_amount).replace('.',',')
            rows_to_write.append(listrow)

        #iftheunaffectedearningsaccountwasn'tintheselectionyet:additmanually
        if(notunaffected_earnings_line
            andunaffected_earnings_results
            and(unaffected_earnings_results[11]!='0,00'
                 orunaffected_earnings_results[12]!='0,00')):
            #searchanunaffectedearningsaccount
            unaffected_earnings_account=self.env['account.account'].search([('user_type_id','=',self.env.ref('account.data_unaffected_earnings').id),
                                                                              ('company_id','=',company.id)],limit=1)
            ifunaffected_earnings_account:
                unaffected_earnings_results[4]=unaffected_earnings_account.code
                unaffected_earnings_results[5]=unaffected_earnings_account.name
            rows_to_write.append(unaffected_earnings_results)

        #INITIALBALANCE-receivable/payable
        sql_query='''
        SELECT
            'OUV'ASJournalCode,
            'Balanceinitiale'ASJournalLib,
            'OUVERTURE/'||%sASEcritureNum,
            %sASEcritureDate,
            MIN(aa.code)ASCompteNum,
            replace(MIN(aa.name),'|','/')ASCompteLib,
            CASEWHENMIN(aat.type)IN('receivable','payable')
            THEN
                CASEWHENrp.refISnullORrp.ref=''
                THENrp.id::text
                ELSEreplace(rp.ref,'|','/')
                END
            ELSE''
            END
            ASCompAuxNum,
            CASEWHENaat.typeIN('receivable','payable')
            THENCOALESCE(replace(rp.name,'|','/'),'')
            ELSE''
            ENDASCompAuxLib,
            '-'ASPieceRef,
            %sASPieceDate,
            '/'ASEcritureLib,
            replace(CASEWHENsum(aml.balance)<=0THEN'0,00'ELSEto_char(SUM(aml.balance),'000000000000000D99')END,'.',',')ASDebit,
            replace(CASEWHENsum(aml.balance)>=0THEN'0,00'ELSEto_char(-SUM(aml.balance),'000000000000000D99')END,'.',',')ASCredit,
            ''ASEcritureLet,
            ''ASDateLet,
            %sASValidDate,
            ''ASMontantdevise,
            ''ASIdevise,
            MIN(aa.id)ASCompteID
        FROM
            account_move_lineaml
            LEFTJOINaccount_moveamONam.id=aml.move_id
            LEFTJOINres_partnerrpONrp.id=aml.partner_id
            JOINaccount_accountaaONaa.id=aml.account_id
            LEFTJOINaccount_account_typeaatONaa.user_type_id=aat.id
        WHERE
            am.date<%s
            ANDam.company_id=%s
            ANDaat.include_initial_balance='t'
        '''

        #Forofficialreport:onlyusepostedentries
        ifself.export_type=="official":
            sql_query+='''
            ANDam.state='posted'
            '''

        sql_query+='''
        GROUPBYaml.account_id,aat.type,rp.ref,rp.id
        HAVINGaat.typein('receivable','payable')
        '''
        self._cr.execute(
            sql_query,(formatted_date_year,formatted_date_from,formatted_date_from,formatted_date_from,self.date_from,company.id))

        forrowinself._cr.fetchall():
            listrow=list(row)
            account_id=listrow.pop()
            rows_to_write.append(listrow)

        #LINES
        query_limit=int(self.env['ir.config_parameter'].sudo().get_param('l10n_fr_fec.batch_size',500000))#Topreventmemoryerrorswhenfetchingtheresults
        sql_query=f'''
        SELECT
            REGEXP_REPLACE(replace(aj.code,'|','/'),'[\\t\\r\\n]','','g')ASJournalCode,
            REGEXP_REPLACE(replace(COALESCE(aj__name.value,aj.name),'|','/'),'[\\t\\r\\n]','','g')ASJournalLib,
            REGEXP_REPLACE(replace(am.name,'|','/'),'[\\t\\r\\n]','','g')ASEcritureNum,
            TO_CHAR(am.date,'YYYYMMDD')ASEcritureDate,
            aa.codeASCompteNum,
            REGEXP_REPLACE(replace(aa.name,'|','/'),'[\\t\\r\\n]','','g')ASCompteLib,
            CASEWHENaat.typeIN('receivable','payable')
            THEN
                CASEWHENrp.refISnullORrp.ref=''
                THENrp.id::text
                ELSEreplace(rp.ref,'|','/')
                END
            ELSE''
            END
            ASCompAuxNum,
            CASEWHENaat.typeIN('receivable','payable')
            THENCOALESCE(REGEXP_REPLACE(replace(rp.name,'|','/'),'[\\t\\r\\n]','','g'),'')
            ELSE''
            ENDASCompAuxLib,
            CASEWHENam.refISnullORam.ref=''
            THEN'-'
            ELSEREGEXP_REPLACE(replace(am.ref,'|','/'),'[\\t\\r\\n]','','g')
            END
            ASPieceRef,
            TO_CHAR(COALESCE(am.invoice_date,am.date),'YYYYMMDD')ASPieceDate,
            CASEWHENaml.nameISNULLORaml.name=''THEN'/'
                WHENaml.nameSIMILARTO'[\\t|\\s|\\n]*'THEN'/'
                ELSEREGEXP_REPLACE(replace(aml.name,'|','/'),'[\\t\\n\\r]','','g')ENDASEcritureLib,
            replace(CASEWHENaml.debit=0THEN'0,00'ELSEto_char(aml.debit,'000000000000000D99')END,'.',',')ASDebit,
            replace(CASEWHENaml.credit=0THEN'0,00'ELSEto_char(aml.credit,'000000000000000D99')END,'.',',')ASCredit,
            CASEWHENrec.nameISNULLTHEN''ELSErec.nameENDASEcritureLet,
            CASEWHENaml.full_reconcile_idISNULLTHEN''ELSETO_CHAR(rec.create_date,'YYYYMMDD')ENDASDateLet,
            TO_CHAR(am.date,'YYYYMMDD')ASValidDate,
            CASE
                WHENaml.amount_currencyISNULLORaml.amount_currency=0THEN''
                ELSEreplace(to_char(aml.amount_currency,'000000000000000D99'),'.',',')
            ENDASMontantdevise,
            CASEWHENaml.currency_idISNULLTHEN''ELSErc.nameENDASIdevise
        FROM
            account_move_lineaml
            LEFTJOINaccount_moveamONam.id=aml.move_id
            LEFTJOINres_partnerrpONrp.id=aml.partner_id
            JOINaccount_journalajONaj.id=am.journal_id
            LEFTJOINir_translationaj__nameONaj__name.res_id=aj.id
                                             ANDaj__name.type='model'
                                             ANDaj__name.name='account.journal,name'
                                             ANDaj__name.lang=%s
                                             ANDaj__name.value!=''
            JOINaccount_accountaaONaa.id=aml.account_id
            LEFTJOINaccount_account_typeaatONaa.user_type_id=aat.id
            LEFTJOINres_currencyrcONrc.id=aml.currency_id
            LEFTJOINaccount_full_reconcilerecONrec.id=aml.full_reconcile_id
        WHERE
            am.date>=%s
            ANDam.date<=%s
            ANDam.company_id=%s
            {"ANDam.state='posted'"ifself.export_type=='official'else""}
        ORDERBY
            am.date,
            am.name,
            aml.id
        LIMIT%s
        OFFSET%s
        '''

        lang=self.env.user.langorget_lang(self.env).code

        withio.BytesIO()asfecfile:
            csv_writer=pycompat.csv_writer(fecfile,delimiter='|',lineterminator='')

            #Writeheaderandinitialbalances
            forinitial_rowinrows_to_write:
                initial_row=list(initial_row)
                #Wedon'tskip\natthenendofthefileifthereareonlyinitialbalances,forsimplicity.Anemptyperiodexportshouldn'thappenIRL.
                initial_row[-1]+=u'\r\n'
                csv_writer.writerow(initial_row)

            #Writecurrentperiod'sdata
            query_offset=0
            has_more_results=True
            whilehas_more_results:
                self._cr.execute(
                    sql_query,
                    (lang,self.date_from,self.date_to,company.id,query_limit+1,query_offset)
                )
                query_offset+=query_limit
                has_more_results=self._cr.rowcount>query_limit#weloadonemoreresultthanthelimittocheckifthereismore
                query_results=self._cr.fetchall()
                fori,rowinenumerate(query_results[:query_limit]):
                    ifi<len(query_results)-1:
                        #Thefileisnotallowedtoendwithanemptyline,sowecan'tuselineterminatoronthewriter
                        row=list(row)
                        row[-1]+=u'\r\n'
                    csv_writer.writerow(row)

            base64_result=base64.encodebytes(fecfile.getvalue())

        end_date=fields.Date.to_string(self.date_to).replace('-','')
        suffix=''
        ifself.export_type=="nonofficial":
            suffix='-NONOFFICIAL'

        self.write({
            'fec_data':base64_result,
            #Filename=<siren>FECYYYYMMDDwhereYYYMMDDistheclosingdate
            'filename':'%sFEC%s%s.csv'%(company_legal_data,end_date,suffix),
            })

        #Setfiscalyearlockdatetotheenddate(notintest)
        fiscalyear_lock_date=self.env.company.fiscalyear_lock_date
        ifnotself.test_fileand(notfiscalyear_lock_dateorfiscalyear_lock_date<self.date_to):
            self.env.company.write({'fiscalyear_lock_date':self.date_to})
        return{
            'name':'FEC',
            'type':'ir.actions.act_url',
            'url':"web/content/?model=account.fr.fec&id="+str(self.id)+"&filename_field=filename&field=fec_data&download=true&filename="+self.filename,
            'target':'self',
        }

    def_csv_write_rows(self,rows,lineterminator=u'\r\n'):#DEPRECATED;willdisappearinmaster
        """
        WriteFECrowsintoafile
        ItseemsthatBercy'sbureaucracyisnottoohappyaboutthe
        emptynewlineattheEndOfFile.

        @param{list(list)}rows:thelistofrows.Eachrowisalistofstrings
        @param{unicodestring}[optional]lineterminator:effectivelineterminator
            Hasnothingtodowiththecsvwriterparameter
            Thelastlinewrittenwon'tbeterminatedwithit

        @returnthevalueofthefile
        """
        fecfile=io.BytesIO()
        writer=pycompat.csv_writer(fecfile,delimiter='|',lineterminator='')

        rows_length=len(rows)
        fori,rowinenumerate(rows):
            ifnoti==rows_length-1:
                row[-1]+=lineterminator
            writer.writerow(row)

        fecvalue=fecfile.getvalue()
        fecfile.close()
        returnfecvalue
