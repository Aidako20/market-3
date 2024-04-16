#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classPartner(models.Model):
    _inherit=['res.partner']

    street_name=fields.Char(
        'StreetName',compute='_compute_street_data',inverse='_inverse_street_data',store=True)
    street_number=fields.Char(
        'House',compute='_compute_street_data',inverse='_inverse_street_data',store=True)
    street_number2=fields.Char(
        'Door',compute='_compute_street_data',inverse='_inverse_street_data',store=True)

    def_inverse_street_data(self):
        """Updatesthestreetfield.
        Writesthe`street`fieldonthepartnerswhenoneofthesub-fieldsinSTREET_FIELDS
        hasbeentouched"""
        street_fields=self._get_street_fields()
        forpartnerinself:
            street_format=(partner.country_id.street_formator
                '%(street_number)s/%(street_number2)s%(street_name)s')
            previous_field=None
            previous_pos=0
            street_value=""
            separator=""
            #iteronfieldsinstreet_format,detectedas'%(<field_name>)s'
            forre_matchinre.finditer(r'%\(\w+\)s',street_format):
                #[2:-2]isusedtoremovetheextrachars'%('and')s'
                field_name=re_match.group()[2:-2]
                field_pos=re_match.start()
                iffield_namenotinstreet_fields:
                    raiseUserError(_("Unrecognizedfield%sinstreetformat.",field_name))
                ifnotprevious_field:
                    #firstiteration:addheadingcharsinstreet_format
                    ifpartner[field_name]:
                        street_value+=street_format[0:field_pos]+partner[field_name]
                else:
                    #getthesubstringbetween2fields,tobeusedasseparator
                    separator=street_format[previous_pos:field_pos]
                    ifstreet_valueandpartner[field_name]:
                        street_value+=separator
                    ifpartner[field_name]:
                        street_value+=partner[field_name]
                previous_field=field_name
                previous_pos=re_match.end()

            #addtrailingcharsinstreet_format
            street_value+=street_format[previous_pos:]
            partner.street=street_value

    @api.depends('street')
    def_compute_street_data(self):
        """Splitsstreetvalueintosub-fields.
        RecomputesthefieldsofSTREET_FIELDSwhen`street`ofapartnerisupdated"""
        street_fields=self._get_street_fields()
        forpartnerinself:
            ifnotpartner.street:
                forfieldinstreet_fields:
                    partner[field]=None
                continue

            street_format=(partner.country_id.street_formator
                '%(street_number)s/%(street_number2)s%(street_name)s')
            street_raw=partner.street
            vals=self._split_street_with_params(street_raw,street_format)
            #assignthevaluestothefields
            fork,vinvals.items():
                partner[k]=v
            forkinset(street_fields)-set(vals):
                partner[k]=None

    def_split_street_with_params(self,street_raw,street_format):
        street_fields=self._get_street_fields()
        vals={}
        previous_pos=0
        field_name=None
        #iteronfieldsinstreet_format,detectedas'%(<field_name>)s'
        forre_matchinre.finditer(r'%\(\w+\)s',street_format):
            field_pos=re_match.start()
            ifnotfield_name:
                #firstiteration:removetheheadingchars
                street_raw=street_raw[field_pos:]

            #getthesubstringbetween2fields,tobeusedasseparator
            separator=street_format[previous_pos:field_pos]
            field_value=None
            ifseparatorandfield_name:
                #maxsplitsetto1tounpackonlythefirstelementandlettherestuntouched
                tmp=street_raw.split(separator,1)
                ifprevious_greedyinvals:
                    #attachpartbeforespacetoprecedinggreedyfield
                    append_previous,sep,tmp[0]=tmp[0].rpartition('')
                    street_raw=separator.join(tmp)
                    vals[previous_greedy]+=sep+append_previous
                iflen(tmp)==2:
                    field_value,street_raw=tmp
                    vals[field_name]=field_value
            iffield_valueornotfield_name:
                previous_greedy=None
                iffield_name=='street_name'andseparator=='':
                    previous_greedy=field_name
                #selectnextfieldtofind(firstpassORfieldfound)
                #[2:-2]isusedtoremovetheextrachars'%('and')s'
                field_name=re_match.group()[2:-2]
            else:
                #valuenotfound:keeplookingforthesamefield
                pass
            iffield_namenotinstreet_fields:
                raiseUserError(_("Unrecognizedfield%sinstreetformat.",field_name))
            previous_pos=re_match.end()

        #lastfieldvalueiswhatremainsinstreet_rawminustrailingcharsinstreet_format
        trailing_chars=street_format[previous_pos:]
        iftrailing_charsandstreet_raw.endswith(trailing_chars):
            vals[field_name]=street_raw[:-len(trailing_chars)]
        else:
            vals[field_name]=street_raw
        returnvals

    defwrite(self,vals):
        res=super(Partner,self).write(vals)
        if'country_id'invalsand'street'notinvals:
            self._inverse_street_data()
        returnres

    def_formatting_address_fields(self):
        """Returnsthelistofaddressfieldsusabletoformataddresses."""
        returnsuper(Partner,self)._formatting_address_fields()+self._get_street_fields()

    def_get_street_fields(self):
        """Returnsthefieldsthatcanbeusedinastreetformat.
        Overwritethisfunctionifyouwanttoaddyourownfields."""
        return['street_name','street_number','street_number2']
