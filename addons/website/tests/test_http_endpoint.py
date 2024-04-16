#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromunittest.mockimportsentinel

fromflectra.httpimportEndPoint
fromflectra.testsimportHttpCase


classTestHttpEndPoint(HttpCase):

    deftest_http_endpoint_equality(self):
        sentinel.method.original_func=sentinel.method_original_func
        args=(sentinel.method,{'routing_arg':sentinel.routing_arg})
        endpoint1=EndPoint(*args)
        endpoint2=EndPoint(*args)

        self.assertEqual(endpoint1,endpoint2)

        testdict={}
        testdict[endpoint1]=42
        self.assertEqual(testdict[endpoint2],42)
        self.assertTrue(endpoint2intestdict)

    deftest_can_clear_routing_map_during_render(self):
        """
        Theroutingmapmightbeclearedwhilerenderingaqwebview.
        Forexample,ifanassetbundleisregeneratedtheoldoneisunlinked,
        whichcausesacacheclearing.
        Thistestensuresthattherenderingstillworks,eveninthiscase.
        """
        homepage_id=self.env['ir.ui.view'].search([
            ('website_id','=',self.env.ref('website.default_website').id),
            ('key','=','website.homepage'),
        ])
        self.env['ir.ui.view'].create({
            'name':'AddcachecleartoHome',
            'type':'qweb',
            'mode':'extension',
            'inherit_id':homepage_id.id,
            'arch_db':"""
                <tt-call="website.layout"position="before">
                    <tt-esc="website.env['ir.http']._clear_routing_map()"/>
                </t>
            """,
        })

        r=self.url_open('/')
        r.raise_for_status()
