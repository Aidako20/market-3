fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classAccountTaxReport(models.Model):
    _name="account.tax.report"
    _description='AccountTaxReport'
    _order='country_id,name'

    name=fields.Char(string="Name",required=True,help="Nameofthistaxreport")
    country_id=fields.Many2one(string="Country",comodel_name='res.country',required=True,default=lambdax:x.env.company.country_id.id,help="Countryforwhichthisreportisavailable.")
    line_ids=fields.One2many(string="ReportLines",comodel_name='account.tax.report.line',inverse_name='report_id',help="Contentofthistaxreport")
    root_line_ids=fields.One2many(string="RootReportLines",comodel_name='account.tax.report.line',inverse_name='report_id',domain=[('parent_id','=',None)],help="Subsetofline_ids,containingthelinesattherootofthereport.")

    defwrite(self,vals):
        #Overriddensothatwechangethecountry_idoftheexistingtags
        #whenwritingthecountry_idofthereport,orcreatenewtags
        #forthenewcountryifthetagsaresharedwithsomeotherreport.

        if'country_id'invals:
            tags_cache={}
            forrecordinself.filtered(lambdax:x.country_id.id!=vals['country_id']):
                forlineinrecord.line_ids:
                    ifline.tag_ids:
                        #Thetagsforthiscountrymayhavebeencreatedbyapreviouslineinthisloop
                        cache_key=(vals['country_id'],line.tag_name)
                        ifcache_keynotintags_cache:
                            tags_cache[cache_key]=self.env['account.account.tag']._get_tax_tags(line.tag_name,vals['country_id'])

                        new_tags=tags_cache[cache_key]

                        iflen(new_tags)==2:
                            line._remove_tags_used_only_by_self()
                            line.write({'tag_ids':[(6,0,new_tags.ids)]})

                        elifline.mapped('tag_ids.tax_report_line_ids.report_id').filtered(lambdax:xnotinself):
                            line._remove_tags_used_only_by_self()
                            line.write({'tag_ids':[(5,0,0)]+line._get_tags_create_vals(line.tag_name,vals['country_id'],existing_tag=new_tags)})
                            tags_cache[cache_key]=line.tag_ids

                        else:
                            line.tag_ids.write({'country_id':vals['country_id']})

        returnsuper(AccountTaxReport,self).write(vals)

    defcopy(self,default=None):
        #Overriddenfromregularcopy,sincetheORMdoesnotmanage
        #thecopyofthelineshierarchyproperly(alltheparent_idfields
        #needtobereassignedtothecorrespondingcopies).

        copy_default={k:vfork,vindefault.items()ifk!='line_ids'}ifdefaultelseNone
        copied_report=super(AccountTaxReport,self).copy(default=copy_default)#Thiscopiesthereportwithoutitslines

        lines_map={}#mapsoriginallinestotheircopies(usingids)
        forlineinself.get_lines_in_hierarchy():
            copy=line.copy({'parent_id':lines_map.get(line.parent_id.id,None),'report_id':copied_report.id})
            lines_map[line.id]=copy.id

        returncopied_report

    defget_lines_in_hierarchy(self):
        """Returnsaninteratortothelinesofthistaxreport,wereparentlines
        aralldirectlyfollowedbytheirchildren.
        """
        self.ensure_one()
        lines_to_treat=list(self.line_ids.filtered(lambdax:notx.parent_id))#Usedasastack,whoseindex0isthetop
        whilelines_to_treat:
            to_yield=lines_to_treat[0]
            lines_to_treat=list(to_yield.children_line_ids)+lines_to_treat[1:]
            yieldto_yield

    defget_checks_to_perform(self,d):
        """Tooverrideinlocalizations
        Ifvalueisafloat,itwillbeformattedwithformat_value
        Thelineisnotdisplayedifitisfalsy(0,0.0,False,...)
        :paramd:themappingdictionaybetweencodesandvalues
        :return:iterableoftuple(name,value)
        """
        self.ensure_one()
        return[]

    defvalidate_country_id(self):
        forrecordinself:
            ifany(line.tag_ids.mapped('country_id')!=record.country_idforlineinrecord.line_ids):
                raiseValidationError(_("Thetagsassociatedwithtaxreportlineobjectsshouldallhavethesamecountrysetasthetaxreportcontainingtheselines."))


classAccountTaxReportLine(models.Model):
    _name="account.tax.report.line"
    _description='AccountTaxReportLine'
    _order='sequence,id'
    _parent_store=True

    name=fields.Char(string="Name",required=True,help="Completenameforthisreportline,tobeusedinreport.")
    tag_ids=fields.Many2many(string="Tags",comodel_name='account.account.tag',relation='account_tax_report_line_tags_rel',help="Taxtagspopulatingthisline")
    report_action_id=fields.Many2one(string="ReportAction",comodel_name='ir.actions.act_window',help="Theoptionalactiontocallwhenclickingonthislineinaccountingreports.")
    children_line_ids=fields.One2many(string="ChildrenLines",comodel_name='account.tax.report.line',inverse_name='parent_id',help="Linesthatshouldberenderedaschildrenofthisone")
    parent_id=fields.Many2one(string="ParentLine",comodel_name='account.tax.report.line')
    sequence=fields.Integer(string='Sequence',required=True,
        help="Sequencedeterminingtheorderofthelinesinthereport(smalleronescomefirst).Thisorderisappliedlocallypersection(so,childrenofthesamelinearealwaysrenderedoneaftertheother).")
    parent_path=fields.Char(index=True)
    report_id=fields.Many2one(string="TaxReport",required=True,comodel_name='account.tax.report',ondelete='cascade',help="Theparenttaxreportofthisline")

    #helpertocreatetags(positiveandnegative)onreportlinecreation
    tag_name=fields.Char(string="TagName",help="Shortnameforthetaxgridcorrespondingtothisreportline.Leaveemptyifthisreportlineshouldnotcorrespondtoanysuchgrid.")

    #fieldsusedinspecificlocalizationreports,whereareportlineisn'tsimplythegivenbythesumofaccount.move.linewithselectedtags
    code=fields.Char(string="Code",help="Optionaluniquecodetorefertothislineintotalformulas")
    formula=fields.Char(string="Formula",help="Pythonexpressionusedtocomputethevalueofatotalline.Thisfieldismutuallyexclusivewithtag_name,settingitturnsthelinetoatotalline.Taxreportlinecodescanbeusedasvariablesinthisexpressiontorefertothebalanceofthecorrespondinglinesinthereport.Aformulacannotrefertoanotherlineusingaformula.")

    @api.model
    defcreate(self,vals):
        #Managetags
        tag_name=vals.get('tag_name','')
        iftag_nameandvals.get('report_id'):
            report=self.env['account.tax.report'].browse(vals['report_id'])
            country=report.country_id

            existing_tags=self.env['account.account.tag']._get_tax_tags(tag_name,country.id)

            iflen(existing_tags)<2:
                #Wecreatenewone(s)
                #Wecanhaveonlyonetagincasewearchiveditanddeleteditsunusedcomplementsign
                vals['tag_ids']=self._get_tags_create_vals(tag_name,country.id,existing_tag=existing_tags)
            else:
                #Weconnectthenewreportlinetothealreadyexistingtags
                vals['tag_ids']=[(6,0,existing_tags.ids)]

        returnsuper(AccountTaxReportLine,self).create(vals)

    @api.model
    def_get_tags_create_vals(self,tag_name,country_id,existing_tag=None):
        """
            Wecreatetheplusandminustagswithtag_name.
            Incasethereisanexisting_tag(whichcanhappenifwedeleteditsunusedcomplementsign)
            weonlyrecreatethemissingsign.
        """
        minus_tag_vals={
          'name':'-'+tag_name,
          'applicability':'taxes',
          'tax_negate':True,
          'country_id':country_id,
        }
        plus_tag_vals={
          'name':'+'+tag_name,
          'applicability':'taxes',
          'tax_negate':False,
          'country_id':country_id,
        }
        res=[]
        ifnotexisting_tagornotexisting_tag.tax_negate:
            res.append((0,0,minus_tag_vals))
        ifnotexisting_tagorexisting_tag.tax_negate:
            res.append((0,0,plus_tag_vals))
        returnres

    defwrite(self,vals):
        #Iftag_namewasset,butnottag_ids,wepostponethewriteof
        #tag_name,andperformitonlyafterhavinggenerated/retrievedthetags.
        #Otherwise,tag_nameandtags'namewouldnotmatch,breaking
        #_validate_tagsconstaint.
        postponed_vals={}

        if'tag_name'invalsand'tag_ids'notinvals:
            postponed_vals={'tag_name':vals.pop('tag_name')}
            tag_name_postponed=postponed_vals['tag_name']
            #iftag_nameisposponedthenwealsopostponeformulatoavoid
            #breaking_validate_formulaconstraint
            if'formula'invals:
                postponed_vals['formula']=vals.pop('formula')

        rslt=super(AccountTaxReportLine,self).write(vals)

        ifpostponed_vals:
            #Iftag_namemodificationhasbeenpostponed,
            #weneedtosearchforexistingtagscorrespondingtothenewtagname
            #(orcreatethemiftheydon'texistyet)andassignthemtotherecords

            records_by_country={}
            forrecordinself.filtered(lambdax:x.tag_name!=tag_name_postponed):
                records_by_country[record.report_id.country_id.id]=records_by_country.get(record.report_id.country_id.id,self.env['account.tax.report.line'])+record

            forcountry_id,recordsinrecords_by_country.items():
                iftag_name_postponed:
                    record_tag_names=records.mapped('tag_name')
                    iflen(record_tag_names)==1andrecord_tag_names[0]:
                        #Ifalltherecordsalreadyhavethesametag_namebeforewriting,
                        #wesimplywanttochangethenameoftheexistingtags
                        to_update=records.mapped('tag_ids.tax_report_line_ids')
                        tags_to_update=to_update.mapped('tag_ids')
                        minus_child_tags=tags_to_update.filtered(lambdax:x.tax_negate)
                        minus_child_tags.write({'name':'-'+tag_name_postponed})
                        plus_child_tags=tags_to_update.filtered(lambdax:notx.tax_negate)
                        plus_child_tags.write({'name':'+'+tag_name_postponed})
                        super(AccountTaxReportLine,to_update).write(postponed_vals)

                    else:
                        existing_tags=self.env['account.account.tag']._get_tax_tags(tag_name_postponed,country_id)
                        records_to_link=records
                        tags_to_remove=self.env['account.account.tag']

                        iflen(existing_tags)<2andrecords_to_link:
                            #Ifthetagdoesnotexistyet(orifweonlyhaveoneofthetwo+/-),
                            #wefirstcreateitbylinkingittothefirstreportlineoftherecordset
                            first_record=records_to_link[0]
                            tags_to_remove+=first_record.tag_ids
                            first_record.write({**postponed_vals,'tag_ids':[(5,0,0)]+self._get_tags_create_vals(tag_name_postponed,country_id,existing_tag=existing_tags)})
                            existing_tags=first_record.tag_ids
                            records_to_link-=first_record

                        #Allthelinessharingtheirtagsmustalwaysbesynchronized,
                        tags_to_remove+=records_to_link.mapped('tag_ids')
                        records_to_link=tags_to_remove.mapped('tax_report_line_ids')
                        tags_to_remove.mapped('tax_report_line_ids')._remove_tags_used_only_by_self()
                        records_to_link.write({**postponed_vals,'tag_ids':[(2,tag.id)fortagintags_to_remove]+[(6,0,existing_tags.ids)]})

                else:
                    #tag_namewassetempty,soweremovethetagsoncurrentlines
                    #Ifsometagsarestillreferencedbyotherreportlines,
                    #wekeepthem;else,wedeletethemfromDB
                    line_tags=records.mapped('tag_ids')
                    other_lines_same_tag=line_tags.mapped('tax_report_line_ids').filtered(lambdax:xnotinrecords)
                    ifnotother_lines_same_tag:
                        self._delete_tags_from_taxes(line_tags.ids)
                    orm_cmd_code=other_lines_same_tagand3or2
                    records.write({**postponed_vals,'tag_ids':[(orm_cmd_code,tag.id)fortaginline_tags]})

        returnrslt

    defunlink(self):
        self._remove_tags_used_only_by_self()
        children=self.mapped('children_line_ids')
        ifchildren:
            children.unlink()
        returnsuper(AccountTaxReportLine,self).unlink()

    def_remove_tags_used_only_by_self(self):
        """Deletesandremovesfromtaxesandmovelinesallthe
        tagsfromtheprovidedtaxreportlinesthatarenotlinked
        toanyothertaxreportlinesnormovelines.
        Thetagsthatareusedbyatleastonemovelinewillbearchivedinstead,toavoidloosinghistory.
        """
        all_tags=self.mapped('tag_ids')
        tags_to_unlink=all_tags.filtered(lambdax:not(x.tax_report_line_ids-self))
        self.write({'tag_ids':[(3,tag.id,0)fortagintags_to_unlink]})

        fortagintags_to_unlink:
            aml_using_tags=self.env['account.move.line'].sudo().search([('tax_tag_ids','in',tag.id)],limit=1)
            #ifthetagisstillreferencedinmovelineswearchivethetag,elsewedeleteit.
            ifaml_using_tags:
                rep_lines_with_archived_tags=self.env['account.tax.repartition.line'].sudo().search([('tag_ids','in',tag.id)])
                rep_lines_with_archived_tags.write({'tag_ids':[(3,tag.id)]})
                tag.active=False
            else:
                self._delete_tags_from_taxes([tag.id])

    @api.model
    def_delete_tags_from_taxes(self,tag_ids_to_delete):
        """Basedonalistoftagids,removesthemfirstfromthe
        repartitionlinestheyarelinkedto,thendeletesthem
        fromtheaccountmovelines,andfinallyunlinkthem.
        """
        ifnottag_ids_to_delete:
            #Nothingtodo,then!
            return

        self.env.cr.execute("""
            deletefromaccount_account_tag_account_tax_repartition_line_rel
            whereaccount_account_tag_idin%(tag_ids_to_delete)s;

            deletefromaccount_account_tag_account_move_line_rel
            whereaccount_account_tag_idin%(tag_ids_to_delete)s;
        """,{'tag_ids_to_delete':tuple(tag_ids_to_delete)})

        self.env['account.move.line'].invalidate_cache(fnames=['tax_tag_ids'])
        self.env['account.tax.repartition.line'].invalidate_cache(fnames=['tag_ids'])

        self.env['account.account.tag'].browse(tag_ids_to_delete).unlink()

    @api.constrains('formula','tag_name')
    def_validate_formula(self):
        forrecordinself:
            ifrecord.formulaandrecord.tag_name:
                raiseValidationError(_("Tagnameandformulaaremutuallyexclusive,theyshouldnotbesettogetheronthesametaxreportline."))

    @api.constrains('tag_name','tag_ids')
    def_validate_tags(self):
        forrecordinself.filtered(lambdax:x.tag_ids):
            neg_tags=record.tag_ids.filtered(lambdax:x.tax_negate)
            pos_tags=record.tag_ids.filtered(lambdax:notx.tax_negate)

            if(len(neg_tags)>1orlen(pos_tags)>1):
                raiseValidationError(_("Iftagsaredefinedforataxreportline,onlytwoareallowedonit:apositiveand/oranegativeone."))

            if(neg_tagsandneg_tags.name!='-'+record.tag_name)or(pos_tagsandpos_tags.name!='+'+record.tag_name):
                raiseValidationError(_("Thetagslinkedtoataxreportlineshouldalwaysmatchitstagname."))
