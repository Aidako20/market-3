#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.testsimportcommon
fromflectra.tests.commonimportForm,SavepointCase


CH_ISR_ISSUER='01-162-8'
CH_IBAN='CH1538815158384538437'
FR_IBAN='FR8387234133870990794002530'
CH_POST_IBAN='CH0909000000100080607'
CH_POSTAL_ACC='10-8060-7'


classTestOnchangePostal(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        cls.env=cls.env(context=dict(cls.env.context,tracking_disable=True))
        cls.partner=cls.env.ref('base.res_partner_12')
        cls.ch_bank=cls.env['res.bank'].create({
            'name':'AlternativeBankSchweizAG',
            'bic':'ALSWCH21XXX',
        })
        cls.post_bank=cls.env['res.bank'].search(
            [('bic','=','POFICHBEXXX')])
        ifnotcls.post_bank:
            cls.post_bank=cls.env['res.bank'].create({
                'name':'PostFinanceAG',
                'bic':'POFICHBEXXX',
            })

    defnew_partner_bank_form(self):
        form=Form(
            self.env['res.partner.bank'],
            view="l10n_ch.isr_partner_bank_form",
        )
        form.partner_id=self.partner
        returnform

    deftest_onchange_acc_number_isr_issuer(self):
        """TheuserenteredISRissuernumberintoacc_number

        Wedetectandmoveittol10n_ch_postal.
        Itmustbemovedasitisnotunique.
        """
        bank_acc=self.new_partner_bank_form()
        bank_acc.acc_number=CH_ISR_ISSUER
        account=bank_acc.save()

        self.assertEqual(
            account.acc_number,
            "{}{}".format(CH_ISR_ISSUER,self.partner.name)
        )
        self.assertEqual(account.l10n_ch_postal,CH_ISR_ISSUER)
        self.assertEqual(account.acc_type,'postal')

    deftest_onchange_acc_number_postal(self):
        """Theuserenteredpostalnumberintoacc_number

        Wedetectandcopyittol10n_ch_postal.
        """
        bank_acc=self.new_partner_bank_form()
        bank_acc.acc_number=CH_POSTAL_ACC
        account=bank_acc.save()

        self.assertEqual(account.acc_number,CH_POSTAL_ACC)
        self.assertEqual(account.l10n_ch_postal,CH_POSTAL_ACC)
        self.assertEqual(account.acc_type,'postal')

    deftest_onchange_acc_number_iban_ch(self):
        bank_acc=self.new_partner_bank_form()
        bank_acc.acc_number=CH_IBAN
        account=bank_acc.save()

        self.assertEqual(account.acc_number,CH_IBAN)
        self.assertFalse(account.l10n_ch_postal)
        self.assertEqual(account.acc_type,'iban')

    deftest_onchange_acc_number_iban_ch_postfinance(self):
        """TheuserenterapostalIBAN,postalnumbercanbededuced"""
        bank_acc=self.new_partner_bank_form()
        bank_acc.acc_number=CH_POST_IBAN
        account=bank_acc.save()

        self.assertEqual(account.acc_number,CH_POST_IBAN)
        self.assertEqual(account.l10n_ch_postal,CH_POSTAL_ACC)
        self.assertEqual(account.acc_type,'iban')

    deftest_onchange_acc_number_iban_foreign(self):
        """CheckIBANstillworkschanged"""
        bank_acc=self.new_partner_bank_form()
        bank_acc.acc_number=FR_IBAN
        account=bank_acc.save()

        self.assertEqual(account.acc_number,FR_IBAN)
        self.assertFalse(account.l10n_ch_postal)
        self.assertEqual(account.acc_type,'iban')

    deftest_onchange_acc_number_none(self):
        """Checkmiscformatstillworks"""
        bank_acc=self.new_partner_bank_form()
        bank_acc.acc_number='anything'
        account=bank_acc.save()

        self.assertEqual(account.acc_number,'anything')
        self.assertFalse(account.l10n_ch_postal)
        self.assertEqual(account.acc_type,'bank')
