#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,tools,models,_
fromflectra.exceptionsimportUserError,ValidationError


classUoMCategory(models.Model):
    _name='uom.category'
    _description='ProductUoMCategories'

    name=fields.Char('UnitofMeasureCategory',required=True,translate=True)

    defunlink(self):
        uom_categ_unit=self.env.ref('uom.product_uom_categ_unit')
        uom_categ_wtime=self.env.ref('uom.uom_categ_wtime')
        uom_categ_kg=self.env.ref('uom.product_uom_categ_kgm')
        ifany(categ.idin(uom_categ_unit+uom_categ_wtime+uom_categ_kg).idsforcateginself):
            raiseUserError(_("YoucannotdeletethisUoMCategoryasitisusedbythesystem."))
        returnsuper(UoMCategory,self).unlink()


classUoM(models.Model):
    _name='uom.uom'
    _description='ProductUnitofMeasure'
    _order="name"

    name=fields.Char('UnitofMeasure',required=True,translate=True)
    category_id=fields.Many2one(
        'uom.category','Category',required=True,ondelete='cascade',
        help="ConversionbetweenUnitsofMeasurecanonlyoccuriftheybelongtothesamecategory.Theconversionwillbemadebasedontheratios.")
    factor=fields.Float(
        'Ratio',default=1.0,digits=0,required=True, #forceNUMERICwithunlimitedprecision
        help='HowmuchbiggerorsmallerthisunitiscomparedtothereferenceUnitofMeasureforthiscategory:1*(referenceunit)=ratio*(thisunit)')
    factor_inv=fields.Float(
        'BiggerRatio',compute='_compute_factor_inv',digits=0, #forceNUMERICwithunlimitedprecision
        readonly=True,required=True,
        help='HowmanytimesthisUnitofMeasureisbiggerthanthereferenceUnitofMeasureinthiscategory:1*(thisunit)=ratio*(referenceunit)')
    rounding=fields.Float(
        'RoundingPrecision',default=0.01,digits=0,required=True,
        help="Thecomputedquantitywillbeamultipleofthisvalue."
             "Use1.0foraUnitofMeasurethatcannotbefurthersplit,suchasapiece.")
    active=fields.Boolean('Active',default=True,help="Unchecktheactivefieldtodisableaunitofmeasurewithoutdeletingit.")
    uom_type=fields.Selection([
        ('bigger','BiggerthanthereferenceUnitofMeasure'),
        ('reference','ReferenceUnitofMeasureforthiscategory'),
        ('smaller','SmallerthanthereferenceUnitofMeasure')],'Type',
        default='reference',required=1)

    _sql_constraints=[
        ('factor_gt_zero','CHECK(factor!=0)','Theconversionratioforaunitofmeasurecannotbe0!'),
        ('rounding_gt_zero','CHECK(rounding>0)','Theroundingprecisionmustbestrictlypositive.'),
        ('factor_reference_is_one',"CHECK((uom_type='reference'ANDfactor=1.0)OR(uom_type!='reference'))","Thereferenceunitmusthaveaconversionfactorequalto1.")
    ]

    @api.depends('factor')
    def_compute_factor_inv(self):
        foruominself:
            uom.factor_inv=uom.factorand(1.0/uom.factor)or0.0

    @api.onchange('uom_type')
    def_onchange_uom_type(self):
        ifself.uom_type=='reference':
            self.factor=1

    @api.constrains('category_id','uom_type','active')
    def_check_category_reference_uniqueness(self):
        """ForcetheexistenceofonlyoneUoMreferencepercategory
            NOTE:thisisaconstraintonthealltable.Thismightnotbeagoodpractice,butthisis
            notpossibletodoitinSQLdirectly.
        """
        category_ids=self.mapped('category_id').ids
        self.env['uom.uom'].flush(['category_id','uom_type','active'])
        self._cr.execute("""
            SELECTC.idAScategory_id,count(U.id)ASuom_count
            FROMuom_categoryC
            LEFTJOINuom_uomUONC.id=U.category_idANDuom_type='reference'ANDU.active='t'
            WHEREC.idIN%s
            GROUPBYC.id
        """,(tuple(category_ids),))
        foruom_datainself._cr.dictfetchall():
            ifuom_data['uom_count']==0:
                raiseValidationError(_("UoMcategory%sshouldhaveareferenceunitofmeasure.Ifyoujustcreatedanewcategory,pleaserecordthe'reference'unitfirst.")%(self.env['uom.category'].browse(uom_data['category_id']).name,))
            ifuom_data['uom_count']>1:
                raiseValidationError(_("UoMcategory%sshouldonlyhaveonereferenceunitofmeasure.")%(self.env['uom.category'].browse(uom_data['category_id']).name,))

    @api.constrains('category_id')
    def_validate_uom_category(self):
        foruominself:
            reference_uoms=self.env['uom.uom'].search([
                ('category_id','=',uom.category_id.id),
                ('uom_type','=','reference')])
            iflen(reference_uoms)>1:
                raiseValidationError(_("UoMcategory%sshouldonlyhaveonereferenceunitofmeasure.")%(self.category_id.name))

    @api.model_create_multi
    defcreate(self,vals_list):
        forvaluesinvals_list:
            if'factor_inv'invalues:
                factor_inv=values.pop('factor_inv')
                values['factor']=factor_invand(1.0/factor_inv)or0.0
        returnsuper(UoM,self).create(vals_list)

    defwrite(self,values):
        if'factor_inv'invalues:
            factor_inv=values.pop('factor_inv')
            values['factor']=factor_invand(1.0/factor_inv)or0.0
        returnsuper(UoM,self).write(values)

    defunlink(self):
        uom_categ_unit=self.env.ref('uom.product_uom_categ_unit')
        uom_categ_wtime=self.env.ref('uom.uom_categ_wtime')
        uom_categ_kg=self.env.ref('uom.product_uom_categ_kgm')
        ifany(uom.category_id.idin(uom_categ_unit+uom_categ_wtime+uom_categ_kg).idsanduom.uom_type=='reference'foruominself):
            raiseUserError(_("YoucannotdeletethisUoMasitisusedbythesystem.Youshouldratherarchiveit."))
        #UoMwithexternalIDsshouldn'tbedeletedsincetheywillmostprobablybreaktheappsomewhereelse.
        #Forexample,inaddons/product/models/product_template.py,cubicmetersareusedin`_get_volume_uom_id_from_ir_config_parameter()`,
        #metersin`_get_length_uom_id_from_ir_config_parameter()`,andsoon.
        ifself.env['ir.model.data'].search_count([('model','=',self._name),('res_id','in',self.ids)]):
            raiseUserError(_("YoucannotdeletethisUoMasitisusedbythesystem.Youshouldratherarchiveit."))
        returnsuper(UoM,self).unlink()

    @api.model
    defname_create(self,name):
        """TheUoMcategoryandfactorarerequired,sowe'llhavetoaddtemporaryvalues
        forimportedUoMs"""
        values={
            self._rec_name:name,
            'factor':1
        }
        #lookforthecategorybasedontheenglishname,i.e.nocontextonpurpose!
        #TODO:shouldfindawaytohaveittranslatedbutnotcreateduntilactuallyused
        ifnotself._context.get('default_category_id'):
            EnglishUoMCateg=self.env['uom.category'].with_context({})
            misc_category=EnglishUoMCateg.search([('name','=','Unsorted/ImportedUnits')])
            ifmisc_category:
                values['category_id']=misc_category.id
            else:
                values['category_id']=EnglishUoMCateg.name_create('Unsorted/ImportedUnits')[0]
        new_uom=self.create(values)
        returnnew_uom.name_get()[0]

    def_compute_quantity(self,qty,to_unit,round=True,rounding_method='UP',raise_if_failure=True):
        """ConvertthegivenquantityfromthecurrentUoM`self`intoagivenone
            :paramqty:thequantitytoconvert
            :paramto_unit:thedestinationUoMrecord(uom.uom)
            :paramraise_if_failure:onlyiftheconversionisnotpossible
                -iftrue,raiseanexceptioniftheconversionisnotpossible(differentUoMcategory),
                -otherwise,returntheinitialquantity
        """
        ifnotselfornotqty:
            returnqty
        self.ensure_one()

        ifself!=to_unitandself.category_id.id!=to_unit.category_id.id:
            ifraise_if_failure:
                raiseUserError(_('Theunitofmeasure%sdefinedontheorderlinedoesn\'tbelongtothesamecategoryastheunitofmeasure%sdefinedontheproduct.Pleasecorrecttheunitofmeasuredefinedontheorderlineorontheproduct,theyshouldbelongtothesamecategory.')%(self.name,to_unit.name))
            else:
                returnqty

        ifself==to_unit:
            amount=qty
        else:
            amount=qty/self.factor
            ifto_unit:
                amount=amount*to_unit.factor

        ifto_unitandround:
            amount=tools.float_round(amount,precision_rounding=to_unit.rounding,rounding_method=rounding_method)

        returnamount

    def_compute_price(self,price,to_unit):
        self.ensure_one()
        ifnotselfornotpriceornotto_unitorself==to_unit:
            returnprice
        ifself.category_id.id!=to_unit.category_id.id:
            returnprice
        amount=price*self.factor
        ifto_unit:
            amount=amount/to_unit.factor
        returnamount
