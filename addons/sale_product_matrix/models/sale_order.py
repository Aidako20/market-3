#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importjson
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classSaleOrder(models.Model):
    _inherit='sale.order'

    report_grids=fields.Boolean(
        string="PrintVariantGrids",default=True,
        help="Ifset,thematrixoftheproductsconfigurablebymatrixwillbeshownonthereportoftheorder.")

    """Matrixloadingandupdate:fieldsandmethods:

    NOTE:Thematrixfunctionalitywasdoneinpython,serverside,toavoidjs
        restriction. Indeed,thejsframeworkonlyloadsthexfirstlinesdisplayed
        intheclient,whichmeansincaseofbigmatricesandlotsofso_lines,
        thejsdoesn'thaveaccesstothe41nthandfollowinglines.

        Toforcetheloading,a'hack'ofthejsframeworkwouldhavebeenneeded...
    """

    grid_product_tmpl_id=fields.Many2one(
        'product.template',store=False,
        help="Technicalfieldforproduct_matrixfunctionalities.")
    grid_update=fields.Boolean(
        default=False,store=False,
        help="Whetherthegridfieldcontainsanewmatrixtoapplyornot.")
    grid=fields.Char(
        "Matrixlocalstorage",store=False,
        help="Technicallocalstorageofgrid.\nIfgrid_update,willbeloadedontheSO.\nIfnot,representsthematrixtoopen.")

    @api.onchange('grid_product_tmpl_id')
    def_set_grid_up(self):
        """Savelocallythematrixofthegivenproduct.template,tobeusedbythematrixconfigurator."""
        ifself.grid_product_tmpl_id:
            self.grid_update=False
            self.grid=json.dumps(self._get_matrix(self.grid_product_tmpl_id))

    @api.onchange('grid')
    def_apply_grid(self):
        """ApplythegivenlistofchangedmatrixcellstothecurrentSO."""
        ifself.gridandself.grid_update:
            grid=json.loads(self.grid)
            product_template=self.env['product.template'].browse(grid['product_template_id'])
            product_ids=set()
            dirty_cells=grid['changes']
            Attrib=self.env['product.template.attribute.value']
            default_so_line_vals={}
            new_lines=[]
            forcellindirty_cells:
                combination=Attrib.browse(cell['ptav_ids'])
                no_variant_attribute_values=combination-combination._without_no_variant_attributes()

                #createorfindproductvariantfromcombination
                product=product_template._create_product_variant(combination)
                order_lines=self.order_line.filtered(
                    lambdaline:line.product_id.id==product.id
                    andline.product_no_variant_attribute_value_ids.ids==no_variant_attribute_values.ids
                )

                #ifproductvariantalreadyexistinorderlines
                old_qty=sum(order_lines.mapped('product_uom_qty'))
                qty=cell['qty']
                diff=qty-old_qty

                ifnotdiff:
                    continue

                product_ids.add(product.id)

                #TODOkeepqtycheck?cannotbe0becauseweonlygetcellchanges...
                iforder_lines:
                    ifqty==0:
                        ifself.statein['draft','sent']:
                            #Removelinesifqtywassetto0inmatrix
                            #onlyifSOstate=draft/sent
                            self.order_line-=order_lines
                        else:
                            order_lines.update({'product_uom_qty':0.0})
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
                            raiseValidationError(_("Youcannotchangethequantityofaproductpresentinmultiplesalelines."))
                        else:
                            order_lines[0].product_uom_qty=qty
                            #Ifwewanttosupportmultiplelinesedition:
                            #removalofotherlines.
                            #Fornow,anerrorisraisedinstead
                            #iflen(order_lines)>1:
                            #    #Remove1+lines
                            #    self.order_line-=order_lines[1:]
                else:
                    ifnotdefault_so_line_vals:
                        OrderLine=self.env['sale.order.line']
                        default_so_line_vals=OrderLine.default_get(OrderLine._fields.keys())
                    last_sequence=self.order_line[-1:].sequence
                    iflast_sequence:
                        default_so_line_vals['sequence']=last_sequence
                    new_lines.append((0,0,dict(
                        default_so_line_vals,
                        product_id=product.id,
                        product_uom_qty=qty,
                        product_no_variant_attribute_value_ids=no_variant_attribute_values.ids)
                    ))
            ifproduct_ids:
                res=False
                ifnew_lines:
                    #AddnewSOlines
                    self.update(dict(order_line=new_lines))

                #Recomputepricesfornew/modifiedlines
                forlineinself.order_line.filtered(lambdaline:line.product_id.idinproduct_ids):
                    res=line.product_id_change()orres
                    line._onchange_discount()
                    line._onchange_product_id_set_customer_lead()
                returnres

    def_get_matrix(self,product_template):
        """Returnthematrixofthegivenproduct,updatedwithcurrentSOLinesquantities.

        :paramproduct.templateproduct_template:
        :return:matrixtodisplay
        :rtypedict:
        """
        defhas_ptavs(line,sorted_attr_ids):
            #TODOinsteadofsortingonids,useflectra-definedorderformatrix?
            ptav=line.product_template_attribute_value_ids.ids
            pnav=line.product_no_variant_attribute_value_ids.ids
            pav=pnav+ptav
            pav.sort()
            returnpav==sorted_attr_ids
        matrix=product_template._get_template_matrix(
            company_id=self.company_id,
            currency_id=self.currency_id,
            display_extra_price=True)
        ifself.order_line:
            lines=matrix['matrix']
            order_lines=self.order_line.filtered(lambdaline:line.product_template_id==product_template)
            forlineinlines:
                forcellinline:
                    ifnotcell.get('name',False):
                        line=order_lines.filtered(lambdaline:has_ptavs(line,cell['ptav_ids']))
                        ifline:
                            cell.update({
                                'qty':sum(line.mapped('product_uom_qty'))
                            })
        returnmatrix

    defget_report_matrixes(self):
        """Reportingmethod.

        :return:arrayofmatricestodisplayinthereport
        :rtype:list
        """
        matrixes=[]
        ifself.report_grids:
            grid_configured_templates=self.order_line.filtered('is_configurable_product').product_template_id.filtered(lambdaptmpl:ptmpl.product_add_mode=='matrix')
            fortemplateingrid_configured_templates:
                iflen(self.order_line.filtered(lambdaline:line.product_template_id==template))>1:
                    #TODOdowereallywantthewholematrixevenifthereisn'talotoflines??
                    matrixes.append(self._get_matrix(template))
        returnmatrixes
