#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError,UserError


classPosCategory(models.Model):
    _name="pos.category"
    _description="PointofSaleCategory"
    _order="sequence,name"

    @api.constrains('parent_id')
    def_check_category_recursion(self):
        ifnotself._check_recursion():
            raiseValidationError(_('Error!Youcannotcreaterecursivecategories.'))

    name=fields.Char(string='CategoryName',required=True,translate=True)
    parent_id=fields.Many2one('pos.category',string='ParentCategory',index=True)
    child_id=fields.One2many('pos.category','parent_id',string='ChildrenCategories')
    sequence=fields.Integer(help="Givesthesequenceorderwhendisplayingalistofproductcategories.")
    image_128=fields.Image("Image",max_width=128,max_height=128)

    defname_get(self):
        defget_names(cat):
            res=[]
            whilecat:
                res.append(cat.name)
                cat=cat.parent_id
            returnres
        return[(cat.id,"/".join(reversed(get_names(cat))))forcatinself]

    defunlink(self):
        ifself.search_count([('id','in',self.ids)]):
            ifself.env['pos.session'].sudo().search_count([('state','!=','closed')]):
                raiseUserError(_('Youcannotdeleteapointofsalecategorywhileasessionisstillopened.'))
        returnsuper(PosCategory,self).unlink()
