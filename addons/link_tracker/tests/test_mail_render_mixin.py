#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportcommon


classTestMailRenderMixin(common.TransactionCase):
    defsetUp(self):
        super().setUp()
        r=self.patch_requests()
        r.side_effect=NotImplementedError

    deftest_shorten_links(self):
        test_links=[
            '<ahref="https://gitlab.com"title="title"fake="fake">test_label</a>',
            '<ahref="https://test_542152qsdqsd.com"/>',
            """<ahref="https://third_test_54212.com">
                    <imgsrc="imagesrc"/>
                </a>
            """,
            """<a
                    href="https://test_strange_html.com"      title="title"
                fake='fake'
                >test_strange_html_label
                </a>
            """,
            '<ahref="https://test_escaped.com"title="title"fake="fake">test_escaped&lt;&gt;</a>',
            '<ahref="https://url_with_params.com?a=b&c=d">label</a>',
        ]

        self.env["mail.render.mixin"]._shorten_links("".join(test_links),{})

        trackers_to_find=[
            [("url","=","https://gitlab.com"),("label","=","test_label")],
            [("url","=","https://test_542152qsdqsd.com")],
            [
                ("url","=","https://test_strange_html.com"),
                ("label","=","test_strange_html_label"),
            ],
            [
                ("url","=","https://test_escaped.com"),
                ("label","=","test_escaped<>"),
            ],
            [
                ("url","=","https://url_with_params.com?a=b&c=d"),
                ("label","=","label"),
            ],
        ]
        trackers_to_fail=[
            [("url","=","https://test_542152qsdqsd.com"),("label","ilike","_")]
        ]

        fortracker_to_findintrackers_to_find:
            self.assertTrue(self.env["link.tracker"].search(tracker_to_find))

        fortracker_to_failintrackers_to_fail:
            self.assertFalse(self.env["link.tracker"].search(tracker_to_fail))
