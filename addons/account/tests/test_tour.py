#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests


@flectra.tests.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpCase):

    deftest_01_account_tour(self):
        #Thistourdoesn'tworkwithdemodataonrunbot
        all_moves=self.env['account.move'].search([('move_type','!=','entry')])
        all_moves.button_draft()
        all_moves.posted_before=False
        all_moves.unlink()
        self.start_tour("/web",'account_tour',login="admin")
