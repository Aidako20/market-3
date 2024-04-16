#-*-coding:utf-8-*-

importdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon


classTestMembershipCommon(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        #Testmemberships
        cls.membership_1=cls.env['product.product'].create({
            'membership':True,
            'membership_date_from':datetime.date.today()+relativedelta(days=-2),
            'membership_date_to':datetime.date.today()+relativedelta(months=1),
            'name':'BasicLimited',
            'type':'service',
            'list_price':100.00,
        })

        #Testpeople
        cls.partner_1=cls.env['res.partner'].create({
            'name':'IgnasseReblochon',
        })
        cls.partner_2=cls.env['res.partner'].create({
            'name':'MartinePoulichette',
            'free_member':True,
        })
