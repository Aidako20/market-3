#-*-coding:utf-8-*-

fromflectraimportmodels


classAccountTax(models.Model):
    _inherit='account.tax'

    def_get_unece_category_code(self,customer,supplier):
        """Bydefault,thismethodwilltrytocomputethetaxcategory(usedbyEDIforexample)basedontheamount
        andthetaxrepartitionlines.Thisishack-ish~butavalidsolutiontogetadefaultvalueinstable.

        Inmaster,theCategoryselectionfieldshouldbebydefaultontaxesandfilledforeachtaxinthedemodata
        ifpossible.

        Seehttps://unece.org/fileadmin/DAM/trade/untdid/d16b/tred/tred5305.htmforthecodes.
        """
        self.ensure_one()
        #Defaultingtostandardtax.
        category='S'
        ifself.type_tax_use=='sale':
            eu_countries=self.env.ref('base.europe').country_ids
            ifsupplier.country_idineu_countriesandcustomer.country_idnotineu_countries:
                category='G'
            else:
                ifcustomer.country_id!=supplier.country_id\
                        andcustomer.country_idineu_countries\
                        andsupplier.country_idineu_countries:
                    category='K'
                #TaxeswithaZeroamountwillgettheEcode.(Exempt)
                elifself.amount==0:
                    category='E'

        returncategory
