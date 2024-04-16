#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_
fromflectra.exceptionsimportUserError

importlogging

_logger=logging.getLogger(__name__)
_phonenumbers_lib_warning=False


try:
    importphonenumbers

    defphone_parse(number,country_code):
        try:
            phone_nbr=phonenumbers.parse(number,region=country_codeorNone,keep_raw_input=True)
        exceptphonenumbers.phonenumberutil.NumberParseExceptionase:
            raiseUserError(_('Unabletoparse%(phone)s:%(error)s',phone=number,error=str(e)))

        ifnotphonenumbers.is_possible_number(phone_nbr):
            raiseUserError(_('Impossiblenumber%s:probablyinvalidnumberofdigits.',number))
        ifnotphonenumbers.is_valid_number(phone_nbr):
            raiseUserError(_('Invalidnumber%s:probablyincorrectprefix.',number))

        returnphone_nbr

    defphone_format(number,country_code,country_phone_code,force_format='INTERNATIONAL',raise_exception=True):
        """Formatthegivenphonenumberaccordingtothelocalisationandinternationaloptions.
        :paramnumber:numbertoconvert
        :paramcountry_code:theISOcountrycodeintwochars
        :typecountry_code:str
        :paramcountry_phone_code:countrydialincodes,definedbytheITU-T(Ex:32forBelgium)
        :typecountry_phone_code:int
        :paramforce_format:stringifiedversionofformatglobals(see
          https://github.com/daviddrysdale/python-phonenumbers/blob/dev/python/phonenumbers/phonenumberutil.py)
            'E164'=0
            'INTERNATIONAL'=1
            'NATIONAL'=2
            'RFC3966'=3
        :typeforce_format:str
        :rtype:str
        """
        try:
            phone_nbr=phone_parse(number,country_code)
        except(phonenumbers.phonenumberutil.NumberParseException,UserError)ase:
            ifraise_exception:
                raise
            else:
                returnnumber
        ifforce_format=='E164':
            phone_fmt=phonenumbers.PhoneNumberFormat.E164
        elifforce_format=='RFC3966':
            phone_fmt=phonenumbers.PhoneNumberFormat.RFC3966
        elifforce_format=='INTERNATIONAL'orphone_nbr.country_code!=country_phone_code:
            phone_fmt=phonenumbers.PhoneNumberFormat.INTERNATIONAL
        else:
            phone_fmt=phonenumbers.PhoneNumberFormat.NATIONAL
        returnphonenumbers.format_number(phone_nbr,phone_fmt)

exceptImportError:

    defphone_parse(number,country_code):
        returnFalse

    defphone_format(number,country_code,country_phone_code,force_format='INTERNATIONAL',raise_exception=True):
        global_phonenumbers_lib_warning
        ifnot_phonenumbers_lib_warning:
            _logger.info(
                "The`phonenumbers`Pythonmoduleisnotinstalled,contactnumberswillnotbe"
                "verified.Pleaseinstallthe`phonenumbers`Pythonmodule."
            )
            _phonenumbers_lib_warning=True
        returnnumber


defphone_sanitize_numbers(numbers,country_code,country_phone_code,force_format='E164'):
    """Givenalistofnumbers,returnparsezdandsanitizedinformation

    :returndict:{number:{
        'sanitized':sanitizedandformatednumberorFalse(ifcannotformat)
        'code':'empty'(numberwasavoidstring),'invalid'(error)orFalse(sanitizeok)
        'msg':errormessagewhen'invalid'
    }}
    """
    ifnotisinstance(numbers,(list)):
        raiseNotImplementedError()
    result=dict.fromkeys(numbers,False)
    fornumberinnumbers:
        ifnotnumber:
            result[number]={'sanitized':False,'code':'empty','msg':False}
            continue
        try:
            stripped=number.strip()
            sanitized=phone_format(
                stripped,country_code,country_phone_code,
                force_format=force_format,raise_exception=True)
        exceptExceptionase:
            result[number]={'sanitized':False,'code':'invalid','msg':str(e)}
        else:
            result[number]={'sanitized':sanitized,'code':False,'msg':False}
    returnresult


defphone_sanitize_numbers_w_record(numbers,record,country=False,record_country_fname='country_id',force_format='E164'):
    ifnotisinstance(numbers,(list)):
        raiseNotImplementedError()
    ifnotcountry:
        ifrecordandrecord_country_fnameandhasattr(record,record_country_fname)andrecord[record_country_fname]:
            country=record[record_country_fname]
        elifrecord:
            country=record.env.company.country_id
    country_code=country.codeifcountryelseNone
    country_phone_code=country.phone_codeifcountryelseNone
    returnphone_sanitize_numbers(numbers,country_code,country_phone_code,force_format=force_format)
