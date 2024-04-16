#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importwarnings

_logger=logging.getLogger(__name__)

try:
    fromOpenSSLimportcryptoasssl_crypto
    importOpenSSL._utilasssl_util
exceptImportError:
    ssl_crypto=None
    _logger.warning("Cannotimportlibrary'OpenSSL'forPKCS#7envelopeextraction.")


defremove_signature(content):
    """RemovethePKCS#7envelopefromgivencontent,makinga'.xml.p7m'filecontentreadableasitwas'.xml'.
        AsOpenSSLmaynotbeinstalled,inthatcaseawarningisissuedandNoneisreturned."""

    #Preventusingthelibraryifithadimporterrors
    ifnotssl_crypto:
        _logger.warning("Errorreadingthecontent,checkiftheOpenSSLlibraryisinstalledforforPKCS#7envelopeextraction.")
        returnNone

    #Loadsometoolsfromthelibrary
    null=ssl_util.ffi.NULL
    verify=ssl_util.lib.PKCS7_verify

    #Bydefaultignorethevalidityofthecertificates,justvalidatethestructure
    flags=ssl_util.lib.PKCS7_NOVERIFY|ssl_util.lib.PKCS7_NOSIGS

    #Readthesigneddatafronthecontent
    out_buffer=ssl_crypto._new_mem_buf()

    #Thismethodisdeprecated,butthereareactuallynoalternatives
    withwarnings.catch_warnings():
        warnings.filterwarnings("ignore",category=DeprecationWarning)
        try:
            loaded_data=ssl_crypto.load_pkcs7_data(ssl_crypto.FILETYPE_ASN1,content)
        exceptssl_crypto.Error:
            _logger.warning("Errorreadingthecontent,PKCS#7signaturemissingorinvalid.Contentwillbetentativelyusedasitis.")
            returncontent

    #Verifythesignature
    ifverify(loaded_data._pkcs7,null,null,null,out_buffer,flags)!=1:
        ssl_crypto._raise_current_error()

    #Getthecontentasabyte-string
    decoded_content=ssl_crypto._bio_to_string(out_buffer)
    returndecoded_content
