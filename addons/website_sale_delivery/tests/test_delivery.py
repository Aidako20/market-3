#-*-coding:utf-8-*-
fromflectra.addons.website_sale.controllers.mainimportWebsiteSale
fromflectra.testsimporttagged,HttpCase

@tagged('post_install','-at_install')
classTestDelivery(HttpCase):
    deftest_address_states(self):
        US=self.env.ref('base.us')
        MX=self.env.ref('base.mx')

        #Setallcarrierstomexico
        self.env['delivery.carrier'].sudo().search([('website_published','=',True)]).country_ids=[(6,0,[MX.id])]

        #Createanewcarriertoonlyonestateinmexico
        self.env['delivery.carrier'].create({
                'name':"One_state",
                'product_id':self.env['product.product'].create({'name':"deliveryproduct"}).id,
                'website_published':True,
                'country_ids':[(6,0,[MX.id])],
                'state_ids':[(6,0,[MX.state_ids.ids[0]])]
        })

        country_info=WebsiteSale().country_infos(country=MX,mode="shipping")
        self.assertEqual(len(country_info['states']),len(MX.state_ids))

        country_info=WebsiteSale().country_infos(country=US,mode="shipping")
        self.assertEqual(len(country_info['states']),0)
