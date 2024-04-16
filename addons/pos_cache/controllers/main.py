#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.point_of_sale.controllers.mainimportPosController
fromflectraimporthttp
fromflectra.httpimportrequest


classPosCache(PosController):

    @http.route()
    defload_onboarding_data(self):
        super().load_onboarding_data()
        request.env["pos.cache"].refresh_all_caches()
