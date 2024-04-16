#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimporttagged
fromflectra.tests.commonimportTransactionCase


@tagged('post_install','-at_install')
classTestGetCurrentWebsite(TransactionCase):

    deftest_01_get_current_website_id(self):
        """Makesure`_get_current_website_idworks`."""

        Website=self.env['website']

        #cleaninitialstate
        website1=self.env.ref('website.default_website')
        website1.domain=''
        website1.country_group_ids=False

        website2=Website.create({
            'name':'MyWebsite2',
            'domain':'',
            'country_group_ids':False,
        })

        country1=self.env['res.country'].create({'name':"MyCountry1"})
        country2=self.env['res.country'].create({'name':"MyCountry2"})
        country3=self.env['res.country'].create({'name':"MyCountry3"})
        country4=self.env['res.country'].create({'name':"MyCountry4"})
        country5=self.env['res.country'].create({'name':"MyCountry5"})

        country_group_1_2=self.env['res.country.group'].create({
            'name':"MyCountryGroup1-2",
            'country_ids':[(6,0,(country1+country2+country5).ids)],
        })
        country_group_3=self.env['res.country.group'].create({
            'name':"MyCountryGroup3",
            'country_ids':[(6,0,(country3+country5).ids)],
        })

        #CASE:nodomain,nocountry:getfirst
        self.assertEqual(Website._get_current_website_id('',False),website1.id)
        self.assertEqual(Website._get_current_website_id('',country3.id),website1.id)

        #CASE:nodomain,givencountry:getbycountry
        website1.country_group_ids=country_group_1_2
        website2.country_group_ids=country_group_3

        self.assertEqual(Website._get_current_website_id('',country1.id),website1.id)
        self.assertEqual(Website._get_current_website_id('',country2.id),website1.id)
        self.assertEqual(Website._get_current_website_id('',country3.id),website2.id)

        #CASE:nodomain,wrongcountry:getfirst
        self.assertEqual(Website._get_current_website_id('',country4.id),Website.search([]).sorted('country_group_ids')[0].id)

        #CASE:nodomain,multiplecountry:getfirst
        self.assertEqual(Website._get_current_website_id('',country5.id),website1.id)

        #setupdomain
        website1.domain='my-site-1.fr'
        website2.domain='https://my2ndsite.com:80'

        website1.country_group_ids=False
        website2.country_group_ids=False

        #CASE:domainset:getmatchingdomain
        self.assertEqual(Website._get_current_website_id('my-site-1.fr',False),website1.id)

        #CASE:domainset:getmatchingdomain(schemeandportsupported)
        self.assertEqual(Website._get_current_website_id('my-site-1.fr:7073',False),website1.id)

        self.assertEqual(Website._get_current_website_id('my2ndsite.com:80',False),website2.id)
        self.assertEqual(Website._get_current_website_id('my2ndsite.com:7073',False),website2.id)
        self.assertEqual(Website._get_current_website_id('my2ndsite.com',False),website2.id)

        #CASE:domainset,wrongdomain:getfirst
        self.assertEqual(Website._get_current_website_id('test.com',False),website1.id)

        #CASE:subdomain:notsupported
        self.assertEqual(Website._get_current_website_id('www.my2ndsite.com',False),website1.id)

        #CASE:domainset,givencountry:getbydomaininpriority
        website1.country_group_ids=country_group_1_2
        website2.country_group_ids=country_group_3

        self.assertEqual(Website._get_current_website_id('my2ndsite.com',country1.id),website2.id)
        self.assertEqual(Website._get_current_website_id('my2ndsite.com',country2.id),website2.id)
        self.assertEqual(Website._get_current_website_id('my-site-1.fr',country3.id),website1.id)

        #CASE:domainset,wrongcountry:getfirstfordomain
        self.assertEqual(Website._get_current_website_id('my2ndsite.com',country4.id),website2.id)

        #CASE:domainset,multiplecountry:getfirstfordomain
        website1.domain=website2.domain
        self.assertEqual(Website._get_current_website_id('my2ndsite.com',country5.id),website1.id)

        #CASE:overlappingdomain:getexactmatch
        website1.domain='site-1.com'
        website2.domain='even-better-site-1.com'
        self.assertEqual(Website._get_current_website_id('site-1.com',False),website1.id)
        self.assertEqual(Website._get_current_website_id('even-better-site-1.com',False),website2.id)

        #CASE:caseinsensitive
        website1.domain='Site-1.com'
        website2.domain='Even-Better-site-1.com'
        self.assertEqual(Website._get_current_website_id('sitE-1.com',False),website1.id)
        self.assertEqual(Website._get_current_website_id('even-beTTer-site-1.com',False),website2.id)

        #CASE:samedomain,differentport
        website1.domain='site-1.com:80'
        website2.domain='site-1.com:81'
        self.assertEqual(Website._get_current_website_id('site-1.com:80',False),website1.id)
        self.assertEqual(Website._get_current_website_id('site-1.com:81',False),website2.id)
        self.assertEqual(Website._get_current_website_id('site-1.com:82',False),website1.id)
        self.assertEqual(Website._get_current_website_id('site-1.com',False),website1.id)

    deftest_02_signup_user_website_id(self):
        website=self.env.ref('website.default_website')
        website.specific_user_account=True

        user=self.env['res.users'].create({'website_id':website.id,'login':'sad@mail.com','name':'HopeFully'})
        self.assertTrue(user.website_id==user.partner_id.website_id==website)
