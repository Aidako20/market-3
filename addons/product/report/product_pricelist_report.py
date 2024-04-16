#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classreport_product_pricelist(models.AbstractModel):
    _name='report.product.report_pricelist'
    _description='PricelistReport'

    def_get_report_values(self,docids,data):
        product_ids=[int(i)foriindata['active_ids'].split(',')]ifdata['active_ids']elseFalse
        pricelist_id=data['pricelist_id']andint(data['pricelist_id'])orNone
        quantities=[int(i)foriindata['quantities'].split(',')]or[1]
        returnself._get_report_data(data['active_model'],product_ids,pricelist_id,quantities,'pdf')

    @api.model
    defget_html(self):
        render_values=self._get_report_data(
            self.env.context.get('active_model'),
            self.env.context.get('active_ids'),
            self.env.context.get('pricelist_id'),
            self.env.context.get('quantities')or[1]
        )
        returnself.env.ref('product.report_pricelist_page')._render(render_values)

    def_get_report_data(self,active_model,active_ids,pricelist_id,quantities,report_type='html'):
        products=[]
        is_product_tmpl=active_model=='product.template'

        ProductClass=self.env['product.template']ifis_product_tmplelseself.env['product.product']
        ProductPricelist=self.env['product.pricelist']
        pricelist=ProductPricelist.browse(pricelist_id)
        ifnotpricelist:
            pricelist=ProductPricelist.search([],limit=1)

        ifis_product_tmpl:
            records=ProductClass.browse(active_ids)ifactive_idselseProductClass.search([('sale_ok','=',True)])
            forproductinrecords:
                product_data=self._get_product_data(is_product_tmpl,product,pricelist,quantities)
                variants=[]
                iflen(product.product_variant_ids)>1:
                    forvariantinproduct.product_variant_ids:
                        variants.append(self._get_product_data(False,variant,pricelist,quantities))
                product_data['variants']=variants
                products.append(product_data)
        else:
            records=ProductClass.browse(active_ids)ifactive_idselseProductClass.search([('sale_ok','=',True)])
            forproductinrecords:
                products.append(self._get_product_data(is_product_tmpl,product,pricelist,quantities))

        return{
            'pricelist':pricelist,
            'products':products,
            'quantities':quantities,
            'is_product_tmpl':is_product_tmpl,
            'is_html_type':report_type=='html',
        }

    def_get_product_data(self,is_product_tmpl,product,pricelist,quantities):
        data={
            'id':product.id,
            'name':is_product_tmplandproduct.nameorproduct.display_name,
            'price':dict.fromkeys(quantities,0.0),
        }
        forqtyinquantities:
            data['price'][qty]=pricelist.get_product_price(product,qty,False)
        returndata
