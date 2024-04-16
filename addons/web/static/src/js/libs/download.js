/*
MITLicense

Copyright(c)2016dandavis

Permissionisherebygranted,freeofcharge,toanypersonobtainingacopy
ofthissoftwareandassociateddocumentationfiles(the"Software"),todeal
intheSoftwarewithoutrestriction,includingwithoutlimitationtherights
touse,copy,modify,merge,publish,distribute,sublicense,and/orsell
copiesoftheSoftware,andtopermitpersonstowhomtheSoftwareis
furnishedtodoso,subjecttothefollowingconditions:

Theabovecopyrightnoticeandthispermissionnoticeshallbeincludedinall
copiesorsubstantialportionsoftheSoftware.

THESOFTWAREISPROVIDED"ASIS",WITHOUTWARRANTYOFANYKIND,EXPRESSOR
IMPLIED,INCLUDINGBUTNOTLIMITEDTOTHEWARRANTIESOFMERCHANTABILITY,
FITNESSFORAPARTICULARPURPOSEANDNONINFRINGEMENT.INNOEVENTSHALLTHE
AUTHORSORCOPYRIGHTHOLDERSBELIABLEFORANYCLAIM,DAMAGESOROTHER
LIABILITY,WHETHERINANACTIONOFCONTRACT,TORTOROTHERWISE,ARISINGFROM,
OUTOFORINCONNECTIONWITHTHESOFTWAREORTHEUSEOROTHERDEALINGSINTHE
SOFTWARE.
 */

/**
 *download.jsv4.2,bydandavis;2008-2018.[MIT]seehttp://danml.com/download.htmlfortests/usage
 *
 *@param{Blob|File|String}data
 *@param{String}[filename]
 *@param{String}[mimetype]
 */
flectra.define('web.download',function(){
returnfunctiondownload(data,filename,mimetype){
    varself=window,//thisscriptisonlyforbrowsersanyway...
            defaultMime="application/octet-stream",//thisdefaultmimealsotriggersiframedownloads
            mimeType=mimetype||defaultMime,payload=data,
            url=!filename&&!mimetype&&payload,
            anchor=document.createElement("a"),
            toString=function(a){returnString(a);},
            myBlob=(self.Blob||self.MozBlob||self.WebKitBlob||toString),
            fileName=filename||"download",blob,reader;
    myBlob=myBlob.call?myBlob.bind(self):Blob;

    if(String(this)==="true"){//reversearguments,allowingdownload.bind(true,"text/xml","export.xml")toactasacallback
        payload=[payload,mimeType];
        mimeType=payload[0];
        payload=payload[1];
    }

    if(url&&url.length<2048){//ifnofilenameandnomime,assumeaurlwaspassedastheonlyargument
        fileName=url.split("/").pop().split("?")[0];
        anchor.href=url;//assignhrefproptotempanchor
        if(anchor.href.indexOf(url)!==-1){//ifthebrowserdeterminesthatit'sapotentiallyvalidurlpath:
            varajax=newXMLHttpRequest();
            ajax.open("GET",url,true);
            ajax.responseType='blob';
            ajax.onload=function(e){
                download(e.target.response,fileName,defaultMime);
            };
            setTimeout(function(){ajax.send();},0);//allowssettingcustomajaxheadersusingthereturn:
            returnajax;
        }
    }

    //goaheadanddownloaddataURLsrightaway
    if(/^data:[\w+\-]+\/[\w+\-]+[,;]/.test(payload)){

        if(payload.length>(1024*1024*1.999)&&myBlob!==toString){
            payload=dataUrlToBlob(payload);
            mimeType=payload.type||defaultMime;
        }else{
            returnnavigator.msSaveBlob? //IE10can'tdoa[download],onlyBlobs:
                    navigator.msSaveBlob(dataUrlToBlob(payload),fileName):saver(payload);//everyoneelsecansavedataURLsun-processed
        }

    }

    blob=payloadinstanceofmyBlob?payload:newmyBlob([payload],{type:mimeType});


    functiondataUrlToBlob(strUrl){
        varparts=strUrl.split(/[:;,]/),type=parts[1],
                decoder=parts[2]==="base64"?atob:decodeURIComponent,
                binData=decoder(parts.pop()),mx=binData.length,
                i=0,uiArr=newUint8Array(mx);

        for(i;i<mx;++i)uiArr[i]=binData.charCodeAt(i);

        returnnewmyBlob([uiArr],{type:type});
    }

    functionsaver(url,winMode){
        if('download'inanchor){//html5A[download]
            anchor.href=url;
            anchor.setAttribute("download",fileName);
            anchor.className="download-js-link";
            anchor.innerHTML="downloading...";
            anchor.style.display="none";
            document.body.appendChild(anchor);
            setTimeout(function(){
                anchor.click();
                document.body.removeChild(anchor);
                if(winMode===true){setTimeout(function(){self.URL.revokeObjectURL(anchor.href);},250);}
            },66);
            returntrue;
        }

        //handlenon-a[download]safariasbestwecan:
        if(/(Version)\/(\d+)\.(\d+)(?:\.(\d+))?.*Safari\//.test(navigator.userAgent)){
            url=url.replace(/^data:([\w\/\-+]+)/,defaultMime);
            if(!window.open(url)){//popupblocked,offerdirectdownload:
                if(confirm("DisplayingNewDocument\n\nUseSaveAs...todownload,thenclickbacktoreturntothispage.")){location.href=url;}
            }
            returntrue;
        }

        //doiframedataURLdownload(oldch+FF):
        varf=document.createElement("iframe");
        document.body.appendChild(f);

        if(!winMode){//forceamimethatwilldownload:
            url="data:"+url.replace(/^data:([\w\/\-+]+)/,defaultMime);
        }
        f.src=url;
        setTimeout(function(){document.body.removeChild(f);},333);
    }

    if(navigator.msSaveBlob){//IE10+:(hasBlob,butnota[download]orURL)
        returnnavigator.msSaveBlob(blob,fileName);
    }

    if(self.URL){//simplefastandmodernwayusingBlobandURL:
        saver(self.URL.createObjectURL(blob),true);
    }else{
        //handlenon-Blob()+non-URLbrowsers:
        if(typeofblob==="string"||blob.constructor===toString){
            try{
                returnsaver("data:"+mimeType+";base64,"+self.btoa(blob));
            }catch(y){
                returnsaver("data:"+mimeType+","+encodeURIComponent(blob));
            }
        }

        //BlobbutnotURLsupport:
        reader=newFileReader();
        reader.onload=function(){
            saver(this.result);
        };
        reader.readAsDataURL(blob);
    }
    returntrue;
};
});
