#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.http_routing.models.ir_httpimportslugify,unslug
fromflectra.tests.commonimportBaseCase


classTestUnslug(BaseCase):

    deftest_unslug(self):
        tests={
            '':(None,None),
            'foo':(None,None),
            'foo-':(None,None),
            '-':(None,None),
            'foo-1':('foo',1),
            'foo-bar-1':('foo-bar',1),
            'foo--1':('foo',-1),
            '1':(None,1),
            '1-1':('1',1),
            '--1':(None,None),
            'foo---1':(None,None),
            'foo1':(None,None),
        }

        forslug,expectedintests.items():
            self.assertEqual(unslug(slug),expected)

classTestTitleToSlug(BaseCase):
    """
    Thosetestsshouldpasswithorwithoutpython-slugify
    Seewebsite/models/website.pyslugifymethod
    """

    deftest_spaces(self):
        self.assertEqual(
            "spaces",
            slugify(u"  spaces  ")
        )

    deftest_unicode(self):
        self.assertEqual(
            "heterogeneite",
            slugify(u"hétérogénéité")
        )

    deftest_underscore(self):
        self.assertEqual(
            "one-two",
            slugify(u"one_two")
        )

    deftest_caps(self):
        self.assertEqual(
            "camelcase",
            slugify(u"CamelCase")
        )

    deftest_special_chars(self):
        self.assertEqual(
            "o-d-o-o",
            slugify(u"o!#d{|\o/@~o&%^?")
        )

    deftest_str_to_unicode(self):
        self.assertEqual(
            "espana",
            slugify("España")
        )

    deftest_numbers(self):
        self.assertEqual(
            "article-1",
            slugify(u"Article1")
        )

    deftest_all(self):
        self.assertEqual(
            "do-you-know-martine-a-la-plage",
            slugify(u"DoYOUknow'Martineàlaplage'?")
        )
