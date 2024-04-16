#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api,_


classResPartnerBank(models.Model):
    _inherit='res.partner.bank'

    def_get_qr_vals(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        ifqr_method=='sct_qr':
            comment=(free_communicationor'')ifnotstructured_communicationelse''

            qr_code_vals=[
                'BCD',                                                 #ServiceTag
                '002',                                                 #Version
                '1',                                                   #CharacterSet
                'SCT',                                                 #IdentificationCode
                self.bank_bicor'',                                   #BICoftheBeneficiaryBank
                (self.acc_holder_nameorself.partner_id.name)[:71],   #NameoftheBeneficiary
                self.sanitized_acc_number,                             #AccountNumberoftheBeneficiary
                currency.name+str(amount),                           #Currency+AmountoftheTransferinEUR
                '',                                                    #PurposeoftheTransfer
                (structured_communicationor'')[:36],                 #RemittanceInformation(Structured)
                comment[:141],                                         #RemittanceInformation(Unstructured)(can'tbesetifthereisastructuredone)
                '',                                                    #BeneficiarytoOriginatorInformation
            ]
            returnqr_code_vals
        returnsuper()._get_qr_vals(qr_method,amount,currency,debtor_partner,free_communication,structured_communication)

    def_get_qr_code_generation_params(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        ifqr_method=='sct_qr':
            return{
                'barcode_type':'QR',
                'width':128,
                'height':128,
                'humanreadable':1,
                'value':'\n'.join(self._get_qr_vals(qr_method,amount,currency,debtor_partner,free_communication,structured_communication)),
            }
        returnsuper()._get_qr_code_generation_params(qr_method,amount,currency,debtor_partner,free_communication,structured_communication)

    def_eligible_for_qr_code(self,qr_method,debtor_partner,currency):
        ifqr_method=='sct_qr':

            #SomecountriessharethesameIBANcountrycode
            #(e.g.ÅlandIslandsandFinlandIBANsare'FI',butÅlandIslands'codeis'AX').
            sepa_country_codes=self.env.ref('base.sepa_zone').country_ids.mapped('code')
            non_iban_codes={'AX','NC','YT','TF','BL','RE','MF','GP','PM','PF','GF','MQ','JE','GG','IM'}
            sepa_iban_codes={codeforcodeinsepa_country_codesifcodenotinnon_iban_codes}

            returncurrency.name=='EUR'andself.acc_type=='iban'andself.sanitized_acc_number[:2]insepa_iban_codes

        returnsuper()._eligible_for_qr_code(qr_method,debtor_partner,currency)

    def_check_for_qr_code_errors(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        ifqr_method=='sct_qr':
            ifnotself.acc_holder_nameandnotself.partner_id.name:
                return_("Theaccountreceivingthepaymentmusthaveanaccountholdernameorpartnernameset.")

        returnsuper()._check_for_qr_code_errors(qr_method,amount,currency,debtor_partner,free_communication,structured_communication)

    @api.model
    def_get_available_qr_methods(self):
        rslt=super()._get_available_qr_methods()
        rslt.append(('sct_qr',_("SEPACreditTransferQR"),20))
        returnrslt
