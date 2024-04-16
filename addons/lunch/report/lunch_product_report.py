#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools
fromflectra.osvimportexpression


classLunchProductReport(models.Model):
    _name="lunch.product.report"
    _description='Productreport'
    _auto=False
    _order='is_favoritedesc,is_newdesc,last_order_dateasc,product_idasc'

    id=fields.Integer('ID')
    product_id=fields.Many2one('lunch.product','Product')
    name=fields.Char('ProductName',related='product_id.name')
    category_id=fields.Many2one('lunch.product.category','ProductCategory')
    description=fields.Text('Description',related='product_id.description')
    price=fields.Float('Price')
    supplier_id=fields.Many2one('lunch.supplier','Vendor')
    company_id=fields.Many2one('res.company')
    currency_id=fields.Many2one('res.currency',related='company_id.currency_id')
    is_favorite=fields.Boolean('Favorite')
    user_id=fields.Many2one('res.users')
    is_new=fields.Boolean('New')
    active=fields.Boolean('Active')
    last_order_date=fields.Date('LastOrderDate')
    image_128=fields.Image(compute="_compute_image_128")

    #Thisfieldisusedonlyforsearching
    is_available_at=fields.Many2one('lunch.location','ProductAvailability',compute='_compute_is_available_at',search='_search_is_available_at')

    def_compute_image_128(self):
        forproduct_rinself:
            product=product_r.product_id
            category=product_r.sudo().category_id
            ifproduct.image_128:
                product_r.image_128=product.image_128
            elifcategory.image_128:
                product_r.image_128=category.image_128
            else:
                product_r.image_128=False

    defcompute_concurrency_field(self):
        """Imagecachingisbasedonthe`__last_update`field(=self.CONCURRENCY_CHECK_FIELD)
        Buttheimageisnevercachedbythebrowserbecausethevaluefallbacksto
        `now`whenaccessloggingisdisabled.Thisoverridesetsa"real"valuebasedonthe
        productorcategorylastupdate.
        """
        forreportinself:
            product_last_update=report.product_id[self.CONCURRENCY_CHECK_FIELD]
            category_last_update=report.category_id[self.CONCURRENCY_CHECK_FIELD]
            report[self.CONCURRENCY_CHECK_FIELD]=max(product_last_update,category_last_update)

    def_compute_is_available_at(self):
        """
            Isavailable_atisalwaysfalsewhenbrowsingit
            thisfieldisthereonlytosearch(see_search_is_available_at)
        """
        forproductinself:
            product.is_available_at=False

    def_search_is_available_at(self,operator,value):
        supported_operators=['in','notin','=','!=']

        ifnotoperatorinsupported_operators:
            returnexpression.TRUE_DOMAIN

        ifisinstance(value,int):
            value=[value]

        ifoperatorinexpression.NEGATIVE_TERM_OPERATORS:
            returnexpression.AND([[('supplier_id.available_location_ids','notin',value)],[('supplier_id.available_location_ids','!=',False)]])

        returnexpression.OR([[('supplier_id.available_location_ids','in',value)],[('supplier_id.available_location_ids','=',False)]])

    defwrite(self,values):
        if'is_favorite'invalues:
            ifvalues['is_favorite']:
                commands=[(4,product_id)forproduct_idinself.mapped('product_id').ids]
            else:
                commands=[(3,product_id)forproduct_idinself.mapped('product_id').ids]
            self.env.user.write({
                'favorite_lunch_product_ids':commands,
            })

    definit(self):
        tools.drop_view_if_exists(self._cr,self._table)

        self._cr.execute("""
            CREATEorREPLACEview%sAS(
                SELECT
                    row_number()over(ORDERBYusers.id,product.id)ASid,
                    product.idASproduct_id,
                    product.category_id,
                    product.price,
                    product.supplier_id,
                    product.company_id,
                    product.active,
                    users.idASuser_id,
                    fav.user_idISNOTNULLASis_favorite,
                    product.new_until>=current_dateASis_new,
                    orders.last_order_date
                FROMlunch_productproduct
                CROSSJOINres_usersusers
                INNERJOINres_groups_users_relgroupsONgroups.uid=users.id--onlygenerateforinternalusers
                LEFTJOINLATERAL(selectmax(date)ASlast_order_dateFROMlunch_orderwhereuser_id=users.idandproduct_id=product.id)ASordersONTRUE
                LEFTJOINLATERAL(selectuser_idFROMlunch_product_favorite_user_relwhereuser_id=users.idandproduct_id=product.id)ASfavONTRUE
                WHEREusers.activeANDproduct.activeANDgroups.gid=%%s--onlytakeintoaccountactiveproductsandusers
            );
        """%self._table,(self.env.ref('base.group_user').id,))
