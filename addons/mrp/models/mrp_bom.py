#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.toolsimportfloat_round

fromitertoolsimportgroupby
fromcollectionsimportdefaultdict


classMrpBom(models.Model):
    """Definesbillsofmaterialforaproductoraproducttemplate"""
    _name='mrp.bom'
    _description='BillofMaterial'
    _inherit=['mail.thread']
    _rec_name='product_tmpl_id'
    _order="sequence"
    _check_company_auto=True

    def_get_default_product_uom_id(self):
        returnself.env['uom.uom'].search([],limit=1,order='id').id

    code=fields.Char('Reference')
    active=fields.Boolean(
        'Active',default=True,
        help="IftheactivefieldissettoFalse,itwillallowyoutohidethebillsofmaterialwithoutremovingit.")
    type=fields.Selection([
        ('normal','Manufacturethisproduct'),
        ('phantom','Kit')],'BoMType',
        default='normal',required=True)
    product_tmpl_id=fields.Many2one(
        'product.template','Product',
        check_company=True,index=True,
        domain="[('type','in',['product','consu']),'|',('company_id','=',False),('company_id','=',company_id)]",required=True)
    product_id=fields.Many2one(
        'product.product','ProductVariant',
        check_company=True,index=True,
        domain="['&',('product_tmpl_id','=',product_tmpl_id),('type','in',['product','consu']), '|',('company_id','=',False),('company_id','=',company_id)]",
        help="IfaproductvariantisdefinedtheBOMisavailableonlyforthisproduct.")
    bom_line_ids=fields.One2many('mrp.bom.line','bom_id','BoMLines',copy=True)
    byproduct_ids=fields.One2many('mrp.bom.byproduct','bom_id','By-products',copy=True)
    product_qty=fields.Float(
        'Quantity',default=1.0,
        digits='UnitofMeasure',required=True)
    product_uom_id=fields.Many2one(
        'uom.uom','UnitofMeasure',
        default=_get_default_product_uom_id,required=True,
        help="UnitofMeasure(UnitofMeasure)istheunitofmeasurementfortheinventorycontrol",domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_tmpl_id.uom_id.category_id')
    sequence=fields.Integer('Sequence',help="Givesthesequenceorderwhendisplayingalistofbillsofmaterial.")
    operation_ids=fields.One2many('mrp.routing.workcenter','bom_id','Operations',copy=True)
    ready_to_produce=fields.Selection([
        ('all_available','Whenallcomponentsareavailable'),
        ('asap','Whencomponentsfor1stoperationareavailable')],string='ManufacturingReadiness',
        default='asap',help="DefineswhenaManufacturingOrderisconsideredasreadytobestarted",required=True)
    picking_type_id=fields.Many2one(
        'stock.picking.type','OperationType',domain="[('code','=','mrp_operation'),('company_id','=',company_id)]",
        check_company=True,
        help=u"Whenaprocurementhasa‘produce’routewithaoperationtypeset,itwilltrytocreate"
             "aManufacturingOrderforthatproductusingaBoMofthesameoperationtype.Thatallows"
             "todefinestockruleswhichtriggerdifferentmanufacturingorderswithdifferentBoMs.")
    company_id=fields.Many2one(
        'res.company','Company',index=True,
        default=lambdaself:self.env.company)
    consumption=fields.Selection([
        ('flexible','Allowed'),
        ('warning','Allowedwithwarning'),
        ('strict','Blocked')],
        help="DefinesifyoucanconsumemoreorlesscomponentsthanthequantitydefinedontheBoM:\n"
             " *Allowed:allowedforallmanufacturingusers.\n"
             " *Allowedwithwarning:allowedforallmanufacturinguserswithsummaryofconsumptiondifferenceswhenclosingthemanufacturingorder.\n"
             " *Blocked:onlyamanagercancloseamanufacturingorderwhentheBoMconsumptionisnotrespected.",
        default='warning',
        string='FlexibleConsumption',
        required=True
    )

    _sql_constraints=[
        ('qty_positive','check(product_qty>0)','Thequantitytoproducemustbepositive!'),
    ]

    @api.onchange('product_id')
    defonchange_product_id(self):
        ifself.product_id:
            forlineinself.bom_line_ids:
                line.bom_product_template_attribute_value_ids=False

    @api.constrains('product_id','product_tmpl_id','bom_line_ids')
    def_check_bom_lines(self):
        forbominself:
            forbom_lineinbom.bom_line_ids:
                ifbom.product_id:
                    same_product=bom.product_id==bom_line.product_id
                else:
                    same_product=bom.product_tmpl_id==bom_line.product_id.product_tmpl_id
                ifsame_product:
                    raiseValidationError(_("BoMlineproduct%sshouldnotbethesameasBoMproduct.")%bom.display_name)
                ifbom.product_idandbom_line.bom_product_template_attribute_value_ids:
                    raiseValidationError(_("BoMcannotconcernproduct%sandhavealinewithattributes(%s)atthesametime.")
                        %(bom.product_id.display_name,",".join([ptav.display_nameforptavinbom_line.bom_product_template_attribute_value_ids])))
                forptavinbom_line.bom_product_template_attribute_value_ids:
                    ifptav.product_tmpl_id!=bom.product_tmpl_id:
                        raiseValidationError(_(
                            "Theattributevalue%(attribute)ssetonproduct%(product)sdoesnotmatchtheBoMproduct%(bom_product)s.",
                            attribute=ptav.display_name,
                            product=ptav.product_tmpl_id.display_name,
                            bom_product=bom_line.parent_product_tmpl_id.display_name
                        ))

    @api.onchange('bom_line_ids','product_qty')
    defonchange_bom_structure(self):
        ifself.type=='phantom'andself._originandself.env['stock.move'].search([('bom_line_id','in',self._origin.bom_line_ids.ids)],limit=1):
            return{
                'warning':{
                    'title':_('Warning'),
                    'message':_(
                        'Theproducthasalreadybeenusedatleastonce,editingitsstructuremayleadtoundesirablebehaviours.'
                        'Youshouldratherarchivetheproductandcreateanewonewithanewbillofmaterials.'),
                }
            }

    @api.onchange('product_uom_id')
    defonchange_product_uom_id(self):
        res={}
        ifnotself.product_uom_idornotself.product_tmpl_id:
            return
        ifself.product_uom_id.category_id.id!=self.product_tmpl_id.uom_id.category_id.id:
            self.product_uom_id=self.product_tmpl_id.uom_id.id
            res['warning']={'title':_('Warning'),'message':_('TheProductUnitofMeasureyouchosehasadifferentcategorythanintheproductform.')}
        returnres

    @api.onchange('product_tmpl_id')
    defonchange_product_tmpl_id(self):
        ifself.product_tmpl_id:
            self.product_uom_id=self.product_tmpl_id.uom_id.id
            ifself.product_id.product_tmpl_id!=self.product_tmpl_id:
                self.product_id=False
            forlineinself.bom_line_ids:
                line.bom_product_template_attribute_value_ids=False

    defcopy(self,default=None):
        res=super().copy(default)
        forbom_lineinres.bom_line_ids:
            ifbom_line.operation_id:
                operation=res.operation_ids.filtered(lambdaop:op._get_comparison_values()==bom_line.operation_id._get_comparison_values())
                #Twooperationscouldhavethesamevaluessowetakethefirstone
                bom_line.operation_id=operation[:1]
        returnres

    @api.model
    defname_create(self,name):
        #preventtousestringasproduct_tmpl_id
        ifisinstance(name,str):
            raiseUserError(_("YoucannotcreateanewBillofMaterialfromhere."))
        returnsuper(MrpBom,self).name_create(name)

    defname_get(self):
        return[(bom.id,'%s%s'%(bom.codeand'%s:'%bom.codeor'',bom.product_tmpl_id.display_name))forbominself]

    @api.constrains('product_tmpl_id','product_id','type')
    defcheck_kit_has_not_orderpoint(self):
        product_ids=[pidforbominself.filtered(lambdabom:bom.type=="phantom")
                           forpidin(bom.product_id.idsorbom.product_tmpl_id.product_variant_ids.ids)]
        ifself.env['stock.warehouse.orderpoint'].search([('product_id','in',product_ids)],count=True):
            raiseValidationError(_("Youcannotcreateakit-typebillofmaterialsforproductsthathaveatleastonereorderingrule."))

    defunlink(self):
        ifself.env['mrp.production'].search([('bom_id','in',self.ids),('state','notin',['done','cancel'])],limit=1):
            raiseUserError(_('YoucannotdeleteaBillofMaterialwithrunningmanufacturingorders.\nPleasecloseorcancelitfirst.'))
        returnsuper(MrpBom,self).unlink()

    @api.model
    def_bom_find_domain(self,product_tmpl=None,product=None,picking_type=None,company_id=False,bom_type=False):
        ifproduct:
            ifnotproduct_tmpl:
                product_tmpl=product.product_tmpl_id
            domain=['|',('product_id','=',product.id),'&',('product_id','=',False),('product_tmpl_id','=',product_tmpl.id)]
        elifproduct_tmpl:
            domain=[('product_tmpl_id','=',product_tmpl.id)]
        else:
            #neitherproductnortemplate,makesnosensetosearch
            raiseUserError(_('YoushouldprovideeitheraproductoraproducttemplatetosearchaBoM'))
        ifpicking_type:
            domain+=['|',('picking_type_id','=',picking_type.id),('picking_type_id','=',False)]
        ifcompany_idorself.env.context.get('company_id'):
            domain=domain+['|',('company_id','=',False),('company_id','=',company_idorself.env.context.get('company_id'))]
        ifbom_type:
            domain+=[('type','=',bom_type)]
        #ordertoprioritizebomwithproduct_idovertheonewithout
        returndomain

    @api.model
    def_bom_find(self,product_tmpl=None,product=None,picking_type=None,company_id=False,bom_type=False):
        """FindsBoMforparticularproduct,pickingandcompany"""
        ifproductandproduct.type=='service'orproduct_tmplandproduct_tmpl.type=='service':
            returnself.env['mrp.bom']
        domain=self._bom_find_domain(product_tmpl=product_tmpl,product=product,picking_type=picking_type,company_id=company_id,bom_type=bom_type)
        ifdomainisFalse:
            returnself.env['mrp.bom']
        returnself.search(domain,order='sequence,product_id',limit=1)

    @api.model
    def_get_product2bom(self,products,bom_type=False,picking_type=False,company_id=False):
        """Optimizedvariantof_bom_findtoworkwithrecordset"""

        bom_by_product=defaultdict(lambda:self.env['mrp.bom'])
        products=products.filtered(lambdap:p.type!='service')
        ifnotproducts:
            returnbom_by_product
        product_templates=products.mapped('product_tmpl_id')
        domain=['|',('product_id','in',products.ids),'&',('product_id','=',False),('product_tmpl_id','in',product_templates.ids),('active','=',True)]
        ifpicking_type:
            domain+=['|',('picking_type_id','=',picking_type.id),('picking_type_id','=',False)]
        ifcompany_idorself.env.context.get('company_id'):
            domain=domain+['|',('company_id','=',False),('company_id','=',company_idorself.env.context.get('company_id'))]
        ifbom_type:
            domain+=[('type','=',bom_type)]

        iflen(products)==1:
            bom=self.search(domain,order='sequence,product_id,id',limit=1)
            ifbom:
                bom_by_product[products]=bom
            returnbom_by_product

        boms=self.search(domain,order='sequence,product_id,id')

        products_ids=set(products.ids)
        forbominboms:
            products_implies=bom.product_idorbom.product_tmpl_id.product_variant_ids
            forproductinproducts_implies:
                ifproduct.idinproducts_idsandproductnotinbom_by_product:
                    bom_by_product[product]=bom
        returnbom_by_product

    defexplode(self,product,quantity,picking_type=False):
        """
            ExplodestheBoMandcreatestwolistswithalltheinformationyouneed:bom_doneandline_done
            QuantitydescribesthenumberoftimesyouneedtheBoM:sothequantitydividedbythenumbercreatedbytheBoM
            andconvertedintoitsUoM
        """
        fromcollectionsimportdefaultdict

        graph=defaultdict(list)
        V=set()

        defcheck_cycle(v,visited,recStack,graph):
            visited[v]=True
            recStack[v]=True
            forneighbouringraph[v]:
                ifvisited[neighbour]==False:
                    ifcheck_cycle(neighbour,visited,recStack,graph)==True:
                        returnTrue
                elifrecStack[neighbour]==True:
                    returnTrue
            recStack[v]=False
            returnFalse

        product_ids=set()
        product_boms={}
        defupdate_product_boms():
            products=self.env['product.product'].browse(product_ids)
            product_boms.update(self._get_product2bom(products,bom_type='phantom',
                picking_type=picking_typeorself.picking_type_id,company_id=self.company_id.id))
            #Setmissingkeystodefaultvalue
            forproductinproducts:
                product_boms.setdefault(product,self.env['mrp.bom'])

        boms_done=[(self,{'qty':quantity,'product':product,'original_qty':quantity,'parent_line':False})]
        lines_done=[]
        V|=set([product.product_tmpl_id.id])

        bom_lines=[]
        forbom_lineinself.bom_line_ids:
            product_id=bom_line.product_id
            V|=set([product_id.product_tmpl_id.id])
            graph[product.product_tmpl_id.id].append(product_id.product_tmpl_id.id)
            bom_lines.append((bom_line,product,quantity,False))
            product_ids.add(product_id.id)
        update_product_boms()
        product_ids.clear()
        whilebom_lines:
            current_line,current_product,current_qty,parent_line=bom_lines[0]
            bom_lines=bom_lines[1:]

            ifcurrent_line._skip_bom_line(current_product):
                continue

            line_quantity=current_qty*current_line.product_qty
            ifnotcurrent_line.product_idinproduct_boms:
                update_product_boms()
                product_ids.clear()
            bom=product_boms.get(current_line.product_id)
            ifbom:
                converted_line_quantity=current_line.product_uom_id._compute_quantity(line_quantity/bom.product_qty,bom.product_uom_id)
                bom_lines+=[(line,current_line.product_id,converted_line_quantity,current_line)forlineinbom.bom_line_ids]
                forbom_lineinbom.bom_line_ids:
                    graph[current_line.product_id.product_tmpl_id.id].append(bom_line.product_id.product_tmpl_id.id)
                    ifbom_line.product_id.product_tmpl_id.idinVandcheck_cycle(bom_line.product_id.product_tmpl_id.id,{key:Falsefor keyinV},{key:Falsefor keyinV},graph):
                        raiseUserError(_('Recursionerror! AproductwithaBillofMaterialshouldnothaveitselfinitsBoMorchildBoMs!'))
                    V|=set([bom_line.product_id.product_tmpl_id.id])
                    ifnotbom_line.product_idinproduct_boms:
                        product_ids.add(bom_line.product_id.id)
                boms_done.append((bom,{'qty':converted_line_quantity,'product':current_product,'original_qty':quantity,'parent_line':current_line}))
            else:
                #Weroundupherebecausetheuserexpectsthatifhehastoconsumealittlemore,thewholeUOMunit
                #shouldbeconsumed.
                rounding=current_line.product_uom_id.rounding
                line_quantity=float_round(line_quantity,precision_rounding=rounding,rounding_method='UP')
                lines_done.append((current_line,{'qty':line_quantity,'product':current_product,'original_qty':quantity,'parent_line':parent_line}))

        returnboms_done,lines_done

    @api.model
    defget_import_templates(self):
        return[{
            'label':_('ImportTemplateforBillsofMaterials'),
            'template':'/mrp/static/xls/mrp_bom.xls'
        }]


classMrpBomLine(models.Model):
    _name='mrp.bom.line'
    _order="sequence,id"
    _rec_name="product_id"
    _description='BillofMaterialLine'
    _check_company_auto=True

    def_get_default_product_uom_id(self):
        returnself.env['uom.uom'].search([],limit=1,order='id').id

    product_id=fields.Many2one('product.product','Component',required=True,check_company=True)
    product_tmpl_id=fields.Many2one('product.template','ProductTemplate',related='product_id.product_tmpl_id')
    company_id=fields.Many2one(
        related='bom_id.company_id',store=True,index=True,readonly=True)
    product_qty=fields.Float(
        'Quantity',default=1.0,
        digits='ProductUnitofMeasure',required=True)
    product_uom_id=fields.Many2one(
        'uom.uom','ProductUnitofMeasure',
        default=_get_default_product_uom_id,
        required=True,
        help="UnitofMeasure(UnitofMeasure)istheunitofmeasurementfortheinventorycontrol",domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_id.uom_id.category_id')
    sequence=fields.Integer(
        'Sequence',default=1,
        help="Givesthesequenceorderwhendisplaying.")
    bom_id=fields.Many2one(
        'mrp.bom','ParentBoM',
        index=True,ondelete='cascade',required=True)
    parent_product_tmpl_id=fields.Many2one('product.template','ParentProductTemplate',related='bom_id.product_tmpl_id')
    possible_bom_product_template_attribute_value_ids=fields.Many2many('product.template.attribute.value',compute='_compute_possible_bom_product_template_attribute_value_ids')
    bom_product_template_attribute_value_ids=fields.Many2many(
        'product.template.attribute.value',string="ApplyonVariants",ondelete='restrict',
        domain="[('id','in',possible_bom_product_template_attribute_value_ids)]",
        help="BOMProductVariantsneededtoapplythisline.")
    allowed_operation_ids=fields.Many2many('mrp.routing.workcenter',compute='_compute_allowed_operation_ids')
    operation_id=fields.Many2one(
        'mrp.routing.workcenter','ConsumedinOperation',check_company=True,
        domain="[('id','in',allowed_operation_ids)]",
        help="Theoperationwherethecomponentsareconsumed,orthefinishedproductscreated.")
    child_bom_id=fields.Many2one(
        'mrp.bom','SubBoM',compute='_compute_child_bom_id')
    child_line_ids=fields.One2many(
        'mrp.bom.line',string="BOMlinesofthereferredbom",
        compute='_compute_child_line_ids')
    attachments_count=fields.Integer('AttachmentsCount',compute='_compute_attachments_count')

    _sql_constraints=[
        ('bom_qty_zero','CHECK(product_qty>=0)','Allproductquantitiesmustbegreaterorequalto0.\n'
            'Lineswith0quantitiescanbeusedasoptionallines.\n'
            'Youshouldinstallthemrp_byproductmoduleifyouwanttomanageextraproductsonBoMs!'),
    ]

    @api.depends(
        'parent_product_tmpl_id.attribute_line_ids.value_ids',
        'parent_product_tmpl_id.attribute_line_ids.attribute_id.create_variant',
        'parent_product_tmpl_id.attribute_line_ids.product_template_value_ids.ptav_active',
    )
    def_compute_possible_bom_product_template_attribute_value_ids(self):
        forlineinself:
            line.possible_bom_product_template_attribute_value_ids=line.parent_product_tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes().product_template_value_ids._only_active()

    @api.depends('product_id','bom_id')
    def_compute_child_bom_id(self):
        forlineinself:
            ifnotline.product_id:
                line.child_bom_id=False
            else:
                line.child_bom_id=self.env['mrp.bom']._bom_find(
                    product_tmpl=line.product_id.product_tmpl_id,
                    product=line.product_id)

    @api.depends('product_id')
    def_compute_attachments_count(self):
        forlineinself:
            nbr_attach=self.env['mrp.document'].search_count([
                '|',
                '&',('res_model','=','product.product'),('res_id','=',line.product_id.id),
                '&',('res_model','=','product.template'),('res_id','=',line.product_id.product_tmpl_id.id)])
            line.attachments_count=nbr_attach

    @api.depends('child_bom_id')
    def_compute_child_line_ids(self):
        """IftheBOMlinereferstoaBOM,returntheidsofthechildBOMlines"""
        forlineinself:
            line.child_line_ids=line.child_bom_id.bom_line_ids.idsorFalse

    @api.depends('bom_id')
    def_compute_allowed_operation_ids(self):
        forbom_lineinself:
            ifnotbom_line.bom_id.operation_ids:
                bom_line.allowed_operation_ids=self.env['mrp.routing.workcenter']
            else:
                operation_domain=[
                    ('id','in',bom_line.bom_id.operation_ids.ids),
                    '|',
                        ('company_id','=',bom_line.company_id.id),
                        ('company_id','=',False)
                ]
                bom_line.allowed_operation_ids=self.env['mrp.routing.workcenter'].search(operation_domain)

    @api.onchange('product_uom_id')
    defonchange_product_uom_id(self):
        res={}
        ifnotself.product_uom_idornotself.product_id:
            returnres
        ifself.product_uom_id.category_id!=self.product_id.uom_id.category_id:
            self.product_uom_id=self.product_id.uom_id.id
            res['warning']={'title':_('Warning'),'message':_('TheProductUnitofMeasureyouchosehasadifferentcategorythanintheproductform.')}
        returnres

    @api.onchange('product_id')
    defonchange_product_id(self):
        ifself.product_id:
            self.product_uom_id=self.product_id.uom_id.id

    @api.model_create_multi
    defcreate(self,vals_list):
        forvaluesinvals_list:
            if'product_id'invaluesand'product_uom_id'notinvalues:
                values['product_uom_id']=self.env['product.product'].browse(values['product_id']).uom_id.id
        returnsuper(MrpBomLine,self).create(vals_list)

    def_skip_bom_line(self,product):
        """ControlifaBoMlineshouldbeproduced,canbeinheritedtoadd
        customcontrol.Itcurrentlychecksthatallvariantvaluesareinthe
        product.

        Ifmultiplevaluesareencodedforthesameattributeline,onlyoneof
        themhastobefoundonthevariant.
        """
        self.ensure_one()
        ifproduct._name=='product.template':
            returnFalse
        #Theintersectionofthevaluesoftheproductandthoseofthelinesatisfy:
        #*thenumberofitemsequalsthenumberofattributes(sinceaproductcannot
        #  havemultiplevaluesforthesameattribute),
        #*theattributesareasubsetoftheattributesoftheline.
        returnlen(product.product_template_attribute_value_ids&self.bom_product_template_attribute_value_ids)!=len(self.bom_product_template_attribute_value_ids.attribute_id)

    defaction_see_attachments(self):
        domain=[
            '|',
            '&',('res_model','=','product.product'),('res_id','=',self.product_id.id),
            '&',('res_model','=','product.template'),('res_id','=',self.product_id.product_tmpl_id.id)]
        attachment_view=self.env.ref('mrp.view_document_file_kanban_mrp')
        return{
            'name':_('Attachments'),
            'domain':domain,
            'res_model':'mrp.document',
            'type':'ir.actions.act_window',
            'view_id':attachment_view.id,
            'views':[(attachment_view.id,'kanban'),(False,'form')],
            'view_mode':'kanban,tree,form',
            'help':_('''<pclass="o_view_nocontent_smiling_face">
                        Uploadfilestoyourproduct
                    </p><p>
                        Usethisfeaturetostoreanyfiles,likedrawingsorspecifications.
                    </p>'''),
            'limit':80,
            'context':"{'default_res_model':'%s','default_res_id':%d,'default_company_id':%s}"%('product.product',self.product_id.id,self.company_id.id)
        }


classMrpByProduct(models.Model):
    _name='mrp.bom.byproduct'
    _description='Byproduct'
    _rec_name="product_id"
    _check_company_auto=True

    product_id=fields.Many2one('product.product','By-product',required=True,check_company=True)
    company_id=fields.Many2one(related='bom_id.company_id',store=True,index=True,readonly=True)
    product_qty=fields.Float(
        'Quantity',
        default=1.0,digits='ProductUnitofMeasure',required=True)
    product_uom_id=fields.Many2one('uom.uom','UnitofMeasure',required=True)
    bom_id=fields.Many2one('mrp.bom','BoM',ondelete='cascade')
    allowed_operation_ids=fields.Many2many('mrp.routing.workcenter',compute='_compute_allowed_operation_ids')
    operation_id=fields.Many2one(
        'mrp.routing.workcenter','ProducedinOperation',check_company=True,
        domain="[('id','in',allowed_operation_ids)]")

    @api.depends('bom_id')
    def_compute_allowed_operation_ids(self):
        forbyproductinself:
            ifnotbyproduct.bom_id.operation_ids:
                byproduct.allowed_operation_ids=self.env['mrp.routing.workcenter']
            else:
                operation_domain=[
                    ('id','in',byproduct.bom_id.operation_ids.ids),
                    '|',
                        ('company_id','=',byproduct.company_id.id),
                        ('company_id','=',False)
                ]
                byproduct.allowed_operation_ids=self.env['mrp.routing.workcenter'].search(operation_domain)

    @api.onchange('product_id')
    defonchange_product_id(self):
        """ChangesUoMifproduct_idchanges."""
        ifself.product_id:
            self.product_uom_id=self.product_id.uom_id.id

    @api.onchange('product_uom_id')
    defonchange_uom(self):
        res={}
        ifself.product_uom_idandself.product_idandself.product_uom_id.category_id!=self.product_id.uom_id.category_id:
            res['warning']={
                'title':_('Warning'),
                'message':_('Theunitofmeasureyouchooseisinadifferentcategorythantheproductunitofmeasure.')
            }
            self.product_uom_id=self.product_id.uom_id.id
        returnres
