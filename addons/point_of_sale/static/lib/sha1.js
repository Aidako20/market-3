/*fromhttp://www.movable-type.co.uk/scripts/sha1.html*/
/*----------------------------------------------- */
/* SHA-1implementationinJavaScript                 (c)ChrisVeness2002-2014/MITLicence */
/*                                                                                               */
/* -seehttp://csrc.nist.gov/groups/ST/toolkit/secure_hashing.html                             */
/*       http://csrc.nist.gov/groups/ST/toolkit/examples.html                                   */
/*----------------------------------------------- */

/*jshintnode:true*//*globaldefine,escape,unescape*/
'usestrict';


/**
 *SHA-1hashfunctionreferenceimplementation.
 *
 *@namespace
 */
varSha1={};


/**
 *GeneratesSHA-1hashofstring.
 *
 *@param  {string}msg-(Unicode)stringtobehashed.
 *@returns{string}Hashofmsgashexcharacterstring.
 */
Sha1.hash=function(msg){
    //convertstringtoUTF-8,asSHAonlydealswithbyte-streams
    msg=msg.utf8Encode();

    //constants[§4.2.1]
    varK=[0x5a827999,0x6ed9eba1,0x8f1bbcdc,0xca62c1d6];

    //PREPROCESSING

    msg+=String.fromCharCode(0x80); //addtrailing'1'bit(+0'spadding)tostring[§5.1.1]

    //convertstringmsginto512-bit/16-integerblocksarraysofints[§5.2.1]
    varl=msg.length/4+2;//length(in32-bitintegers)ofmsg+‘1’+appendedlength
    varN=Math.ceil(l/16); //numberof16-integer-blocksrequiredtohold'l'ints
    varM=newArray(N);

    for(vari=0;i<N;i++){
        M[i]=newArray(16);
        for(varj=0;j<16;j++){ //encode4charsperinteger,big-endianencoding
            M[i][j]=(msg.charCodeAt(i*64+j*4)<<24)|(msg.charCodeAt(i*64+j*4+1)<<16)|
                (msg.charCodeAt(i*64+j*4+2)<<8)|(msg.charCodeAt(i*64+j*4+3));
        }//noterunningofftheendofmsgisok'cosbitwiseopsonNaNreturn0
    }
    //addlength(inbits)intofinalpairof32-bitintegers(big-endian)[§5.1.1]
    //note:mostsignificantwordwouldbe(len-1)*8>>>32,butsinceJSconverts
    //bitwise-opargsto32bits,weneedtosimulatethisbyarithmeticoperators
    M[N-1][14]=((msg.length-1)*8)/Math.pow(2,32);M[N-1][14]=Math.floor(M[N-1][14]);
    M[N-1][15]=((msg.length-1)*8)&0xffffffff;

    //setinitialhashvalue[§5.3.1]
    varH0=0x67452301;
    varH1=0xefcdab89;
    varH2=0x98badcfe;
    varH3=0x10325476;
    varH4=0xc3d2e1f0;

    //HASHCOMPUTATION[§6.1.2]

    varW=newArray(80);vara,b,c,d,e;
    for(vari=0;i<N;i++){

        //1-preparemessageschedule'W'
        for(vart=0; t<16;t++)W[t]=M[i][t];
        for(vart=16;t<80;t++)W[t]=Sha1.ROTL(W[t-3]^W[t-8]^W[t-14]^W[t-16],1);

        //2-initialisefiveworkingvariablesa,b,c,d,ewithprevioushashvalue
        a=H0;b=H1;c=H2;d=H3;e=H4;

        //3-mainloop
        for(vart=0;t<80;t++){
            vars=Math.floor(t/20);//seqforblocksof'f'functionsand'K'constants
            varT=(Sha1.ROTL(a,5)+Sha1.f(s,b,c,d)+e+K[s]+W[t])&0xffffffff;
            e=d;
            d=c;
            c=Sha1.ROTL(b,30);
            b=a;
            a=T;
        }

        //4-computethenewintermediatehashvalue(note'additionmodulo2^32')
        H0=(H0+a)&0xffffffff;
        H1=(H1+b)&0xffffffff;
        H2=(H2+c)&0xffffffff;
        H3=(H3+d)&0xffffffff;
        H4=(H4+e)&0xffffffff;
    }

    returnSha1.toHexStr(H0)+Sha1.toHexStr(H1)+Sha1.toHexStr(H2)+
           Sha1.toHexStr(H3)+Sha1.toHexStr(H4);
};


/**
 *Function'f'[§4.1.1].
 *@private
 */
Sha1.f=function(s,x,y,z) {
    switch(s){
        case0:return(x&y)^(~x&z);          //Ch()
        case1:return x^y ^ z;                //Parity()
        case2:return(x&y)^(x&z)^(y&z); //Maj()
        case3:return x^y ^ z;                //Parity()
    }
};

/**
 *Rotatesleft(circularleftshift)valuexbynpositions[§3.2.5].
 *@private
 */
Sha1.ROTL=function(x,n){
    return(x<<n)|(x>>>(32-n));
};


/**
 *Hexadecimalrepresentationofanumber.
 *@private
 */
Sha1.toHexStr=function(n){
    //notecan'tusetoString(16)asitisimplementation-dependant,
    //andinIEreturnssignednumberswhenusedonfullwords
    vars="",v;
    for(vari=7;i>=0;i--){v=(n>>>(i*4))&0xf;s+=v.toString(16);}
    returns;
};


/*----------------------------------------------- */


/**ExtendStringobjectwithmethodtoencodemulti-bytestringtoutf8
 * -monsur.hossa.in/2012/07/20/utf-8-in-javascript.html*/
if(typeofString.prototype.utf8Encode=='undefined'){
    String.prototype.utf8Encode=function(){
        returnunescape(encodeURIComponent(this));
    };
}

/**ExtendStringobjectwithmethodtodecodeutf8stringtomulti-byte*/
if(typeofString.prototype.utf8Decode=='undefined'){
    String.prototype.utf8Decode=function(){
        try{
            returndecodeURIComponent(escape(this));
        }catch(e){
            returnthis;//invalidUTF-8?returnas-is
        }
    };
}


/*----------------------------------------------- */
if(typeofmodule!='undefined'&&module.exports)module.exports=Sha1;//CommonJsexport
if(typeofdefine=='function'&&define.amd)define([],function(){returnSha1;});//AMD
