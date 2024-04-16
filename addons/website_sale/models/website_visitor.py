#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta

fromflectraimportfields,models,api

classWebsiteTrack(models.Model):
    _inherit='website.track'

    product_id=fields.Many2one('product.product',index=True,ondelete='cascade',readonly=True)


classWebsiteVisitor(models.Model):
    _inherit='website.visitor'

    visitor_product_count=fields.Integer('ProductViews',compute="_compute_product_statistics",help="Totalnumberofviewsonproducts")
    product_ids=fields.Many2many('product.product',string="VisitedProducts",compute="_compute_product_statistics")
    product_count=fields.Integer('ProductsViews',compute="_compute_product_statistics",help="Totalnumberofproductviewed")

    @api.depends('website_track_ids')
    def_compute_product_statistics(self):
        results=self.env['website.track'].read_group(
            [('visitor_id','in',self.ids),('product_id','!=',False),
             '|',('product_id.company_id','in',self.env.companies.ids),('product_id.company_id','=',False)],
            ['visitor_id','product_id'],['visitor_id','product_id'],
            lazy=False)
        mapped_data={}
        forresultinresults:
            visitor_info=mapped_data.get(result['visitor_id'][0],{'product_count':0,'product_ids':set()})
            visitor_info['product_count']+=result['__count']
            visitor_info['product_ids'].add(result['product_id'][0])
            mapped_data[result['visitor_id'][0]]=visitor_info

        forvisitorinself:
            visitor_info=mapped_data.get(visitor.id,{'product_ids':[],'product_count':0})

            visitor.product_ids=[(6,0,visitor_info['product_ids'])]
            visitor.visitor_product_count=visitor_info['product_count']
            visitor.product_count=len(visitor_info['product_ids'])

    def_add_viewed_product(self,product_id):
        """addawebsite_trackwithapagemarkedasviewed"""
        self.ensure_one()
        ifproduct_idandself.env['product.product'].browse(product_id)._is_variant_possible():
            domain=[('product_id','=',product_id)]
            website_track_values={'product_id':product_id,'visit_datetime':datetime.now()}
            self._add_tracking(domain,website_track_values)
