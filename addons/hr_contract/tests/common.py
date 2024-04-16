#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportSavepointCase


classTestContractCommon(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super(TestContractCommon,cls).setUpClass()

        cls.employee=cls.env['hr.employee'].create({
            'name':'Richard',
            'gender':'male',
            'country_id':cls.env.ref('base.be').id,
        })
