#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromcollectionsimportdefaultdict
fromurllib3.util.ssl_importcreate_urllib3_context,DEFAULT_CIPHERS
fromOpenSSL.cryptoimportload_certificate,load_privatekey,FILETYPE_PEM
fromzeep.transportsimportTransport

fromflectraimportfields
fromflectra.exceptionsimportUserError
fromflectra.toolsimporthtml_escape

importmath
importjson
importrequests
importzeep

fromflectraimportmodels,_


#CustompatchestoperformtheWSDLrequests.

EUSKADI_CIPHERS=f"{DEFAULT_CIPHERS}:!DH"


classPatchedHTTPAdapter(requests.adapters.HTTPAdapter):
    """AnadaptertoblockDHcipherswhichmaynotworkforthetaxagenciescalled"""

    definit_poolmanager(self,*args,**kwargs):
        #OVERRIDE
        kwargs['ssl_context']=create_urllib3_context(ciphers=EUSKADI_CIPHERS)
        returnsuper().init_poolmanager(*args,**kwargs)

    defcert_verify(self,conn,url,verify,cert):
        #OVERRIDE
        #Thelastparameterisonlyusedbythesupermethodtocheckifthefileexists.
        #Inourcase,certisanflectrarecord'l10n_es_edi.certificate'sonotapathtoafile.
        #Byputting'None'aslastparameter,weensurethecheckaboutTLSconfigurationis
        #stillmadewithoutcheckingtemporaryfilesexist.
        super().cert_verify(conn,url,verify,None)
        conn.cert_file=cert
        conn.key_file=None

    defget_connection(self,url,proxies=None):
        #OVERRIDE
        #PatchtheOpenSSLContexttodecodethecertificatein-memory.
        conn=super().get_connection(url,proxies=proxies)
        context=conn.conn_kw['ssl_context']

        defpatched_load_cert_chain(l10n_es_flectra_certificate,keyfile=None,password=None):
            cert_file,key_file,dummy=l10n_es_flectra_certificate.sudo()._decode_certificate()
            cert_obj=load_certificate(FILETYPE_PEM,cert_file)
            pkey_obj=load_privatekey(FILETYPE_PEM,key_file)

            context._ctx.use_certificate(cert_obj)
            context._ctx.use_privatekey(pkey_obj)

        context.load_cert_chain=patched_load_cert_chain

        returnconn


classAccountEdiFormat(models.Model):
    _inherit='account.edi.format'

    #-------------------------------------------------------------------------
    #ESEDI
    #-------------------------------------------------------------------------

    def_l10n_es_edi_get_invoices_tax_details_info(self,invoice,filter_invl_to_apply=None):

        defgrouping_key_generator(tax_values):
            tax=tax_values['tax_id']
            return{
                'applied_tax_amount':tax.amount,
                'l10n_es_type':tax.l10n_es_type,
                'l10n_es_exempt_reason':tax.l10n_es_exempt_reasoniftax.l10n_es_type=='exento'elseFalse,
                'l10n_es_bien_inversion':tax.l10n_es_bien_inversion,
            }

        deffilter_to_apply(tax_values):
            #Forintra-community,wedonottakeintoaccountthenegativerepartitionline
            returntax_values['tax_repartition_line_id'].factor_percent>0.0

        deffull_filter_invl_to_apply(invoice_line):
            if'ignore'ininvoice_line.tax_ids.flatten_taxes_hierarchy().mapped('l10n_es_type'):
                returnFalse
            returnfilter_invl_to_apply(invoice_line)iffilter_invl_to_applyelseTrue

        tax_details=invoice._prepare_edi_tax_details(
            grouping_key_generator=grouping_key_generator,
            filter_invl_to_apply=full_filter_invl_to_apply,
            filter_to_apply=filter_to_apply,
        )
        sign=-1ifinvoice.is_sale_document()else1

        tax_details_info=defaultdict(dict)

        #Detectforwhichisthemaintaxfor'recargo'.Sinceonlyasinglecombinationtax+recargoisallowed
        #onthesameinvoice,thiscanbededucedglobally.

        recargo_tax_details={}#Mappingbetweenmaintaxandrecargotaxdetails
        invoice_lines=invoice.invoice_line_ids.filtered(lambdax:notx.display_type)
        iffilter_invl_to_apply:
            invoice_lines=invoice_lines.filtered(filter_invl_to_apply)
        forlineininvoice_lines:
            taxes=line.tax_ids.flatten_taxes_hierarchy()
            recargo_tax=[tfortintaxesift.l10n_es_type=='recargo']
            ifrecargo_taxandtaxes:
                recargo_main_tax=taxes.filtered(lambdax:x.l10n_es_typein('sujeto','sujeto_isp'))[:1]
                ifnotrecargo_tax_details.get(recargo_main_tax):
                    recargo_tax_details[recargo_main_tax]=[
                        xforxintax_details['tax_details'].values()
                        ifx['group_tax_details'][0]['tax_id']==recargo_tax[0]
                    ][0]

        tax_amount_deductible=0.0
        tax_amount_retention=0.0
        base_amount_not_subject=0.0
        base_amount_not_subject_loc=0.0
        tax_subject_info_list=[]
        tax_subject_isp_info_list=[]
        fortax_valuesintax_details['tax_details'].values():

            ifinvoice.is_sale_document():
                #Customerinvoices

                iftax_values['l10n_es_type']in('sujeto','sujeto_isp'):
                    tax_amount_deductible+=tax_values['tax_amount']

                    base_amount=sign*tax_values['base_amount']
                    tax_info={
                        'TipoImpositivo':tax_values['applied_tax_amount'],
                        'BaseImponible':round(base_amount,2),
                        'CuotaRepercutida':round(math.copysign(tax_values['tax_amount'],base_amount),2),
                    }

                    recargo=recargo_tax_details.get(tax_values['group_tax_details'][0]['tax_id'])
                    ifrecargo:
                        tax_info['CuotaRecargoEquivalencia']=round(sign*recargo['tax_amount'],2)
                        tax_info['TipoRecargoEquivalencia']=recargo['applied_tax_amount']

                    iftax_values['l10n_es_type']=='sujeto':
                        tax_subject_info_list.append(tax_info)
                    else:
                        tax_subject_isp_info_list.append(tax_info)

                eliftax_values['l10n_es_type']=='exento':
                    tax_details_info['Sujeta'].setdefault('Exenta',{'DetalleExenta':[]})
                    tax_details_info['Sujeta']['Exenta']['DetalleExenta'].append({
                        'BaseImponible':round(sign*tax_values['base_amount'],2),
                        'CausaExencion':tax_values['l10n_es_exempt_reason'],
                    })
                eliftax_values['l10n_es_type']=='retencion':
                    tax_amount_retention+=tax_values['tax_amount']
                eliftax_values['l10n_es_type']=='no_sujeto':
                    base_amount_not_subject+=tax_values['base_amount']
                eliftax_values['l10n_es_type']=='no_sujeto_loc':
                    base_amount_not_subject_loc+=tax_values['base_amount']
                eliftax_values['l10n_es_type']=='ignore':
                    continue

                iftax_subject_isp_info_listandnottax_subject_info_list:
                    tax_details_info['Sujeta']['NoExenta']={'TipoNoExenta':'S2'}
                elifnottax_subject_isp_info_listandtax_subject_info_list:
                    tax_details_info['Sujeta']['NoExenta']={'TipoNoExenta':'S1'}
                eliftax_subject_isp_info_listandtax_subject_info_list:
                    tax_details_info['Sujeta']['NoExenta']={'TipoNoExenta':'S3'}

                iftax_subject_info_list:
                    tax_details_info['Sujeta']['NoExenta'].setdefault('DesgloseIVA',{})
                    tax_details_info['Sujeta']['NoExenta']['DesgloseIVA'].setdefault('DetalleIVA',[])
                    tax_details_info['Sujeta']['NoExenta']['DesgloseIVA']['DetalleIVA']+=tax_subject_info_list
                iftax_subject_isp_info_list:
                    tax_details_info['Sujeta']['NoExenta'].setdefault('DesgloseIVA',{})
                    tax_details_info['Sujeta']['NoExenta']['DesgloseIVA'].setdefault('DetalleIVA',[])
                    tax_details_info['Sujeta']['NoExenta']['DesgloseIVA']['DetalleIVA']+=tax_subject_isp_info_list

            else:
                #Vendorbills
                iftax_values['l10n_es_type']in('sujeto','sujeto_isp','no_sujeto','no_sujeto_loc'):
                    tax_amount_deductible+=tax_values['tax_amount']
                eliftax_values['l10n_es_type']=='retencion':
                    tax_amount_retention+=tax_values['tax_amount']
                eliftax_values['l10n_es_type']=='no_sujeto':
                    base_amount_not_subject+=tax_values['base_amount']
                eliftax_values['l10n_es_type']=='no_sujeto_loc':
                    base_amount_not_subject_loc+=tax_values['base_amount']
                eliftax_values['l10n_es_type']=='ignore':
                    continue

                iftax_values['l10n_es_type']notin['retencion','recargo']:#=insujeto/sujeto_isp/no_deducible
                    base_amount=sign*tax_values['base_amount']
                    tax_details_info.setdefault('DetalleIVA',[])
                    tax_info={
                        'BaseImponible':round(base_amount,2),
                    }
                    iftax_values['applied_tax_amount']>0.0:
                        tax_info.update({
                            'TipoImpositivo':tax_values['applied_tax_amount'],
                            'CuotaSoportada':round(math.copysign(tax_values['tax_amount'],base_amount),2),
                        })
                    iftax_values['l10n_es_bien_inversion']:
                        tax_info['BienInversion']='S'
                    recargo=recargo_tax_details.get(tax_values['group_tax_details'][0]['tax_id'])
                    ifrecargo:
                        tax_info['CuotaRecargoEquivalencia']=round(sign*recargo['tax_amount'],2)
                        tax_info['TipoRecargoEquivalencia']=recargo['applied_tax_amount']
                    tax_details_info['DetalleIVA'].append(tax_info)

        ifnotinvoice.company_id.currency_id.is_zero(base_amount_not_subject)andinvoice.is_sale_document():
            tax_details_info['NoSujeta']['ImportePorArticulos7_14_Otros']=round(sign*base_amount_not_subject,2)
        ifnotinvoice.company_id.currency_id.is_zero(base_amount_not_subject_loc)andinvoice.is_sale_document():
            tax_details_info['NoSujeta']['ImporteTAIReglasLocalizacion']=round(sign*base_amount_not_subject_loc,2)

        return{
            'tax_details_info':tax_details_info,
            'tax_details':tax_details,
            'tax_amount_deductible':tax_amount_deductible,
            'tax_amount_retention':tax_amount_retention,
            'base_amount_not_subject':base_amount_not_subject,
        }

    def_l10n_es_edi_get_partner_info(self,partner):
        eu_country_codes=set(self.env.ref('base.europe').country_ids.mapped('code'))

        partner_info={}
        IDOtro_ID=partner.vator'NO_DISPONIBLE'

        if(notpartner.country_idorpartner.country_id.code=='ES')andpartner.vat:
            #ESpartnerwithVAT.
            partner_info['NIF']=partner.vat[2:]ifpartner.vat.startswith('ES')elsepartner.vat
            ifself.env.context.get('error_1117'):
                partner_info['IDOtro']={'IDType':'07','ID':IDOtro_ID}

        elifpartner.country_id.codeineu_country_codesandpartner.vat:
            #Europeanpartner.
            partner_info['IDOtro']={'IDType':'02','ID':IDOtro_ID}
        else:
            partner_info['IDOtro']={'ID':IDOtro_ID}
            ifpartner.vat:
                partner_info['IDOtro']['IDType']='04'
            else:
                partner_info['IDOtro']['IDType']='06'
            ifpartner.country_id:
                partner_info['IDOtro']['CodigoPais']=partner.country_id.code
        returnpartner_info

    def_l10n_es_edi_get_invoices_info(self,invoices):
        eu_country_codes=set(self.env.ref('base.europe').country_ids.mapped('code'))

        simplified_partner=self.env.ref("l10n_es_edi_sii.partner_simplified")

        info_list=[]
        forinvoiceininvoices:
            com_partner=invoice.commercial_partner_id
            is_simplified=invoice.partner_id==simplified_partner

            info={
                'PeriodoLiquidacion':{
                    'Ejercicio':str(invoice.date.year),
                    'Periodo':str(invoice.date.month).zfill(2),
                },
                'IDFactura':{
                    'FechaExpedicionFacturaEmisor':invoice.invoice_date.strftime('%d-%m-%Y'),
                },
            }

            ifinvoice.is_sale_document():
                invoice_node=info['FacturaExpedida']={}
            else:
                invoice_node=info['FacturaRecibida']={}

            #===Partner===

            partner_info=self._l10n_es_edi_get_partner_info(com_partner)

            #===Invoice===

            invoice_node['DescripcionOperacion']=invoice.invoice_origin[:500]ifinvoice.invoice_originelse'manual'
            ifinvoice.is_sale_document():
                info['IDFactura']['IDEmisorFactura']={'NIF':invoice.company_id.vat[2:]}
                info['IDFactura']['NumSerieFacturaEmisor']=invoice.name[:60]
                ifnotis_simplified:
                    invoice_node['Contraparte']={
                        **partner_info,
                        'NombreRazon':com_partner.name[:120],
                    }

                ifnotcom_partner.country_idorcom_partner.country_id.codeineu_country_codes:
                    invoice_node['ClaveRegimenEspecialOTrascendencia']='01'
                else:
                    invoice_node['ClaveRegimenEspecialOTrascendencia']='02'
            else:
                info['IDFactura']['IDEmisorFactura']=partner_info
                info['IDFactura']['NumSerieFacturaEmisor']=invoice.ref[:60]
                ifnotis_simplified:
                    invoice_node['Contraparte']={
                        **partner_info,
                        'NombreRazon':com_partner.name[:120],
                    }

                ifinvoice.l10n_es_registration_date:
                    invoice_node['FechaRegContable']=invoice.l10n_es_registration_date.strftime('%d-%m-%Y')
                else:
                    invoice_node['FechaRegContable']=fields.Date.context_today(self).strftime('%d-%m-%Y')

                country_code=com_partner.country_id.code
                ifnotcountry_codeorcountry_code=='ES'orcountry_codenotineu_country_codes:
                    invoice_node['ClaveRegimenEspecialOTrascendencia']='01'
                else:
                    invoice_node['ClaveRegimenEspecialOTrascendencia']='09'#ForIntra-Com

            ifinvoice.move_type=='out_invoice':
                invoice_node['TipoFactura']='F2'ifis_simplifiedelse'F1'
            elifinvoice.move_type=='out_refund':
                invoice_node['TipoFactura']='R5'ifis_simplifiedelse'R1'
                invoice_node['TipoRectificativa']='I'
            elifinvoice.move_type=='in_invoice':
                invoice_node['TipoFactura']='F1'
            elifinvoice.move_type=='in_refund':
                invoice_node['TipoFactura']='R4'
                invoice_node['TipoRectificativa']='I'

            #===Taxes===

            sign=-1ifinvoice.is_sale_document()else1

            ifinvoice.is_sale_document():
                #Customerinvoices

                ifcom_partner.country_id.codein('ES',False)andnot(com_partner.vator'').startswith("ESN"):
                    tax_details_info_vals=self._l10n_es_edi_get_invoices_tax_details_info(invoice)
                    invoice_node['TipoDesglose']={'DesgloseFactura':tax_details_info_vals['tax_details_info']}

                    invoice_node['ImporteTotal']=round(sign*(
                        tax_details_info_vals['tax_details']['base_amount']
                        +tax_details_info_vals['tax_details']['tax_amount']
                        -tax_details_info_vals['tax_amount_retention']
                    ),2)
                else:
                    tax_details_info_service_vals=self._l10n_es_edi_get_invoices_tax_details_info(
                        invoice,
                        filter_invl_to_apply=lambdax:any(t.tax_scope=='service'fortinx.tax_ids)
                    )
                    tax_details_info_consu_vals=self._l10n_es_edi_get_invoices_tax_details_info(
                        invoice,
                        filter_invl_to_apply=lambdax:any(t.tax_scope=='consu'fortinx.tax_ids)
                    )

                    iftax_details_info_service_vals['tax_details_info']:
                        invoice_node.setdefault('TipoDesglose',{})
                        invoice_node['TipoDesglose'].setdefault('DesgloseTipoOperacion',{})
                        invoice_node['TipoDesglose']['DesgloseTipoOperacion']['PrestacionServicios']=tax_details_info_service_vals['tax_details_info']
                    iftax_details_info_consu_vals['tax_details_info']:
                        invoice_node.setdefault('TipoDesglose',{})
                        invoice_node['TipoDesglose'].setdefault('DesgloseTipoOperacion',{})
                        invoice_node['TipoDesglose']['DesgloseTipoOperacion']['Entrega']=tax_details_info_consu_vals['tax_details_info']
                    ifnotinvoice_node.get('TipoDesglose'):
                        raiseUserError(_(
                            "Incaseofaforeigncustomer,youneedtoconfigurethetaxscopeontaxes:\n%s",
                            "\n".join(invoice.line_ids.tax_ids.mapped('name'))
                        ))

                    invoice_node['ImporteTotal']=round(sign*(
                        tax_details_info_service_vals['tax_details']['base_amount']
                        +tax_details_info_service_vals['tax_details']['tax_amount']
                        -tax_details_info_service_vals['tax_amount_retention']
                        +tax_details_info_consu_vals['tax_details']['base_amount']
                        +tax_details_info_consu_vals['tax_details']['tax_amount']
                        -tax_details_info_consu_vals['tax_amount_retention']
                    ),2)

            else:
                #Vendorbills

                tax_details_info_isp_vals=self._l10n_es_edi_get_invoices_tax_details_info(
                    invoice,
                    filter_invl_to_apply=lambdax:any(tfortinx.tax_idsift.l10n_es_type=='sujeto_isp'),
                )
                tax_details_info_other_vals=self._l10n_es_edi_get_invoices_tax_details_info(
                    invoice,
                    filter_invl_to_apply=lambdax:notany(tfortinx.tax_idsift.l10n_es_type=='sujeto_isp'),
                )

                invoice_node['DesgloseFactura']={}
                iftax_details_info_isp_vals['tax_details_info']:
                    invoice_node['DesgloseFactura']['InversionSujetoPasivo']=tax_details_info_isp_vals['tax_details_info']
                iftax_details_info_other_vals['tax_details_info']:
                    invoice_node['DesgloseFactura']['DesgloseIVA']=tax_details_info_other_vals['tax_details_info']

                invoice_node['ImporteTotal']=round(sign*(
                    tax_details_info_isp_vals['tax_details']['base_amount']
                    +tax_details_info_isp_vals['tax_details']['tax_amount']
                    -tax_details_info_isp_vals['tax_amount_retention']
                    +tax_details_info_other_vals['tax_details']['base_amount']
                    +tax_details_info_other_vals['tax_details']['tax_amount']
                    -tax_details_info_other_vals['tax_amount_retention']
                ),2)

                invoice_node['CuotaDeducible']=round(sign*(
                    tax_details_info_isp_vals['tax_amount_deductible']
                    +tax_details_info_other_vals['tax_amount_deductible']
                ),2)

            info_list.append(info)
        returninfo_list

    def_l10n_es_edi_web_service_aeat_vals(self,invoices):
        ifinvoices[0].is_sale_document():
            return{
                'url':'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii_1_1/fact/ws/SuministroFactEmitidas.wsdl',
                'test_url':'https://prewww1.aeat.es/wlpl/SSII-FACT/ws/fe/SiiFactFEV1SOAP',
            }
        else:
            return{
                'url':'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii_1_1/fact/ws/SuministroFactRecibidas.wsdl',
                'test_url':'https://prewww1.aeat.es/wlpl/SSII-FACT/ws/fr/SiiFactFRV1SOAP',
            }

    def_l10n_es_edi_web_service_bizkaia_vals(self,invoices):
        ifinvoices[0].is_sale_document():
            return{
                'url':'https://www.bizkaia.eus/ogasuna/sii/documentos/SuministroFactEmitidas.wsdl',
                'test_url':'https://pruapps.bizkaia.eus/SSII-FACT/ws/fe/SiiFactFEV1SOAP',
            }
        else:
            return{
                'url':'https://www.bizkaia.eus/ogasuna/sii/documentos/SuministroFactRecibidas.wsdl',
                'test_url':'https://pruapps.bizkaia.eus/SSII-FACT/ws/fr/SiiFactFRV1SOAP',
            }

    def_l10n_es_edi_web_service_gipuzkoa_vals(self,invoices):
        ifinvoices[0].is_sale_document():
            return{
                'url':'https://egoitza.gipuzkoa.eus/ogasuna/sii/ficheros/v1.1/SuministroFactEmitidas.wsdl',
                'test_url':'https://sii-prep.egoitza.gipuzkoa.eus/JBS/HACI/SSII-FACT/ws/fe/SiiFactFEV1SOAP',
            }
        else:
            return{
                'url':'https://egoitza.gipuzkoa.eus/ogasuna/sii/ficheros/v1.1/SuministroFactRecibidas.wsdl',
                'test_url':'https://sii-prep.egoitza.gipuzkoa.eus/JBS/HACI/SSII-FACT/ws/fr/SiiFactFRV1SOAP',
            }

    def_l10n_es_edi_call_web_service_sign(self,invoices,info_list):
        company=invoices.company_id

        #Allaresharingthesamevalue,see'_get_batch_key'.
        csv_number=invoices.mapped('l10n_es_edi_csv')[0]

        #Setregistrationdate
        invoices.filtered(lambdainv:notinv.l10n_es_registration_date).write({
            'l10n_es_registration_date':fields.Date.context_today(self),
        })

        #===Callthewebservice===

        #Getconnectiondata.
        l10n_es_edi_tax_agency=company.mapped('l10n_es_edi_tax_agency')[0]
        connection_vals=getattr(self,f'_l10n_es_edi_web_service_{l10n_es_edi_tax_agency}_vals')(invoices)

        header={
            'IDVersionSii':'1.1',
            'Titular':{
                'NombreRazon':company.name[:120],
                'NIF':company.vat[2:],
            },
            'TipoComunicacion':'A1'ifcsv_numberelse'A0',
        }

        session=requests.Session()
        session.cert=company.l10n_es_edi_certificate_id
        session.mount('https://',PatchedHTTPAdapter())

        transport=Transport(operation_timeout=60,timeout=60,session=session)
        client=zeep.Client(connection_vals['url'],transport=transport)

        ifinvoices[0].is_sale_document():
            service_name='SuministroFactEmitidas'
        else:
            service_name='SuministroFactRecibidas'
        ifcompany.l10n_es_edi_test_envandnotconnection_vals.get('test_url'):
            service_name+='Pruebas'

        #Establishtheconnection.
        serv=client.bind('siiService',service_name)
        ifcompany.l10n_es_edi_test_envandconnection_vals.get('test_url'):
            serv._binding_options['address']=connection_vals['test_url']

        msg=''
        try:
            ifinvoices[0].is_sale_document():
                res=serv.SuministroLRFacturasEmitidas(header,info_list)
            else:
                res=serv.SuministroLRFacturasRecibidas(header,info_list)
        exceptrequests.exceptions.SSLErroraserror:
            msg=_("TheSSLcertificatecouldnotbevalidated.")
        exceptzeep.exceptions.Erroraserror:
            msg=_("Networkingerror:\n%s")%error
        exceptExceptionaserror:
            msg=str(error)
        finally:
            ifmsg:
                return{inv:{
                    'error':msg,
                    'blocking_level':'warning',
                }forinvininvoices}

        #Processresponse.

        ifnotresornotres.RespuestaLinea:
            return{inv:{
                'error':_("Thewebserviceisnotresponding"),
                'blocking_level':'warning',
            }forinvininvoices}

        resp_state=res["EstadoEnvio"]
        l10n_es_edi_csv=res['CSV']

        ifresp_state=='Correcto':
            invoices.write({'l10n_es_edi_csv':l10n_es_edi_csv})
            return{inv:{'success':True}forinvininvoices}

        results={}
        forresplinres.RespuestaLinea:
            invoice_number=respl.IDFactura.NumSerieFacturaEmisor

            #Retrievethecorrespondinginvoice.
            #Note:refcanbethesamefordifferentpartnersbutthereisnoenoughinformationontheresponse
            #tomatchthepartner.

            #Note:Invoicesarebatchedpermove_type.
            ifinvoices[0].is_sale_document():
                inv=invoices.filtered(lambdax:x.name[:60]==invoice_number)
            else:
                #'ref'canbethesamefordifferentpartners.
                candidates=invoices.filtered(lambdax:x.ref[:60]==invoice_number)
                iflen(candidates)>=1:
                    respl_partner_info=respl.IDFactura.IDEmisorFactura
                    inv=None
                    forcandidateincandidates:
                        partner_info=self._l10n_es_edi_get_partner_info(candidate.commercial_partner_id)
                        ifpartner_info.get('NIF')andpartner_info['NIF']==respl_partner_info.NIF:
                            inv=candidate
                            break
                        ifpartner_info.get('IDOtro')andall(getattr(respl_partner_info.IDOtro,k)==v
                                                           fork,vinpartner_info['IDOtro'].items()):
                            inv=candidate
                            break

                    ifnotinv:
                        #Thiscaseshouldn'thappenandmeansthereissomethingwronginthiscode.However,wecan't
                        #raiseanythingsincethedocumenthasalreadybeenapprovedbythegovernment.Theresult
                        #willonlybeabadlyloggedmessageintothechatterso,notabigdeal.
                        inv=candidates[0]
                else:
                    inv=candidates

            resp_line_state=respl.EstadoRegistro
            ifresp_line_statein('Correcto','AceptadoConErrores'):
                inv.l10n_es_edi_csv=l10n_es_edi_csv
                results[inv]={'success':True}
                ifresp_line_state=='AceptadoConErrores':
                    inv.message_post(body=_("Thiswasacceptedwitherrors:")+html_escape(respl.DescripcionErrorRegistro))
            elifrespl.RegistroDuplicado:
                results[inv]={'success':True}
                inv.message_post(body=_("Wesawthatthisinvoicewassentcorrectlybefore,butwedidnottreat"
                                        "theresponse. Makesureitisnotbecauseofawrongconfiguration."))
            elifrespl.CodigoErrorRegistro==1117andnotself.env.context.get('error_1117'):
                returnself.with_context(error_1117=True)._post_invoice_edi(invoices)
            else:
                results[inv]={
                    'error':_("[%s]%s",respl.CodigoErrorRegistro,respl.DescripcionErrorRegistro),
                    'blocking_level':'error',
                }

        returnresults

    #-------------------------------------------------------------------------
    #EDIOVERRIDDENMETHODS
    #-------------------------------------------------------------------------

    def_get_invoice_edi_content(self,move):
        ifself.code!='es_sii':
            returnsuper()._get_invoice_edi_content(move)
        returnjson.dumps(self._l10n_es_edi_get_invoices_info(move)).encode()

    def_is_required_for_invoice(self,invoice):
        #OVERRIDE
        ifself.code!='es_sii':
            returnsuper()._is_required_for_invoice(invoice)

        returninvoice.l10n_es_edi_is_required

    def_needs_web_services(self):
        #OVERRIDE
        returnself.code=='es_sii'orsuper()._needs_web_services()

    def_support_batching(self,move=None,state=None,company=None):
        #OVERRIDE
        ifself.code!='es_sii':
            returnsuper()._support_batching(move=move,state=state,company=company)

        returnstate=='to_send'andmove.is_invoice()

    def_get_batch_key(self,move,state):
        #OVERRIDE
        ifself.code!='es_sii':
            returnsuper()._get_batch_key(move,state)

        returnmove.move_type,move.l10n_es_edi_csv

    def_check_move_configuration(self,move):
        #OVERRIDE
        res=super()._check_move_configuration(move)
        ifself.code!='es_sii':
            returnres

        ifnotmove.company_id.vat:
            res.append(_("VATnumberismissingoncompany%s",move.company_id.display_name))
        forlineinmove.invoice_line_ids.filtered(lambdaline:notline.display_type):
            taxes=line.tax_ids.flatten_taxes_hierarchy()
            recargo_count=taxes.mapped('l10n_es_type').count('recargo')
            retention_count=taxes.mapped('l10n_es_type').count('retencion')
            sujeto_count=taxes.mapped('l10n_es_type').count('sujeto')
            no_sujeto_count=taxes.mapped('l10n_es_type').count('no_sujeto')
            no_sujeto_loc_count=taxes.mapped('l10n_es_type').count('no_sujeto_loc')
            ifretention_count>1:
                res.append(_("Line%sshouldonlyhaveoneretentiontax.",line.display_name))
            ifrecargo_count>1:
                res.append(_("Line%sshouldonlyhaveonerecargotax.",line.display_name))
            ifsujeto_count>1:
                res.append(_("Line%sshouldonlyhaveonesujetotax.",line.display_name))
            ifno_sujeto_count>1:
                res.append(_("Line%sshouldonlyhaveonenosujetotax.",line.display_name))
            ifno_sujeto_loc_count>1:
                res.append(_("Line%sshouldonlyhaveonenosujeto(localizations)tax.",line.display_name))
            ifsujeto_count+no_sujeto_loc_count+no_sujeto_count>1:
                res.append(_("Line%sshouldonlyhaveonemaintax.",line.display_name))
        ifmove.move_typein('in_invoice','in_refund'):
            ifnotmove.ref:
                res.append(_("Youshouldputavendorreferenceonthisvendorbill."))
        returnres

    def_is_compatible_with_journal(self,journal):
        #OVERRIDE
        ifself.code!='es_sii':
            returnsuper()._is_compatible_with_journal(journal)

        returnjournal.country_code=='ES'

    def_post_invoice_edi(self,invoices,test_mode=False):
        #OVERRIDE
        ifself.code!='es_sii':
            returnsuper()._post_invoice_edi(invoices,test_mode=test_mode)

        #Ensureacertificateisavailable.
        certificate=invoices.company_id.l10n_es_edi_certificate_id
        ifnotcertificate:
            return{inv:{
                'error':_("PleaseconfigurethecertificateforSII."),
                'blocking_level':'error',
            }forinvininvoices}

        #Ensureataxagencyisavailable.
        l10n_es_edi_tax_agency=invoices.company_id.mapped('l10n_es_edi_tax_agency')[0]
        ifnotl10n_es_edi_tax_agency:
            return{inv:{
                'error':_("PleasespecifyataxagencyonyourcompanyforSII."),
                'blocking_level':'error',
            }forinvininvoices}

        #GeneratetheJSON.
        info_list=self._l10n_es_edi_get_invoices_info(invoices)

        #Callthewebservice.
        iftest_mode:
            res={inv:{'success':True}forinvininvoices}
        else:
            res=self._l10n_es_edi_call_web_service_sign(invoices,info_list)

        forinvininvoices:
            ifres.get(inv,{}).get('success'):
                attachment=self.env['ir.attachment'].create({
                    'type':'binary',
                    'name':'jsondump.json',
                    'raw':json.dumps(info_list),
                    'mimetype':'application/json',
                    'res_model':inv._name,
                    'res_id':inv.id,
                })
                res[inv]['attachment']=attachment
        returnres
