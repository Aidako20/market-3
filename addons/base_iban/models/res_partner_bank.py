#-*-coding:utf-8-*-

importre

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError


defnormalize_iban(iban):
    returnre.sub('[\W_]','',ibanor'')

defpretty_iban(iban):
    """returnibaningroupsoffourcharactersseparatedbyasinglespace"""
    try:
        validate_iban(iban)
        iban=''.join([iban[i:i+4]foriinrange(0,len(iban),4)])
    exceptValidationError:
        pass
    returniban

defget_bban_from_iban(iban):
    """ReturnsthebasicbankaccountnumbercorrespondingtoanIBAN.
        Note:theBBANisnotthesameasthedomesticbankaccountnumber!
        TherelationbetweenIBAN,BBANanddomesticcanbefoundhere:http://www.ecbs.org/iban.htm
    """
    returnnormalize_iban(iban)[4:]

defvalidate_iban(iban):
    iban=normalize_iban(iban)
    ifnotiban:
        raiseValidationError(_("ThereisnoIBANcode."))

    country_code=iban[:2].lower()
    ifcountry_codenotin_map_iban_template:
        raiseValidationError(_("TheIBANisinvalid,itshouldbeginwiththecountrycode"))

    iban_template=_map_iban_template[country_code]
    iflen(iban)!=len(iban_template.replace('',''))ornotre.fullmatch("[a-zA-Z0-9]+",iban):
        raiseValidationError(_("TheIBANdoesnotseemtobecorrect.Youshouldhaveenteredsomethinglikethis%s\n"
            "WhereB=Nationalbankcode,S=Branchcode,C=AccountNo,k=Checkdigit")%iban_template)

    check_chars=iban[4:]+iban[:4]
    digits=int(''.join(str(int(char,36))forcharincheck_chars)) #BASE36:0..9,A..Z->0..35
    ifdigits%97!=1:
        raiseValidationError(_("ThisIBANdoesnotpassthevalidationcheck,pleaseverifyit."))


classResPartnerBank(models.Model):
    _inherit="res.partner.bank"

    @api.model
    def_get_supported_account_types(self):
        rslt=super(ResPartnerBank,self)._get_supported_account_types()
        rslt.append(('iban',_('IBAN')))
        returnrslt

    @api.model
    defretrieve_acc_type(self,acc_number):
        try:
            validate_iban(acc_number)
            return'iban'
        exceptValidationError:
            returnsuper(ResPartnerBank,self).retrieve_acc_type(acc_number)

    defget_bban(self):
        ifself.acc_type!='iban':
            raiseUserError(_("CannotcomputetheBBANbecausetheaccountnumberisnotanIBAN."))
        returnget_bban_from_iban(self.acc_number)

    @api.model
    defcreate(self,vals):
        ifvals.get('acc_number'):
            try:
                validate_iban(vals['acc_number'])
                vals['acc_number']=pretty_iban(normalize_iban(vals['acc_number']))
            exceptValidationError:
                pass
        returnsuper(ResPartnerBank,self).create(vals)

    defwrite(self,vals):
        ifvals.get('acc_number'):
            try:
                validate_iban(vals['acc_number'])
                vals['acc_number']=pretty_iban(normalize_iban(vals['acc_number']))
            exceptValidationError:
                pass
        returnsuper(ResPartnerBank,self).write(vals)

    @api.constrains('acc_number')
    def_check_iban(self):
        forbankinself:
            ifbank.acc_type=='iban':
                validate_iban(bank.acc_number)

    defcheck_iban(self,iban=''):
        try:
            validate_iban(iban)
            returnTrue
        exceptValidationError:
            returnFalse

#MapISO3166-1->IBANtemplate,asdescribedhere:
#http://en.wikipedia.org/wiki/International_Bank_Account_Number#IBAN_formats_by_country
_map_iban_template={
    'ad':'ADkkBBBBSSSSCCCCCCCCCCCC', #Andorra
    'ae':'AEkkBBBCCCCCCCCCCCCCCCC', #UnitedArabEmirates
    'al':'ALkkBBBSSSSKCCCCCCCCCCCCCCCC', #Albania
    'at':'ATkkBBBBBCCCCCCCCCCC', #Austria
    'az':'AZkkBBBBCCCCCCCCCCCCCCCCCCCC', #Azerbaijan
    'ba':'BAkkBBBSSSCCCCCCCCKK', #BosniaandHerzegovina
    'be':'BEkkBBBCCCCCCCXX', #Belgium
    'bg':'BGkkBBBBSSSSDDCCCCCCCC', #Bulgaria
    'bh':'BHkkBBBBCCCCCCCCCCCCCC', #Bahrain
    'br':'BRkkBBBBBBBBSSSSSCCCCCCCCCCTN', #Brazil
    'by':'BYkkBBBBAAAACCCCCCCCCCCCCCCC', #Belarus
    'ch':'CHkkBBBBBCCCCCCCCCCCC', #Switzerland
    'cr':'CRkkBBBCCCCCCCCCCCCCCC', #CostaRica
    'cy':'CYkkBBBSSSSSCCCCCCCCCCCCCCCC', #Cyprus
    'cz':'CZkkBBBBSSSSSSCCCCCCCCCC', #CzechRepublic
    'de':'DEkkBBBBBBBBCCCCCCCCCC', #Germany
    'dk':'DKkkBBBBCCCCCCCCCC', #Denmark
    'do':'DOkkBBBBCCCCCCCCCCCCCCCCCCCC', #DominicanRepublic
    'ee':'EEkkBBSSCCCCCCCCCCCK', #Estonia
    'es':'ESkkBBBBSSSSKKCCCCCCCCCC', #Spain
    'fi':'FIkkBBBBBBCCCCCCCK', #Finland
    'fo':'FOkkCCCCCCCCCCCCCC', #FaroeIslands
    'fr':'FRkkBBBBBGGGGGCCCCCCCCCCCKK', #France
    'gb':'GBkkBBBBSSSSSSCCCCCCCC', #UnitedKingdom
    'ge':'GEkkBBCCCCCCCCCCCCCCCC', #Georgia
    'gi':'GIkkBBBBCCCCCCCCCCCCCCC', #Gibraltar
    'gl':'GLkkBBBBCCCCCCCCCC', #Greenland
    'gr':'GRkkBBBSSSSCCCCCCCCCCCCCCCC', #Greece
    'gt':'GTkkBBBBMMTTCCCCCCCCCCCCCCCC', #Guatemala
    'hr':'HRkkBBBBBBBCCCCCCCCCC', #Croatia
    'hu':'HUkkBBBSSSSCCCCCCCCCCCCCCCCC', #Hungary
    'ie':'IEkkBBBBSSSSSSCCCCCCCC', #Ireland
    'il':'ILkkBBBSSSCCCCCCCCCCCCC', #Israel
    'is':'ISkkBBBBSSCCCCCCXXXXXXXXXX', #Iceland
    'it':'ITkkKBBBBBSSSSSCCCCCCCCCCCC', #Italy
    'jo':'JOkkBBBBNNNNCCCCCCCCCCCCCCCCCC', #Jordan
    'kw':'KWkkBBBBCCCCCCCCCCCCCCCCCCCCCC', #Kuwait
    'kz':'KZkkBBBCCCCCCCCCCCCC', #Kazakhstan
    'lb':'LBkkBBBBCCCCCCCCCCCCCCCCCCCC', #Lebanon
    'li':'LIkkBBBBBCCCCCCCCCCCC', #Liechtenstein
    'lt':'LTkkBBBBBCCCCCCCCCCC', #Lithuania
    'lu':'LUkkBBBCCCCCCCCCCCCC', #Luxembourg
    'lv':'LVkkBBBBCCCCCCCCCCCCC', #Latvia
    'mc':'MCkkBBBBBGGGGGCCCCCCCCCCCKK', #Monaco
    'md':'MDkkBBCCCCCCCCCCCCCCCCCC', #Moldova
    'me':'MEkkBBBCCCCCCCCCCCCCKK', #Montenegro
    'mk':'MKkkBBBCCCCCCCCCCKK', #Macedonia
    'mr':'MRkkBBBBBSSSSSCCCCCCCCCCCKK', #Mauritania
    'mt':'MTkkBBBBSSSSSCCCCCCCCCCCCCCCCCC', #Malta
    'mu':'MUkkBBBBBBSSCCCCCCCCCCCCCCCCCC', #Mauritius
    'nl':'NLkkBBBBCCCCCCCCCC', #Netherlands
    'no':'NOkkBBBBCCCCCCK', #Norway
    'pk':'PKkkBBBBCCCCCCCCCCCCCCCC', #Pakistan
    'pl':'PLkkBBBSSSSKCCCCCCCCCCCCCCCC', #Poland
    'ps':'PSkkBBBBXXXXXXXXXCCCCCCCCCCCC', #Palestinian
    'pt':'PTkkBBBBSSSSCCCCCCCCCCCKK', #Portugal
    'qa':'QAkkBBBBCCCCCCCCCCCCCCCCCCCCC', #Qatar
    'ro':'ROkkBBBBCCCCCCCCCCCCCCCC', #Romania
    'rs':'RSkkBBBCCCCCCCCCCCCCKK', #Serbia
    'sa':'SAkkBBCCCCCCCCCCCCCCCCCC', #SaudiArabia
    'se':'SEkkBBBBCCCCCCCCCCCCCCCC', #Sweden
    'si':'SIkkBBSSSCCCCCCCCKK', #Slovenia
    'sk':'SKkkBBBBSSSSSSCCCCCCCCCC', #Slovakia
    'sm':'SMkkKBBBBBSSSSSCCCCCCCCCCCC', #SanMarino
    'tn':'TNkkBBSSSCCCCCCCCCCCCCCC', #Tunisia
    'tr':'TRkkBBBBBRCCCCCCCCCCCCCCCC', #Turkey
    'ua':'UAkkBBBBBBCCCCCCCCCCCCCCCCCCC', #Ukraine
    'vg':'VGkkBBBBCCCCCCCCCCCCCCCC', #VirginIslands
    'xk':'XKkkBBBBCCCCCCCCCCCC', #Kosovo
}
