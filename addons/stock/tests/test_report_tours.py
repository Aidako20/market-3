#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importflectra
fromflectra.testsimportForm,HttpCase,tagged


@tagged('-at_install','post_install')
classTestStockReportTour(HttpCase):
    defsetUp(self):
        super().setUp()

    def_get_report_url(self):
        return'/web#&model=product.template&action=stock.product_template_action_product'


    deftest_stock_route_diagram_report(self):
        """Opentheroutediagramreport."""
        url=self._get_report_url()

        self.start_tour(url,'test_stock_route_diagram_report',login='admin',timeout=180)
