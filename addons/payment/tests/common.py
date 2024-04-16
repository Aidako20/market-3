#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon


classPaymentAcquirerCommon(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.currency_euro=cls.env.ref('base.EUR')
        cls.country_belgium=cls.env.ref('base.be')
        cls.country_france=cls.env.ref('base.fr')

        #dictpartnervalues
        cls.buyer_values={
            'partner_name':'NorbertBuyer',
            'partner_lang':'en_US',
            'partner_email':'norbert.buyer@example.com',
            'partner_address':'HugeStreet2/543',
            'partner_phone':'003212345678',
            'partner_city':'SinCity',
            'partner_zip':'1000',
            'partner_country':cls.country_belgium,
            'partner_country_id':cls.country_belgium.id,
            'partner_country_name':'Belgium',
            'billing_partner_name':'NorbertBuyer',
            'billing_partner_commercial_company_name':'BigCompany',
            'billing_partner_lang':'en_US',
            'billing_partner_email':'norbert.buyer@example.com',
            'billing_partner_address':'HugeStreet2/543',
            'billing_partner_phone':'003212345678',
            'billing_partner_city':'SinCity',
            'billing_partner_zip':'1000',
            'billing_partner_country':cls.country_belgium,
            'billing_partner_country_id':cls.country_belgium.id,
            'billing_partner_country_name':'Belgium',
        }

        #testpartner
        cls.buyer=cls.env['res.partner'].create({
            'name':'NorbertBuyer',
            'lang':'en_US',
            'email':'norbert.buyer@example.com',
            'street':'HugeStreet',
            'street2':'2/543',
            'phone':'003212345678',
            'city':'SinCity',
            'zip':'1000',
            'country_id':cls.country_belgium.id})
        cls.buyer_id=cls.buyer.id
