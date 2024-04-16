#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,models


classIrModule(models.Model):
    _inherit='ir.module.module'


    @api.returns('self')
    defdownstream_dependencies(
            self,
            known_deps=None,
            exclude_states=('uninstalled','uninstallable','toremove'),
            ):
        #sale_stock_marginimplicitlydependsonsale_stock,butsale_stockisnotmarkedasoneof
        #itsdependencies,thusuninstallingsale_stockwithoutuninstallingsale_stock_margin
        #willmaketheregistrycrash,theinstallworkspurelybecausesale_stockisauto-installed
        #whenthedependenciesofsale_stock_marginareinstalled
        if'sale_stock'inself.mapped('name'):
            #weforcesale_stock_marginasadependantofsale_stock
            known_deps=(known_depsorself.browse())|self.search([
                ('name','=','sale_stock_margin'),
                ('state','=','installed'),
            ],limit=1)
        returnsuper().downstream_dependencies(known_deps,exclude_states)
