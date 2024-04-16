#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


fromflectraimportfields,models

#inthisfile,wemostlyaddthetagtranslate=Trueonexistingfieldsthatwenowwanttobetranslated

classAccountAccountTag(models.Model):
    _inherit='account.account.tag'

    name=fields.Char(translate=True)

classAccountAccountTemplate(models.Model):
    _inherit='account.account.template'

    name=fields.Char(translate=True)


classAccountAccount(models.Model):
    _inherit='account.account'

    name=fields.Char(translate=True)

classAccountGroupTemplate(models.Model):
    _inherit='account.group.template'

    name=fields.Char(translate=True)

classAccountGroup(models.Model):
    _inherit='account.group'

    name=fields.Char(translate=True)

classAccountTax(models.Model):
    _inherit='account.tax'

    name=fields.Char(translate=True)
    description=fields.Char(translate=True)


classAccountTaxTemplate(models.Model):
    _inherit='account.tax.template'

    name=fields.Char(translate=True)
    description=fields.Char(translate=True)


classAccountChartTemplate(models.Model):
    _inherit='account.chart.template'
    _order='name'

    name=fields.Char(translate=True)
    spoken_languages=fields.Char(string='SpokenLanguages',help="Stateherethelanguagesforwhichthetranslationsoftemplatescouldbeloadedatthetimeofinstallationofthislocalizationmoduleandcopiedinthefinalobjectwhengeneratingthemfromtemplates.Youmustprovidethelanguagecodesseparatedby';'")


classAccountFiscalPosition(models.Model):
    _inherit='account.fiscal.position'

    name=fields.Char(translate=True)
    note=fields.Text(translate=True)


classAccountFiscalPositionTemplate(models.Model):
    _inherit='account.fiscal.position.template'

    name=fields.Char(translate=True)
    note=fields.Text(translate=True)


classAccountJournal(models.Model):
    _inherit='account.journal'

    name=fields.Char(translate=True)


classAccountAnalyticAccount(models.Model):
    _inherit='account.analytic.account'

    name=fields.Char(translate=True)


classAccountTaxReportLine(models.Model):
    _inherit='account.tax.report.line'

    name=fields.Char(translate=True)
    tag_name=fields.Char(translate=True)


classResCountryState(models.Model):
    _inherit='res.country.state'

    name=fields.Char(translate=True)
