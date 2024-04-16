flectra.define('barcodes.BarcodeParser',function(require){
"usestrict";

varClass=require('web.Class');
varrpc=require('web.rpc');

//TheBarcodeParserisusedtodetectwhatisthecategory
//ofabarcode(product,partner,...)andextractanencodedvalue
//(likeweight,price,etc.)
varBarcodeParser=Class.extend({
    init:function(attributes){
        this.nomenclature_id=attributes.nomenclature_id;
        this.loaded=this.load();
    },

    //Thisloadsthebarcodenomenclatureandbarcoderuleswhichare
    //necessarytoparsethebarcodes.TheBarcodeParserisoperational
    //onlywhenthosedatahavebeenloaded
    load:function(){
        varself=this;
        if(!this.nomenclature_id){
            return;
        }
        varid=this.nomenclature_id[0];
        returnrpc.query({
                model:'barcode.nomenclature',
                method:'read',
                args:[[id],['name','rule_ids','upc_ean_conv']],
            })
            .then(function(nomenclatures){
                self.nomenclature=nomenclatures[0];

                varargs=[
                    [['barcode_nomenclature_id','=',self.nomenclature.id]],
                    ['name','sequence','type','encoding','pattern','alias'],
                ];
                returnrpc.query({
                    model:'barcode.rule',
                    method:'search_read',
                    args:args,
                });
            }).then(function(rules){
                rules=rules.sort(function(a,b){returna.sequence-b.sequence;});
                self.nomenclature.rules=rules;
            });
    },

    //resolveswhenthebarcodeparserisoperational.
    is_loaded:function(){
        returnthis.loaded;
    },

    //returnsthechecksumoftheean13,or-1iftheeanhasnotthecorrectlength,eanmustbeastring
    ean_checksum:function(ean){
        varcode=ean.split('');
        if(code.length!==13){
            return-1;
        }
        varoddsum=0,evensum=0,total=0;
        code=code.reverse().splice(1);
        for(vari=0;i<code.length;i++){
            if(i%2===0){
                oddsum+=Number(code[i]);
            }else{
                evensum+=Number(code[i]);
            }
        }
        total=oddsum*3+evensum;
        returnNumber((10-total%10)%10);
    },

    //returnsthechecksumoftheean8,or-1iftheeanhasnotthecorrectlength,eanmustbeastring
    ean8_checksum:function(ean){
        varcode=ean.split('');
        if(code.length!==8){
            return-1;
        }
        varsum1 =Number(code[1])+Number(code[3])+Number(code[5]);
        varsum2 =Number(code[0])+Number(code[2])+Number(code[4])+Number(code[6]);
        vartotal=sum1+3*sum2;
        returnNumber((10-total%10)%10);
    },


    //returnstrueiftheeanisavalidEANbarcodenumberbycheckingthecontroldigit.
    //eanmustbeastring
    check_ean:function(ean){
        return/^\d+$/.test(ean)&&this.ean_checksum(ean)===Number(ean[ean.length-1]);
    },

    //returnstrueifthebarcodestringisencodedwiththeprovidedencoding.
    check_encoding:function(barcode,encoding){
        varlen   =barcode.length;
        varallnum=/^\d+$/.test(barcode);
        varcheck =Number(barcode[len-1]);

        if(encoding==='ean13'){
            returnlen===13&&allnum&&this.ean_checksum(barcode)===check;
        }elseif(encoding==='ean8'){
            returnlen===8 &&allnum&&this.ean8_checksum(barcode)===check;
        }elseif(encoding==='upca'){
            returnlen===12&&allnum&&this.ean_checksum('0'+barcode)===check;
        }elseif(encoding==='any'){
            returntrue;
        }else{
            returnfalse;
        }
    },

    //returnsavalidzeropaddedean13fromaneanprefix.theeanprefixmustbeastring.
    sanitize_ean:function(ean){
        ean=ean.substr(0,13);

        for(varn=0,count=(13-ean.length);n<count;n++){
            ean='0'+ean;
        }
        returnean.substr(0,12)+this.ean_checksum(ean);
    },

    //ReturnsavalidzeropaddedUPC-AfromaUPC-Aprefix.theUPC-Aprefixmustbeastring.
    sanitize_upc:function(upc){
        returnthis.sanitize_ean('0'+upc).substr(1,12);
    },

    //Checksifbarcodematchesthepattern
    //Additionnalyretrievestheoptionalnumericalcontentinbarcode
    //Returnsanobjectcontaining:
    //-value:thenumericalvalueencodedinthebarcode(0ifnovalueencoded)
    //-base_code:thebarcodeinwhichnumericalcontentisreplacedby0's
    //-match:boolean
    match_pattern:function(barcode,pattern,encoding){
        varmatch={
            value:0,
            base_code:barcode,
            match:false,
        };
        barcode=barcode.replace("\\","\\\\").replace("{",'\{').replace("}","\}").replace(".","\.");

        varnumerical_content=pattern.match(/[{][N]*[D]*[}]/);//lookfornumericalcontentinpattern
        varbase_pattern=pattern;
        if(numerical_content){//thepatternencodesanumericalcontent
            varnum_start=numerical_content.index;//startindexofnumericalcontent
            varnum_length=numerical_content[0].length;//lengthofnumericalcontent
            varvalue_string=barcode.substr(num_start,num_length-2);//numericalcontentinbarcode
            varwhole_part_match=numerical_content[0].match("[{][N]*[D}]");//looksforwholepartofnumericalcontent
            vardecimal_part_match=numerical_content[0].match("[{N][D]*[}]");//looksfordecimalpart
            varwhole_part=value_string.substr(0,whole_part_match.index+whole_part_match[0].length-2);//retrievewholepartofnumericalcontentinbarcode
            vardecimal_part="0."+value_string.substr(decimal_part_match.index,decimal_part_match[0].length-1);//retrievedecimalpart
            if(whole_part===''){
                whole_part='0';
            }
            match['value']=parseInt(whole_part)+parseFloat(decimal_part);

            //replacenumericalcontentby0'sinbarcodeandpattern
            match['base_code']=barcode.substr(0,num_start);
            varbase_pattern=pattern.substr(0,num_start);
            for(vari=0;i<(num_length-2);i++){
                match['base_code']+="0";
                base_pattern+="0";
            }
            match['base_code']+=barcode.substr(num_start+num_length-2,barcode.length-1);
            base_pattern+=pattern.substr(num_start+num_length,pattern.length-1);

            match['base_code']=match['base_code']
                .replace("\\\\","\\")
                .replace("\{","{")
                .replace("\}","}")
                .replace("\.",".");

            varbase_code=match.base_code.split('')
            if(encoding==='ean13'){
                base_code[12]=''+this.ean_checksum(match.base_code);
            }elseif(encoding==='ean8'){
                base_code[7] =''+this.ean8_checksum(match.base_code);
            }elseif(encoding==='upca'){
                base_code[11]=''+this.ean_checksum('0'+match.base_code);
            }
            match.base_code=base_code.join('')
        }

        base_pattern=base_pattern.split('|')
            .map(part=>part.startsWith('^')?part:'^'+part)
            .join('|');
        match.match=match.base_code.match(base_pattern);

        returnmatch;
    },

    //attemptstointerpretabarcode(stringencodingabarcodeCode-128)
    //itwillreturnanobjectcontainingvariousinformationaboutthebarcode.
    //mostimportantly:
    //-code   :thebarcode
    //-type  :thetypeofthebarcode(e.g.alias,unitproduct,weightedproduct...)
    //
    //-value :ifthebarcodeencodesanumericalvalue,itwillbeputthere
    //-base_code:thebarcodewithalltheencodingpartssettozero;theoneputon
    //              theproductinthebackend
    parse_barcode:function(barcode){
        varparsed_result={
            encoding:'',
            type:'error',
            code:barcode,
            base_code:barcode,
            value:0,
        };

        if(!this.nomenclature){
            returnparsed_result;
        }

        varrules=this.nomenclature.rules;
        for(vari=0;i<rules.length;i++){
            varrule=rules[i];
            varcur_barcode=barcode;

            if(   rule.encoding==='ean13'&&
                    this.check_encoding(barcode,'upca')&&
                    this.nomenclature.upc_ean_convin{'upc2ean':'','always':''}){
                cur_barcode='0'+cur_barcode;
            }elseif(rule.encoding==='upca'&&
                    this.check_encoding(barcode,'ean13')&&
                    barcode[0]==='0'&&
                    this.upc_ean_convin{'ean2upc':'','always':''}){
                cur_barcode=cur_barcode.substr(1,12);
            }

            if(!this.check_encoding(cur_barcode,rule.encoding)){
                continue;
            }

            varmatch=this.match_pattern(cur_barcode,rules[i].pattern,rule.encoding);
            if(match.match){
                if(rules[i].type==='alias'){
                    barcode=rules[i].alias;
                    parsed_result.code=barcode;
                    parsed_result.type='alias';
                }
                else{
                    parsed_result.encoding =rules[i].encoding;
                    parsed_result.type     =rules[i].type;
                    parsed_result.value    =match.value;
                    parsed_result.code     =cur_barcode;
                    if(rules[i].encoding==="ean13"){
                        parsed_result.base_code=this.sanitize_ean(match.base_code);
                    }
                    else{
                        parsed_result.base_code=match.base_code;
                    }
                    returnparsed_result;
                }
            }
        }
        returnparsed_result;
    },
});

returnBarcodeParser;
});
