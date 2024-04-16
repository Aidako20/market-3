#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime
importstring
importre
importstdnum
fromstdnum.eu.vatimportcheck_vies
fromstdnum.exceptionsimportInvalidComponent
importlogging

fromflectraimportapi,models,tools,_
fromflectra.tools.miscimportustr
fromflectra.exceptionsimportValidationError


_logger=logging.getLogger(__name__)

_eu_country_vat={
    'GR':'EL'
}

_eu_country_vat_inverse={v:kfork,vin_eu_country_vat.items()}

_ref_vat={
    'al':'ALJ91402501L',
    'ar':'AR200-5536168-2or20055361682',
    'at':'ATU12345675',
    'au':'83914571673',
    'be':'BE0477472701',
    'bg':'BG1234567892',
    'ch':'CHE-123.456.788TVAorCHE-123.456.788MWSTorCHE-123.456.788IVA', #SwissbyYannickVaucher@Camptocamp
    'cl':'CL76086428-5',
    'co':'CO213123432-1orCO213.123.432-1',
    'cy':'CY10259033P',
    'cz':'CZ12345679',
    'de':'DE123456788',
    'dk':'DK12345674',
    'do':'DO1-01-85004-3or101850043',
    'ec':'EC1792060346-001',
    'ee':'EE123456780',
    'el':'EL12345670',
    'es':'ESA12345674',
    'fi':'FI12345671',
    'fr':'FR23334175221',
    'gb':'GB123456782orXI123456782',
    'gr':'GR12345670',
    'hu':'HU12345676or12345678-1-11or8071592153',
    'hr':'HR01234567896', #Croatia,contributedbyMilanTribuson
    'ie':'IE1234567FA',
    'in':"12AAAAA1234AAZA",
    'is':'IS062199',
    'it':'IT12345670017',
    'lt':'LT123456715',
    'lu':'LU12345613',
    'lv':'LV41234567891',
    'mc':'FR53000004605',
    'mt':'MT12345634',
    'mx':'MXGODE561231GR8orGODE561231GR8',
    'nl':'NL123456782B90',
    'no':'NO123456785',
    'pe':'10XXXXXXXXYor20XXXXXXXXYor15XXXXXXXXYor16XXXXXXXXYor17XXXXXXXXY',
    'ph':'123-456-789-123',
    'pl':'PL1234567883',
    'pt':'PT123456789',
    'ro':'RO1234567897',
    'rs':'RS101134702',
    'ru':'RU123456789047',
    'se':'SE123456789701',
    'si':'SI12345679',
    'sk':'SK2022749619',
    'sm':'SM24165',
    'tr':'TR1234567890(VERGINO)orTR17291716060(TCKIMLIKNO)', #LeventKarakas@EskaYazilimA.S.
    've':'V-12345678-1,V123456781,V-12.345.678-1',
    'xi':'XI123456782',
}

_region_specific_vat_codes={
    'xi',
    't',
}


classResPartner(models.Model):
    _inherit='res.partner'

    def_split_vat(self,vat):
        '''
        SplitstheVATNumbertogetthecountrycodeinafirstplaceandthecodeitselfinasecondplace.
        Thishastobedonebecausesomecountries'codeareonecharacterlonginsteadoftwo(i.e."T"forJapan)
        '''
        iflen(vat)>1andvat[1].isalpha():
            vat_country,vat_number=vat[:2].lower(),vat[2:].replace('','')
        else:
            vat_country,vat_number=vat[:1].lower(),vat[1:].replace('','')
        returnvat_country,vat_number

    @api.model
    defsimple_vat_check(self,country_code,vat_number):
        '''
        ChecktheVATnumberdependingofthecountry.
        http://sima-pc.com/nif.php
        '''
        ifnotustr(country_code).encode('utf-8').isalpha():
            returnFalse
        check_func_name='check_vat_'+country_code
        check_func=getattr(self,check_func_name,None)orgetattr(stdnum.util.get_cc_module(country_code,'vat'),'is_valid',None)
        ifnotcheck_func:
            #NoVATvalidationavailable,defaulttocheckthatthecountrycodeexists
            ifcountry_code.upper()=='EU':
                #Foreigncompaniesthattradewithnon-enterprisesintheEU
                #mayhaveaVATINstartingwith"EU"insteadofacountrycode.
                returnTrue
            country_code=_eu_country_vat_inverse.get(country_code,country_code)
            returnbool(self.env['res.country'].search([('code','=ilike',country_code)]))
        returncheck_func(vat_number)

    @api.model
    @tools.ormcache('vat')
    def_check_vies(self,vat):
        #StoretheVIESresultinthecache.Incaseanexceptionisraisedduringtherequest
        #(e.g.serviceunavailable),thefallbackonsimple_vat_checkisnotkeptincache.
        returncheck_vies(vat)

    @api.model
    defvies_vat_check(self,country_code,vat_number):
        try:
            #Validateagainst VATInformationExchangeSystem(VIES)
            #seealsohttp://ec.europa.eu/taxation_customs/vies/
            vies_result=self._check_vies(country_code.upper()+vat_number)
            returnvies_result['valid']
        exceptInvalidComponent:
            returnFalse
        exceptException:
            #seehttp://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl
            #FaultcodemaycontainINVALID_INPUT,SERVICE_UNAVAILABLE,MS_UNAVAILABLE,
            #TIMEOUTorSERVER_BUSY.Thereisnowaywecanvalidatetheinput
            #withVIESifanyofthesearise,includingthefirstone(itmeansinvalid
            #countrycodeoremptyVATnumber),sowefallbacktothesimplecheck.
            _logger.exception("FailedVIESVATcheck.")
            returnself.simple_vat_check(country_code,vat_number)

    @api.model
    deffix_eu_vat_number(self,country_id,vat):
        europe=self.env.ref('base.europe')
        country=self.env["res.country"].browse(country_id)
        ifnoteurope:
            europe=self.env["res.country.group"].search([('name','=','Europe')],limit=1)
        ifeuropeandcountryandcountry.idineurope.country_ids.ids:
            vat=re.sub('[^A-Za-z0-9]','',vat).upper()
            country_code=_eu_country_vat.get(country.code,country.code).upper()
            ifvat[:2]!=country_code:
                vat=country_code+vat
        returnvat

    @api.constrains('vat','country_id')
    defcheck_vat(self):
        #Thecontextkey'no_vat_validation'allowsyoutostore/setaVATnumberwithoutdoingvalidations.
        #ThisisforAPIpushesfromexternalplatformswhereyouhavenocontroloverVATnumbers.
        ifself.env.context.get('no_vat_validation'):
            return
        partners_with_vat=self.filtered('vat')
        ifnotpartners_with_vat:
            return
        ifself.env.context.get('company_id'):
            company=self.env['res.company'].browse(self.env.context['company_id'])
        else:
            company=self.env.company
        eu_countries=self.env.ref('base.europe').country_ids
        forpartnerinpartners_with_vat:
            is_eu_country=partner.commercial_partner_id.country_idineu_countries
            ifcompany.vat_check_viesandis_eu_countryandpartner.is_company:
                #forcefullVIESonlinecheck
                check_func=self.vies_vat_check
            else:
                #quickandpartialoff-linechecksumvalidation
                check_func=self.simple_vat_check

            failed_check=False
            #checkwithcountrycodeasprefixoftheTIN
            vat_country_code,vat_number=self._split_vat(partner.vat)
            vat_has_legit_country_code=self.env['res.country'].search([('code','=',vat_country_code.upper())])
            ifnotvat_has_legit_country_code:
                vat_has_legit_country_code=vat_country_code.lower()in_region_specific_vat_codes
            ifvat_has_legit_country_code:
                failed_check=notcheck_func(vat_country_code,vat_number)

            #iffails,checkwithcountrycodefromcountry
            partner_country_code=partner.commercial_partner_id.country_id.code
            if(notvat_has_legit_country_codeorfailed_check)andpartner_country_code:
                failed_check=notcheck_func(partner_country_code.lower(),partner.vat)

            #Weallowanynumberifitdoesn'tstartwithacountrycodeandthepartnerhasnocountry.
            #ThisisnecessarytosupportanORMlimitation:settingvatandcountry_idtogetheronacompany
            #triggerstwodistinctwriteonres.partner,oneforeachfield,bothtriggeringthisconstraint.
            #Ifvatissetbeforecountry_id,theconstraintmustnotbreak.

            iffailed_check:
                country_code=partner_country_codeorvat_country_code
                msg=partner._construct_constraint_msg(country_code.lower()ifcountry_codeelseNone)
                raiseValidationError(msg)

    def_construct_constraint_msg(self,country_code):
        self.ensure_one()
        vat_no="'CC##'(CC=CountryCode,##=VATNumber)"
        vat_no=_ref_vat.get(country_code)orvat_no
        ifself.env.context.get('company_id'):
            company=self.env['res.company'].browse(self.env.context['company_id'])
        else:
            company=self.env.company
        ifcompany.vat_check_vies:
            return'\n'+_(
                'TheVATnumber[%(vat)s]forpartner[%(name)s]eitherfailedtheVIESVATvalidationcheckordidnotrespecttheexpectedformat%(format)s.',
                vat=self.vat,
                name=self.name,
                format=vat_no
            )
        return'\n'+_(
            'TheVATnumber[%(vat)s]forpartner[%(name)s]doesnotseemtobevalid.\nNote:theexpectedformatis%(format)s',
            vat=self.vat,
            name=self.name,
            format=vat_no
        )

    __check_vat_al_re=re.compile(r'^[JKLM][0-9]{8}[A-Z]$')

    defcheck_vat_al(self,vat):
        """CheckAlbaniaVATnumber"""
        number=stdnum.util.get_cc_module('al','vat').compact(vat)

        iflen(number)==10andself.__check_vat_al_re.match(number):
            returnTrue
        returnFalse

    __check_tin_hu_individual_re=re.compile(r'^8\d{9}$')
    __check_tin_hu_companies_re=re.compile(r'^\d{8}-[1-5]-\d{2}$')

    defcheck_vat_hu(self,vat):
        """
            CheckHungaryVATnumberthatcanbeforexample'HU12345676or'xxxxxxxx-y-zz'or'8xxxxxxxxy'
            -Forxxxxxxxx-y-zz,'x'canbeanynumber,'y'isanumberbetween1and5dependingonthepersonandthe'zz'
              isusedforregioncode.
            -8xxxxxxxxy,Tinnumberforindividual,ithastostartwithan8andfinishwiththecheckdigit
        """
        companies=self.__check_tin_hu_companies_re.match(vat)
        ifcompanies:
            returnTrue
        individual=self.__check_tin_hu_individual_re.match(vat)
        ifindividual:
            returnTrue
        #Checkthevatnumber
        returnstdnum.util.get_cc_module('hu','vat').is_valid(vat)

    __check_vat_ch_re=re.compile(r'E([0-9]{9}|-[0-9]{3}\.[0-9]{3}\.[0-9]{3})(MWST|TVA|IVA)$')

    defcheck_vat_ch(self,vat):
        '''
        CheckSwitzerlandVATnumber.
        '''
        #AnewVATnumberformatinSwitzerlandhasbeenintroducedbetween2011and2013
        #https://www.estv.admin.ch/estv/fr/home/mehrwertsteuer/fachinformationen/steuerpflicht/unternehmens-identifikationsnummer--uid-.html
        #Theoldformat"TVA123456"isnotvalidsince2014
        #Acceptedformatare:(spacesareignored)
        #    CHE#########MWST
        #    CHE#########TVA
        #    CHE#########IVA
        #    CHE-###.###.###MWST
        #    CHE-###.###.###TVA
        #    CHE-###.###.###IVA
        #
        #/!\TheenglishabbreviationVATisnotvalid/!\

        match=self.__check_vat_ch_re.match(vat)

        ifmatch:
            #FornewTVAnumbers,thelastdigitisaMOD11checksumdigitbuildwithweightingpattern:5,4,3,2,7,6,5,4
            num=[sforsinmatch.group(1)ifs.isdigit()]       #getthedigitsonly
            factor=(5,4,3,2,7,6,5,4)
            csum=sum([int(num[i])*factor[i]foriinrange(8)])
            check=(11-(csum%11))%11
            returncheck==int(num[8])
        returnFalse

    def_ie_check_char(self,vat):
        vat=vat.zfill(8)
        extra=0
        ifvat[7]notin'W':
            ifvat[7].isalpha():
                extra=9*(ord(vat[7])-64)
            else:
                #invalid
                return-1
        checksum=extra+sum((8-i)*int(x)fori,xinenumerate(vat[:7]))
        return'WABCDEFGHIJKLMNOPQRSTUV'[checksum%23]

    defcheck_vat_ie(self,vat):
        """TemporaryIrelandVATvalidationtosupportthenewformat
        introducedinJanuary2013inIreland,untilupstreamisfixed.
        TODO:removewhenfixedupstream"""
        iflen(vat)notin(8,9)ornotvat[2:7].isdigit():
            returnFalse
        iflen(vat)==8:
            #Normalizepre-2013numbers:finalspaceor'W'notsignificant
            vat+=''
        ifvat[:7].isdigit():
            returnvat[7]==self._ie_check_char(vat[:7]+vat[8])
        elifvat[1]in(string.ascii_uppercase+'+*'):
            #Deprecatedformat
            #Seehttp://www.revenue.ie/en/online/third-party-reporting/reporting-payment-details/faqs.html#section3
            returnvat[7]==self._ie_check_char(vat[2:7]+vat[0]+vat[8])
        returnFalse

    #MexicanVATverification,contributedbyVauxoo
    #andPanosChristeas<p_christ@hol.gr>
    __check_vat_mx_re=re.compile(br"(?P<primeras>[A-Za-z\xd1\xf1&]{3,4})"\
                                   br"[\-_]?"\
                                   br"(?P<ano>[0-9]{2})(?P<mes>[01][0-9])(?P<dia>[0-3][0-9])"\
                                   br"[\-_]?"\
                                   br"(?P<code>[A-Za-z0-9&\xd1\xf1]{3})$")

    defcheck_vat_mx(self,vat):
        '''MexicanVATverification

        VerificarRFCMéxico
        '''
        #weconvertto8-bitencoding,tohelptheregexparseonlybytes
        vat=ustr(vat).encode('iso8859-1')
        m=self.__check_vat_mx_re.match(vat)
        ifnotm:
            #Novalidformat
            returnFalse
        try:
            ano=int(m.group('ano'))
            ifano>30:
                ano=1900+ano
            else:
                ano=2000+ano
            datetime.date(ano,int(m.group('mes')),int(m.group('dia')))
        exceptValueError:
            returnFalse

        #Validformatandvaliddate
        returnTrue

    #NetherlandsVATverification
    __check_vat_nl_re=re.compile("(?:NL)?[0-9A-Z+*]{10}[0-9]{2}")

    defcheck_vat_nl(self,vat):
        """
        TemporaryNetherlandsVATvalidationtosupportthenewformatintroducedinJanuary2020,
        untilupstreamisfixed.

        Algorithmdetail:http://kleineondernemer.nl/index.php/nieuw-btw-identificatienummer-vanaf-1-januari-2020-voor-eenmanszaken

        TODO:removewhenfixedupstream
        """

        try:
            fromstdnum.utilimportclean
            fromstdnum.nl.bsnimportchecksum
        exceptImportError:
            returnTrue

        vat=clean(vat,'-.').upper().strip()

        #Removetheprefix
        ifvat.startswith("NL"):
            vat=vat[2:]

        ifnotlen(vat)==12:
            returnFalse

        #Checktheformat
        match=self.__check_vat_nl_re.match(vat)
        ifnotmatch:
            returnFalse

        #Matchletterstointegers
        char_to_int={k:str(ord(k)-55)forkinstring.ascii_uppercase}
        char_to_int['+']='36'
        char_to_int['*']='37'

        #2possiblechecks:
        #-Fornaturalpersons
        #-Fornon-naturalpersonsandcombinationsofnaturalpersons(company)

        #Naturalperson=>mod97fullchecksum
        check_val_natural='2321'
        forxinvat:
            check_val_natural+=xifx.isdigit()elsechar_to_int[x]
        ifint(check_val_natural)%97==1:
            returnTrue

        #Company=>weighted(9->2)mod11onbsn
        vat=vat[:-3]
        ifvat.isdigit()andchecksum(vat)==0:
            returnTrue

        returnFalse

    #NorwayVATvalidation,contributedbyRolvRåen(adEgo)<rora@adego.no>
    #SupportforMVAsuffixcontributedbyBringsvorConsultingAS(bringsvor@bringsvor.com)
    defcheck_vat_no(self,vat):
        """
        CheckNorwayVATnumber.Seehttp://www.brreg.no/english/coordination/number.html
        """
        iflen(vat)==12andvat.upper().endswith('MVA'):
            vat=vat[:-3]#StrictlyspeakingweshouldenforcethesuffixMVAbut...

        iflen(vat)!=9:
            returnFalse
        try:
            int(vat)
        exceptValueError:
            returnFalse

        sum=(3*int(vat[0]))+(2*int(vat[1]))+\
            (7*int(vat[2]))+(6*int(vat[3]))+\
            (5*int(vat[4]))+(4*int(vat[5]))+\
            (3*int(vat[6]))+(2*int(vat[7]))

        check=11-(sum%11)
        ifcheck==11:
            check=0
        ifcheck==10:
            #10isnotavalidcheckdigitforanorganizationnumber
            returnFalse
        returncheck==int(vat[8])

    #PeruvianVATvalidation,contributedbyVauxoo
    defcheck_vat_pe(self,vat):
        iflen(vat)!=11ornotvat.isdigit():
            returnFalse
        dig_check=11-(sum([int('5432765432'[f])*int(vat[f])forfinrange(0,10)])%11)
        ifdig_check==10:
            dig_check=0
        elifdig_check==11:
            dig_check=1
        returnint(vat[10])==dig_check

    #PhilippinesTIN(+branchcode)validation
    __check_vat_ph_re=re.compile(r"\d{3}-\d{3}-\d{3}(-\d{3,5})?$")

    defcheck_vat_ph(self,vat):
        returnlen(vat)>=11andlen(vat)<=17andself.__check_vat_ph_re.match(vat)

    defcheck_vat_ru(self,vat):
        '''
        CheckRussiaVATnumber.
        Methodcopiedfromvatnumber1.2libhttps://code.google.com/archive/p/vatnumber/
        '''
        iflen(vat)!=10andlen(vat)!=12:
            returnFalse
        try:
            int(vat)
        exceptValueError:
            returnFalse

        iflen(vat)==10:
            check_sum=2*int(vat[0])+4*int(vat[1])+10*int(vat[2])+\
                3*int(vat[3])+5*int(vat[4])+9*int(vat[5])+\
                4*int(vat[6])+6*int(vat[7])+8*int(vat[8])
            check=check_sum%11
            ifcheck%10!=int(vat[9]):
                returnFalse
        else:
            check_sum1=7*int(vat[0])+2*int(vat[1])+4*int(vat[2])+\
                10*int(vat[3])+3*int(vat[4])+5*int(vat[5])+\
                9*int(vat[6])+4*int(vat[7])+6*int(vat[8])+\
                8*int(vat[9])
            check=check_sum1%11

            ifcheck!=int(vat[10]):
                returnFalse
            check_sum2=3*int(vat[0])+7*int(vat[1])+2*int(vat[2])+\
                4*int(vat[3])+10*int(vat[4])+3*int(vat[5])+\
                5*int(vat[6])+9*int(vat[7])+4*int(vat[8])+\
                6*int(vat[9])+8*int(vat[10])
            check=check_sum2%11
            ifcheck!=int(vat[11]):
                returnFalse
        returnTrue

    #VATvalidationinTurkey,contributedby#LeventKarakas@EskaYazilimA.S.
    defcheck_vat_tr(self,vat):

        ifnot(10<=len(vat)<=11):
            returnFalse
        try:
            int(vat)
        exceptValueError:
            returnFalse

        #checkvatnumber(vergino)
        iflen(vat)==10:
            sum=0
            check=0
            forfinrange(0,9):
                c1=(int(vat[f])+(9-f))%10
                c2=(c1*(2**(9-f)))%9
                if(c1!=0)and(c2==0):
                    c2=9
                sum+=c2
            ifsum%10==0:
                check=0
            else:
                check=10-(sum%10)
            returnint(vat[9])==check

        #checkpersonalid(tckimlikno)
        iflen(vat)==11:
            c1a=0
            c1b=0
            c2=0
            forfinrange(0,9,2):
                c1a+=int(vat[f])
            forfinrange(1,9,2):
                c1b+=int(vat[f])
            c1=((7*c1a)-c1b)%10
            forfinrange(0,10):
                c2+=int(vat[f])
            c2=c2%10
            returnint(vat[9])==c1andint(vat[10])==c2

        returnFalse

    defcheck_vat_ua(self,vat):
        res=[]
        forpartnerinself:
            ifpartner.commercial_partner_id.country_id.code=='MX':
                iflen(vat)==10:
                    res.append(True)
                else:
                    res.append(False)
            elifpartner.commercial_partner_id.is_company:
                iflen(vat)==12:
                    res.append(True)
                else:
                    res.append(False)
            else:
                iflen(vat)==10orlen(vat)==9:
                    res.append(True)
                else:
                    res.append(False)
        returnall(res)

    defcheck_vat_ve(self,vat):
        #https://tin-check.com/en/venezuela/
        #https://techdocs.broadcom.com/us/en/symantec-security-software/information-security/data-loss-prevention/15-7/About-content-packs/What-s-included-in-Content-Pack-2021-02/Updated-data-identifiers-in-Content-Pack-2021-02/venezuela-national-identification-number-v115451096-d327e108002-CP2021-02.html
        #Sourceslastvisitedon2022-12-09

        #VATformat:(kind-1letter)(identifiernumber-8-digitnumber)(checkdigit-1digit)
        vat_regex=re.compile(r"""
            ([vecjpg])                         #group1-kind
            (
                (?P<optional_1>-)?                     #optional'-'(1)
                [0-9]{2}
                (?(optional_1)(?P<optional_2>[.])?)    #optional'.'(2)onlyif(1)
                [0-9]{3}
                (?(optional_2)[.])                     #mandatory'.'if(2)
                [0-9]{3}
                (?(optional_1)-)                       #mandatory'-'if(1)
            )                                  #group2-identifiernumber
            ([0-9]{1})                         #groupX-checkdigit
        """,re.VERBOSE|re.IGNORECASE)

        matches=re.fullmatch(vat_regex,vat)
        ifnotmatches:
            returnFalse

        kind,identifier_number,*_,check_digit=matches.groups()
        kind=kind.lower()
        identifier_number=identifier_number.replace("-","").replace(".","")
        check_digit=int(check_digit)

        ifkind=='v':                  #Venezuelacitizenship
            kind_digit=1
        elifkind=='e':                #Foreigner
            kind_digit=2
        elifkind=='c'orkind=='j': #Township/CommunalCouncilorLegalentity
            kind_digit=3
        elifkind=='p':                #Passport
            kind_digit=4
        else:                            #Government('g')
            kind_digit=5

        #===Checksumvalidation===
        multipliers=[3,2,7,6,5,4,3,2]
        checksum=kind_digit*4
        checksum+=sum(map(lambdan,m:int(n)*m,identifier_number,multipliers))

        checksum_digit=11-checksum%11
        ifchecksum_digit>9:
            checksum_digit=0

        returncheck_digit==checksum_digit

    defcheck_vat_xi(self,vat):
        """TemporaryNothernIrelandVATvalidationfollowingBrexit
        AsofJanuary1st2021,companiesinNorthernIrelandhavea
        newVATnumberstartingwithXI
        TODO:removewhenstdnumisupdatedto1.16insupporteddistro"""
        returnstdnum.util.get_cc_module('gb','vat').is_valid(vat)ifstdnumelseTrue

    defcheck_vat_in(self,vat):
        #referencefromhttps://www.gstzen.in/a/format-of-a-gst-number-gstin.html
        ifvatandlen(vat)==15:
            all_gstin_re=[
                r'[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[Zz1-9A-Ja-j]{1}[0-9a-zA-Z]{1}',#Normal,Composite,CasualGSTIN
                r'[0-9]{4}[A-Z]{3}[0-9]{5}[UO]{1}[N][A-Z0-9]{1}',#UN/ONBodyGSTIN
                r'[0-9]{4}[a-zA-Z]{3}[0-9]{5}[N][R][0-9a-zA-Z]{1}',#NRIGSTIN
                r'[0-9]{2}[a-zA-Z]{4}[a-zA-Z0-9]{1}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[DK]{1}[0-9a-zA-Z]{1}',#TDSGSTIN
                r'[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[C]{1}[0-9a-zA-Z]{1}'#TCSGSTIN
            ]
            returnany(re.compile(rx).match(vat)forrxinall_gstin_re)
        returnFalse

    defcheck_vat_au(self,vat):
        '''
        TheAustralianequivalentofaVATnumberisanABNnumber.
        TFN(AustraliaTaxfilenumbers)areprivateandnottobe
        enteredintosystemsorpubliclydisplayed,soABNnumbers
        arethepublicfacingnumberthatlegallymustbedisplayed
        onallinvoices
        '''
        check_func=getattr(stdnum.util.get_cc_module('au','abn'),'is_valid',None)
        ifnotcheck_func:
            vat=vat.replace("","")
            returnlen(vat)==11andvat.isdigit()
        returncheck_func(vat)

    defcheck_vat_t(self,vat):
        ifself.country_id.code=='JP':
            returnself.simple_vat_check('jp',vat)

    defformat_vat_eu(self,vat):
        #Foreigncompaniesthattradewithnon-enterprisesintheEU
        #mayhaveaVATINstartingwith"EU"insteadofacountrycode.
        returnvat

    defformat_vat_ch(self,vat):
        stdnum_vat_format=getattr(stdnum.util.get_cc_module('ch','vat'),'format',None)
        returnstdnum_vat_format('CH'+vat)[2:]ifstdnum_vat_formatelsevat

    defformat_vat_sm(self,vat):
        stdnum_vat_format=stdnum.util.get_cc_module('sm','vat').compact
        returnstdnum_vat_format('SM'+vat)[2:]

    def_fix_vat_number(self,vat,country_id):
        code=self.env['res.country'].browse(country_id).codeifcountry_idelseFalse
        vat_country,vat_number=self._split_vat(vat)
        ifcodeandcode.lower()!=vat_country:
            returnvat
        stdnum_vat_fix_func=getattr(stdnum.util.get_cc_module(vat_country,'vat'),'compact',None)
        #Ifanylocalizationmoduleneedtodefinevatfixmethodforit'scountrythenwegivefirstprioritytoit.
        format_func_name='format_vat_'+vat_country
        format_func=getattr(self,format_func_name,None)orstdnum_vat_fix_func
        ifformat_func:
            vat_number=format_func(vat_number)
        returnvat_country.upper()+vat_number

    @api.model_create_multi
    defcreate(self,vals_list):
        forvaluesinvals_list:
            ifvalues.get('vat'):
                country_id=values.get('country_id')
                values['vat']=self._fix_vat_number(values['vat'],country_id)
        returnsuper(ResPartner,self).create(vals_list)

    defwrite(self,values):
        ifvalues.get('vat')andlen(self.mapped('country_id'))==1:
            country_id=values.get('country_id',self.country_id.id)
            values['vat']=self._fix_vat_number(values['vat'],country_id)
        returnsuper(ResPartner,self).write(values)
