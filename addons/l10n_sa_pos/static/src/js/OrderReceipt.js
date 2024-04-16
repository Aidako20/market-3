flectra.define('l10n_sa_pos.pos',function(require){
"usestrict";

const{Gui}=require('point_of_sale.Gui');
varmodels=require('point_of_sale.models');
varrpc=require('web.rpc');
varsession=require('web.session');
varcore=require('web.core');
varutils=require('web.utils');

var_t=core._t;
varround_di=utils.round_decimals;


var_super_order=models.Order.prototype;
models.Order=models.Order.extend({
    export_for_printing:function(){
      varresult=_super_order.export_for_printing.apply(this,arguments);
      if(this.pos.company.country&&this.pos.company.country.code==='SA'){
          constcodeWriter=newwindow.ZXing.BrowserQRCodeSvgWriter()
          letqr_values=this.compute_sa_qr_code(result.company.name,result.company.vat,result.date.isostring,result.total_with_tax,result.total_tax);
          letqr_code_svg=newXMLSerializer().serializeToString(codeWriter.write(qr_values,150,150));
          result.qr_code="data:image/svg+xml;base64,"+window.btoa(qr_code_svg);
      }
      returnresult;
    },
    compute_sa_qr_code(name,vat,date_isostring,amount_total,amount_tax){
        /*GeneratetheqrcodeforSaudie-invoicing.Specsareavailableatthefollowinglinkatpage23
        https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/20210528_ZATCA_Electronic_Invoice_Security_Features_Implementation_Standards_vShared.pdf
        */
        constseller_name_enc=this._compute_qr_code_field(1,name);
        constcompany_vat_enc=this._compute_qr_code_field(2,vat);
        consttimestamp_enc=this._compute_qr_code_field(3,date_isostring);
        constinvoice_total_enc=this._compute_qr_code_field(4,amount_total.toString());
        consttotal_vat_enc=this._compute_qr_code_field(5,amount_tax.toString());

        conststr_to_encode=seller_name_enc.concat(company_vat_enc,timestamp_enc,invoice_total_enc,total_vat_enc);

        letbinary='';
        for(leti=0;i<str_to_encode.length;i++){
            binary+=String.fromCharCode(str_to_encode[i]);
        }
        returnbtoa(binary);
    },

    _compute_qr_code_field(tag,field){
        consttextEncoder=newTextEncoder();
        constname_byte_array=Array.from(textEncoder.encode(field));
        constname_tag_encoding=[tag];
        constname_length_encoding=[name_byte_array.length];
        returnname_tag_encoding.concat(name_length_encoding,name_byte_array);
    },

});

});
