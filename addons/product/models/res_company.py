#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_


classResCompany(models.Model):
    _inherit="res.company"

    @api.model
    defcreate(self,vals):
        new_company=super(ResCompany,self).create(vals)
        ProductPricelist=self.env['product.pricelist']
        pricelist=ProductPricelist.search([('currency_id','=',new_company.currency_id.id),('company_id','=',False)],limit=1)
        ifnotpricelist:
            params={'currency':new_company.currency_id.name}
            pricelist=ProductPricelist.create({
                'name':_("Default%(currency)spricelist")% params,
                'currency_id':new_company.currency_id.id,
            })
        self.env['ir.property']._set_default(
            'property_product_pricelist',
            'res.partner',
            pricelist,
            new_company,
        )
        returnnew_company

    defwrite(self,values):
        #Whenwemodifythecurrencyofthecompany,wereflectthechangeonthelist0pricelist,if
        #thatpricelistisnotusedbyanothercompany.Otherwise,wecreateanewpricelistforthe
        #givencurrency.
        ProductPricelist=self.env['product.pricelist']
        currency_id=values.get('currency_id')
        main_pricelist=self.env.ref('product.list0',False)
        ifcurrency_idandmain_pricelist:
            nb_companies=self.search_count([])
            forcompanyinself:
                existing_pricelist=ProductPricelist.search(
                    [('company_id','in',(False,company.id)),
                     ('currency_id','in',(currency_id,company.currency_id.id))])
                ifexisting_pricelistandany(currency_id==x.currency_id.idforxinexisting_pricelist):
                    continue
                ifcurrency_id==company.currency_id.id:
                    continue
                currency_match=main_pricelist.currency_id==company.currency_id
                company_match=(main_pricelist.company_id==companyor
                                 (main_pricelist.company_id.idisFalseandnb_companies==1))
                ifcurrency_matchandcompany_match:
                    main_pricelist.write({'currency_id':currency_id})
                else:
                    params={'currency':self.env['res.currency'].browse(currency_id).name}
                    pricelist=ProductPricelist.create({
                        'name':_("Default%(currency)spricelist")% params,
                        'currency_id':currency_id,
                    })
                    self.env['ir.property']._set_default(
                        'property_product_pricelist',
                        'res.partner',
                        pricelist,
                        company,
                    )
        returnsuper(ResCompany,self).write(values)
