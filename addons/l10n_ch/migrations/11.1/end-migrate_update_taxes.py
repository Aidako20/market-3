#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,SUPERUSER_ID
fromflectra.addons.account.models.chart_templateimportupdate_taxes_from_templates


defmigrate(cr,version):
    env=api.Environment(cr,SUPERUSER_ID,{})
    #Wehadcorrupteddata,handlethecorrectionsothetaxupdatecanproceed.
    #Seehttps://github.com/flectra/flectra/commit/7b07df873535446f97abc1de9176b9332de5cb07
    forcompanyinenv.companies:
        taxes_to_check=(f'{company.id}_vat_purchase_81_reverse',f'{company.id}_vat_77_purchase_reverse')
        tax_ids=env['ir.model.data'].search([
            ('name','in',taxes_to_check),
            ('model','=','account.tax'),
        ]).mapped('res_id')
        fortaxinenv['account.tax'].browse(tax_ids).with_context(active_test=False):
            forchildintax.children_tax_ids:
                ifchild.type_tax_usenotin('none',tax.type_tax_use):
                    #setthechildtoit'sparent'svalue
                    child.type_tax_use=tax.type_tax_use

    #Updatetaxes
    new_template_to_tax=update_taxes_from_templates(cr,'l10n_ch.l10nch_chart_template')
    ifnew_template_to_tax:
        _,new_tax_ids=zip(*new_template_to_tax)
        env=api.Environment(cr,SUPERUSER_ID,{})
        env['account.tax'].browse(new_tax_ids).active=True
