#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

frombase64importb64decode
frompytzimporttimezone
fromdatetimeimportdatetime
fromcryptography.hazmat.backendsimportdefault_backend
fromcryptography.hazmat.primitives.serializationimportEncoding,NoEncryption,PrivateFormat,pkcs12


fromflectraimport_,api,fields,models,tools
fromflectra.exceptionsimportValidationError


classCertificate(models.Model):
    _name='l10n_es_edi.certificate'
    _description='PersonalDigitalCertificate'
    _order='date_startdesc,iddesc'
    _rec_name='date_start'

    content=fields.Binary(string="File",required=True,help="PFXCertificate")
    password=fields.Char(help="PassphraseforthePFXcertificate",groups="base.group_system")
    date_start=fields.Datetime(readonly=True,help="Thedateonwhichthecertificatestartstobevalid")
    date_end=fields.Datetime(readonly=True,help="Thedateonwhichthecertificateexpires")
    company_id=fields.Many2one(comodel_name='res.company',required=True,default=lambdaself:self.env.company)

    #-------------------------------------------------------------------------
    #HELPERS
    #-------------------------------------------------------------------------

    @api.model
    def_get_es_current_datetime(self):
        """GetthecurrentdatetimewiththePeruviantimezone."""
        returndatetime.now(timezone('Europe/Madrid'))

    @tools.ormcache('self.content','self.password')
    def_decode_certificate(self):
        """Returnthecontent(DERencoded)andthecertificatedecryptedbasedinthepoint3.1fromtheRS097-2012
        http://www.vauxoo.com/r/manualdeautorizacion#page=21
        """
        self.ensure_one()

        ifnotself.password:
            returnNone,None,None

        private_key,certificate,dummy=pkcs12.load_key_and_certificates(
            b64decode(self.content),
            self.password.encode(),
            backend=default_backend(),
        )

        pem_certificate=certificate.public_bytes(Encoding.PEM)
        pem_private_key=private_key.private_bytes(
            Encoding.PEM,
            format=PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=NoEncryption(),
        )
        returnpem_certificate,pem_private_key,certificate

    #-------------------------------------------------------------------------
    #LOW-LEVELMETHODS
    #-------------------------------------------------------------------------

    @api.model
    defcreate(self,vals):
        record=super().create(vals)

        spain_tz=timezone('Europe/Madrid')
        spain_dt=self._get_es_current_datetime()
        try:
            pem_certificate,pem_private_key,certificate=record._decode_certificate()
            cert_date_start=spain_tz.localize(certificate.not_valid_before)
            cert_date_end=spain_tz.localize(certificate.not_valid_after)
        exceptException:
            raiseValidationError(_(
                "Therehasbeenaproblemwiththecertificate,someusualproblemscanbe:\n"
                "-Thepasswordgivenorthecertificatearenotvalid.\n"
                "-Thecertificatecontentisinvalid."
            ))
        #Assignextractedvaluesfromthecertificate
        record.write({
            'date_start':fields.Datetime.to_string(cert_date_start),
            'date_end':fields.Datetime.to_string(cert_date_end),
        })
        ifspain_dt>cert_date_end:
            raiseValidationError(_("Thecertificateisexpiredsince%s",record.date_end))
        returnrecord
