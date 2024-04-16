#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importjson
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classPurchaseOrder(models.Model):
    _inherit='purchase.order'

    report_grids=fields.Boolean(string="PrintVariantGrids",default=True,help="Ifset,thematrixofconfigurableproductswillbeshownonthereportofthisorder.")

    """Matrixloadingandupdate:fieldsandmethods:

    NOTE:Thematrixfunctionalitywasdoneinpython,serverside,toavoidjs
        restriction. Indeed,thejsframeworkonlyloadsthexfirstlinesdisplayed
        intheclient,whichmeansincaseofbigmatricesandlotsofpo_lines,
        thejsdoesn'thaveaccesstothe41standfollowinglines.

        Toforcetheloading,a'hack'ofthejsframeworkwouldhavebeenneeded...
    """

    grid_product_tmpl_id=fields.Many2one('product.template',store=False,help="Technicalfieldforproduct_matrixfunctionalities.")
    grid_update=fields.Boolean(default=False,store=False,help="Whetherthegridfieldcontainsanewmatrixtoapplyornot.")
    grid=fields.Char(store=False,help="Technicalstorageofgrid.\nIfgrid_update,willbeloadedonthePO.\nIfnot,representsthematrixtoopen.")

    @api.onchange('grid_product_tmpl_id')
    def_set_grid_up(self):
        ifself.grid_product_tmpl_id:
            self.grid_update=False
            self.grid=json.dumps(self._get_matrix(self.grid_product_tmpl_id))

    def_must_delete_date_planned(self,field_name):
        returnsuper()._must_delete_date_planned(field_name)orfield_name=="grid"

    @api.onchange('grid')
    def_apply_grid(self):
        ifself.gridandself.grid_update:
            grid=json.loads(self.grid)
            product_template=self.env['product.template'].browse(grid['product_template_id'])
            product_ids=set()
            dirty_cells=grid['changes']
            Attrib=self.env['product.template.attribute.value']
            default_po_line_vals={}
            new_lines=[]
            forcellindirty_cells:
                combination=Attrib.browse(cell['ptav_ids'])
                no_variant_attribute_values=combination-combination._without_no_variant_attributes()

                #createorfindproductvariantfromcombination
                product=product_template._create_product_variant(combination)
                #TODOreplacethecheckonproduct_idbyafirstcheckontheptavsandpnavs?
                #andonlycreate/requirevariantafternolinehasbeenfound???
                order_lines=self.order_line.filtered(lambdaline:(line._originorline).product_id==productand(line._originorline).product_no_variant_attribute_value_ids==no_variant_attribute_values)

                #ifproductvariantalreadyexistinorderlines
                old_qty=sum(order_lines.mapped('product_qty'))
                qty=cell['qty']
                diff=qty-old_qty

                ifnotdiff:
                    continue

                product_ids.add(product.id)

                iforder_lines:
                    ifqty==0:
                        ifself.statein['draft','sent']:
                            #Removelinesifqtywassetto0inmatrix
                            #onlyifPOstate=draft/sent
                            self.order_line-=order_lines
                        else:
                            order_lines.update({'product_qty':0.0})
                    else:
                        """
                        Whentherearemultiplelinesforsameproductanditsquantitywaschangedinthematrix,
                        Anerrorisraised.

                        A'good'strategywouldbeto:
                            *Setsthequantityofthefirstfoundlinetothecellvalue
                            *Removetheotherlines.

                        Butthiswouldremoveallbusinesslogiclinkedtotheotherlines...
                        Therefore,itonlyraisesanErrorfornow.
                        """
                        iflen(order_lines)>1:
                            raiseValidationError(_("Youcannotchangethequantityofaproductpresentinmultiplepurchaselines."))
                        else:
                            order_lines[0].product_qty=qty
                            order_lines[0]._onchange_quantity()
                            #Ifwewanttosupportmultiplelinesedition:
                            #removalofotherlines.
                            #Fornow,anerrorisraisedinstead
                            #iflen(order_lines)>1:
                            #    #Remove1+lines
                            #    self.order_line-=order_lines[1:]
                else:
                    ifnotdefault_po_line_vals:
                        OrderLine=self.env['purchase.order.line']
                        default_po_line_vals=OrderLine.default_get(OrderLine._fields.keys())
                    last_sequence=self.order_line[-1:].sequence
                    iflast_sequence:
                        default_po_line_vals['sequence']=last_sequence
                    new_lines.append((0,0,dict(
                        default_po_line_vals,
                        product_id=product.id,
                        product_qty=qty,
                        product_no_variant_attribute_value_ids=no_variant_attribute_values.ids)
                    ))
            ifproduct_ids:
                res=False
                ifnew_lines:
                    #AddnewPOlines
                    self.update(dict(order_line=new_lines))

                #Recomputepricesfornew/modifiedlines:
                forlineinself.order_line.filtered(lambdaline:line.product_id.idinproduct_ids):
                    line._product_id_change()
                    line._onchange_quantity()
                    res=line.onchange_product_id_warning()orres
                returnres

    def_get_matrix(self,product_template):
        defhas_ptavs(line,sorted_attr_ids):
            ptav=line.product_template_attribute_value_ids.ids
            pnav=line.product_no_variant_attribute_value_ids.ids
            pav=pnav+ptav
            pav.sort()
            returnpav==sorted_attr_ids
        matrix=product_template._get_template_matrix(
            company_id=self.company_id,
            currency_id=self.currency_id)
        ifself.order_line:
            lines=matrix['matrix']
            order_lines=self.order_line.filtered(lambdaline:line.product_template_id==product_template)
            forlineinlines:
                forcellinline:
                    ifnotcell.get('name',False):
                        line=order_lines.filtered(lambdaline:has_ptavs(line,cell['ptav_ids']))
                        ifline:
                            cell.update({
                                'qty':sum(line.mapped('product_qty'))
                            })
        returnmatrix

    defget_report_matrixes(self):
        """Reportingmethod."""
        matrixes=[]
        ifself.report_grids:
            grid_configured_templates=self.order_line.filtered('is_configurable_product').product_template_id
            #TODOisconfigurableproductandproduct_variant_count>1
            #configurableproductsareonlyconfiguredthroughthematrixinpurchase,sononeedtocheckproduct_add_mode.
            fortemplateingrid_configured_templates:
                iflen(self.order_line.filtered(lambdaline:line.product_template_id==template))>1:
                    matrixes.append(self._get_matrix(template))
        returnmatrixes


classPurchaseOrderLine(models.Model):
    _inherit="purchase.order.line"

    product_template_id=fields.Many2one('product.template',string='ProductTemplate',related="product_id.product_tmpl_id",domain=[('purchase_ok','=',True)])
    is_configurable_product=fields.Boolean('Istheproductconfigurable?',related="product_template_id.has_configurable_attributes")
    product_template_attribute_value_ids=fields.Many2many(related='product_id.product_template_attribute_value_ids',readonly=True)
    product_no_variant_attribute_value_ids=fields.Many2many('product.template.attribute.value',string='Productattributevaluesthatdonotcreatevariants',ondelete='restrict')

    def_get_product_purchase_description(self,product):
        name=super(PurchaseOrderLine,self)._get_product_purchase_description(product)
        forno_variant_attribute_valueinself.product_no_variant_attribute_value_ids:
            name+="\n"+no_variant_attribute_value.attribute_id.name+':'+no_variant_attribute_value.name

        returnname
