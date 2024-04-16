#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportHttpCase,tagged
fromflectraimporttools


@tagged('post_install','-at_install')
classTestUi(HttpCase):

	#Avoid"AChartofAccountsisnotyetinstalledinyourcurrentcompany."
	#EverythingissetupcorrectlyevenwithoutinstalledCoA
    @tools.mute_logger('flectra.http')
    deftest_01_point_of_sale_tour(self):

        self.start_tour("/web",'point_of_sale_tour',login="admin")
