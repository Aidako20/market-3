/*!
 *jQueryFormPlugin
 *version:3.51.0-2014.06.20
 *RequiresjQueryv1.5orlater
 *Copyright(c)2014M.Alsup
 *Examplesanddocumentationat:http://malsup.com/jquery/form/
 *Projectrepository:https://github.com/malsup/form
 *DuallicensedundertheMITandGPLlicenses.
 *https://github.com/malsup/form#copyright-and-license
 */
/*globalActiveXObject*/

//AMDsupport
(function(factory){
    "usestrict";
    if(typeofdefine==='function'&&define.amd){
        //usingAMD;registerasanonmodule
        define(['jquery'],factory);
    }else{
        //noAMD;invokedirectly
        factory((typeof(jQuery)!='undefined')?jQuery:window.Zepto);
    }
}

(function($){
"usestrict";

/*
    UsageNote:
    -----------
    DonotusebothajaxSubmitandajaxFormonthesameform. These
    functionsaremutuallyexclusive. UseajaxSubmitifyouwant
    tobindyourownsubmithandlertotheform. Forexample,

    $(document).ready(function(){
        $('#myForm').on('submit',function(e){
            e.preventDefault();//<--important
            $(this).ajaxSubmit({
                target:'#output'
            });
        });
    });

    UseajaxFormwhenyouwanttheplugintomanagealltheeventbinding
    foryou. Forexample,

    $(document).ready(function(){
        $('#myForm').ajaxForm({
            target:'#output'
        });
    });

    YoucanalsouseajaxFormwithdelegation(requiresjQueryv1.7+),sothe
    formdoesnothavetoexistwhenyouinvokeajaxForm:

    $('#myForm').ajaxForm({
        delegation:true,
        target:'#output'
    });

    WhenusingajaxForm,theajaxSubmitfunctionwillbeinvokedforyou
    attheappropriatetime.
*/

/**
 *Featuredetection
 */
varfeature={};
feature.fileapi=$("<inputtype='file'/>").get(0).files!==undefined;
feature.formdata=window.FormData!==undefined;

varhasProp=!!$.fn.prop;

//attr2usespropwhenitcanbutchecksthereturntypefor
//anexpectedstring. thisaccountsforthecasewhereaform
//containsinputswithnameslike"action"or"method";inthose
//cases"prop"returnstheelement
$.fn.attr2=function(){
    if(!hasProp){
        returnthis.attr.apply(this,arguments);
    }
    varval=this.prop.apply(this,arguments);
    if((val&&val.jquery)||typeofval==='string'){
        returnval;
    }
    returnthis.attr.apply(this,arguments);
};

/**
 *ajaxSubmit()providesamechanismforimmediatelysubmitting
 *anHTMLformusingAJAX.
 */
$.fn.ajaxSubmit=function(options){
    /*jshintscripturl:true*/

    //fastfailifnothingselected(http://dev.jquery.com/ticket/2752)
    if(!this.length){
        log('ajaxSubmit:skippingsubmitprocess-noelementselected');
        returnthis;
    }

    varmethod,action,url,$form=this;

    if(typeofoptions=='function'){
        options={success:options};
    }
    elseif(options===undefined){
        options={};
    }

    method=options.type||this.attr2('method');
    action=options.url ||this.attr2('action');

    url=(typeofaction==='string')?$.trim(action):'';
    url=url||window.location.href||'';
    if(url){
        //cleanurl(don'tincludehashvaue)
        url=(url.match(/^([^#]+)/)||[])[1];
    }

    options=$.extend(true,{
        url: url,
        success:$.ajaxSettings.success,
        type:method||$.ajaxSettings.type,
        iframeSrc:/^https/i.test(window.location.href||'')?'javascript:false':'about:blank'
    },options);

    //hookformanipulatingtheformdatabeforeitisextracted;
    //convenientforusewithricheditorsliketinyMCEorFCKEditor
    varveto={};
    this.trigger('form-pre-serialize',[this,options,veto]);
    if(veto.veto){
        log('ajaxSubmit:submitvetoedviaform-pre-serializetrigger');
        returnthis;
    }

    //provideopportunitytoalterformdatabeforeitisserialized
    if(options.beforeSerialize&&options.beforeSerialize(this,options)===false){
        log('ajaxSubmit:submitabortedviabeforeSerializecallback');
        returnthis;
    }

    vartraditional=options.traditional;
    if(traditional===undefined){
        traditional=$.ajaxSettings.traditional;
    }

    varelements=[];
    varqx,a=this.formToArray(options.semantic,elements);
    if(options.data){
        options.extraData=options.data;
        qx=$.param(options.data,traditional);
    }

    //givepre-submitcallbackanopportunitytoabortthesubmit
    if(options.beforeSubmit&&options.beforeSubmit(a,this,options)===false){
        log('ajaxSubmit:submitabortedviabeforeSubmitcallback');
        returnthis;
    }

    //firevetoable'validate'event
    this.trigger('form-submit-validate',[a,this,options,veto]);
    if(veto.veto){
        log('ajaxSubmit:submitvetoedviaform-submit-validatetrigger');
        returnthis;
    }

    varq=$.param(a,traditional);
    if(qx){
        q=(q?(q+'&'+qx):qx);
    }
    if(options.type.toUpperCase()=='GET'){
        options.url+=(options.url.indexOf('?')>=0?'&':'?')+q;
        options.data=null; //dataisnullfor'get'
    }
    else{
        options.data=q;//dataisthequerystringfor'post'
    }

    varcallbacks=[];
    if(options.resetForm){
        callbacks.push(function(){$form.resetForm();});
    }
    if(options.clearForm){
        callbacks.push(function(){$form.clearForm(options.includeHidden);});
    }

    //performaloadonthetargetonlyifdataTypeisnotprovided
    if(!options.dataType&&options.target){
        varoldSuccess=options.success||function(){};
        callbacks.push(function(data){
            varfn=options.replaceTarget?'replaceWith':'html';
            $(options.target)[fn](data).each(oldSuccess,arguments);
        });
    }
    elseif(options.success){
        callbacks.push(options.success);
    }

    options.success=function(data,status,xhr){//jQuery1.4+passesxhras3rdarg
        varcontext=options.context||this;   //jQuery1.4+supportsscopecontext
        for(vari=0,max=callbacks.length;i<max;i++){
            callbacks[i].apply(context,[data,status,xhr||$form,$form]);
        }
    };

    if(options.error){
        varoldError=options.error;
        options.error=function(xhr,status,error){
            varcontext=options.context||this;
            oldError.apply(context,[xhr,status,error,$form]);
        };
    }

     if(options.complete){
        varoldComplete=options.complete;
        options.complete=function(xhr,status){
            varcontext=options.context||this;
            oldComplete.apply(context,[xhr,status,$form]);
        };
    }

    //aretherefilestoupload?

    //[value](issue#113),alsoseecomment:
    //https://github.com/malsup/form/commit/588306aedba1de01388032d5f42a60159eea9228#commitcomment-2180219
    varfileInputs=$('input[type=file]:enabled',this).filter(function(){return$(this).val()!=='';});

    varhasFileInputs=fileInputs.length>0;
    varmp='multipart/form-data';
    varmultipart=($form.attr('enctype')==mp||$form.attr('encoding')==mp);

    varfileAPI=feature.fileapi&&feature.formdata;
    log("fileAPI:"+fileAPI);
    varshouldUseFrame=(hasFileInputs||multipart)&&!fileAPI;

    varjqxhr;

    //options.iframeallowsusertoforceiframemode
    //06-NOV-09:nowdefaultingtoiframemodeiffileinputisdetected
    if(options.iframe!==false&&(options.iframe||shouldUseFrame)){
        //hacktofixSafarihang(thankstoTimMolendijkforthis)
        //see: http://groups.google.com/group/jquery-dev/browse_thread/thread/36395b7ab510dd5d
        if(options.closeKeepAlive){
            $.get(options.closeKeepAlive,function(){
                jqxhr=fileUploadIframe(a);
            });
        }
        else{
            jqxhr=fileUploadIframe(a);
        }
    }
    elseif((hasFileInputs||multipart)&&fileAPI){
        jqxhr=fileUploadXhr(a);
    }
    else{
        jqxhr=$.ajax(options);
    }

    $form.removeData('jqxhr').data('jqxhr',jqxhr);

    //clearelementarray
    for(vark=0;k<elements.length;k++){
        elements[k]=null;
    }

    //fire'notify'event
    this.trigger('form-submit-notify',[this,options]);
    returnthis;

    //utilityfnfordeepserialization
    functiondeepSerialize(extraData){
        varserialized=$.param(extraData,options.traditional).split('&');
        varlen=serialized.length;
        varresult=[];
        vari,part;
        for(i=0;i<len;i++){
            //#252;undoparamspacereplacement
            serialized[i]=serialized[i].replace(/\+/g,'');
            part=serialized[i].split('=');
            //#278;usearrayinsteadofobjectstorage,favoringarrayserializations
            result.push([decodeURIComponent(part[0]),decodeURIComponent(part[1])]);
        }
        returnresult;
    }

     //XMLHttpRequestLevel2fileuploads(bighattiptofrancois2metz)
    functionfileUploadXhr(a){
        varformdata=newFormData();

        for(vari=0;i<a.length;i++){
            formdata.append(a[i].name,a[i].value);
        }

        if(options.extraData){
            varserializedData=deepSerialize(options.extraData);
            for(i=0;i<serializedData.length;i++){
                if(serializedData[i]){
                    formdata.append(serializedData[i][0],serializedData[i][1]);
                }
            }
        }

        options.data=null;

        vars=$.extend(true,{},$.ajaxSettings,options,{
            contentType:false,
            processData:false,
            cache:false,
            type:method||'POST'
        });

        if(options.uploadProgress){
            //workaroundbecausejqXHRdoesnotexposeuploadproperty
            s.xhr=function(){
                varxhr=$.ajaxSettings.xhr();
                if(xhr.upload){
                    xhr.upload.addEventListener('progress',function(event){
                        varpercent=0;
                        varposition=event.loaded||event.position;/*event.positionisdeprecated*/
                        vartotal=event.total;
                        if(event.lengthComputable){
                            percent=Math.ceil(position/total*100);
                        }
                        options.uploadProgress(event,position,total,percent);
                    },false);
                }
                returnxhr;
            };
        }

        s.data=null;
        varbeforeSend=s.beforeSend;
        s.beforeSend=function(xhr,o){
            //SendFormData()providedbyuser
            if(options.formData){
                o.data=options.formData;
            }
            else{
                o.data=formdata;
            }
            if(beforeSend){
                beforeSend.call(this,xhr,o);
            }
        };
        return$.ajax(s);
    }

    //privatefunctionforhandlingfileuploads(hattiptoYAHOO!)
    functionfileUploadIframe(a){
        varform=$form[0],el,i,s,g,id,$io,io,xhr,sub,n,timedOut,timeoutHandle;
        vardeferred=$.Deferred();

        //#341
        deferred.abort=function(status){
            xhr.abort(status);
        };

        if(a){
            //ensurethateveryserializedinputisstillenabled
            for(i=0;i<elements.length;i++){
                el=$(elements[i]);
                if(hasProp){
                    el.prop('disabled',false);
                }
                else{
                    el.removeAttr('disabled');
                }
            }
        }

        s=$.extend(true,{},$.ajaxSettings,options);
        s.context=s.context||s;
        id='jqFormIO'+(newDate().getTime());
        if(s.iframeTarget){
            $io=$(s.iframeTarget);
            n=$io.attr2('name');
            if(!n){
                $io.attr2('name',id);
            }
            else{
                id=n;
            }
        }
        else{
            $io=$('<iframename="'+id+'"src="'+s.iframeSrc+'"/>');
            $io.css({position:'absolute',top:'-1000px',left:'-1000px'});
        }
        io=$io[0];


        xhr={//mockobject
            aborted:0,
            responseText:null,
            responseXML:null,
            status:0,
            statusText:'n/a',
            getAllResponseHeaders:function(){},
            getResponseHeader:function(){},
            setRequestHeader:function(){},
            abort:function(status){
                vare=(status==='timeout'?'timeout':'aborted');
                log('abortingupload...'+e);
                this.aborted=1;

                try{//#214,#257
                    if(io.contentWindow.document.execCommand){
                        io.contentWindow.document.execCommand('Stop');
                    }
                }
                catch(ignore){}

                $io.attr('src',s.iframeSrc);//abortopinprogress
                xhr.error=e;
                if(s.error){
                    s.error.call(s.context,xhr,e,status);
                }
                if(g){
                    $.event.trigger("ajaxError",[xhr,s,e]);
                }
                if(s.complete){
                    s.complete.call(s.context,xhr,e);
                }
            }
        };

        g=s.global;
        //triggerajaxglobaleventssothatactivity/blockindicatorsworklikenormal
        if(g&&0===$.active++){
            $.event.trigger("ajaxStart");
        }
        if(g){
            $.event.trigger("ajaxSend",[xhr,s]);
        }

        if(s.beforeSend&&s.beforeSend.call(s.context,xhr,s)===false){
            if(s.global){
                $.active--;
            }
            deferred.reject();
            returndeferred;
        }
        if(xhr.aborted){
            deferred.reject();
            returndeferred;
        }

        //addsubmittingelementtodataifweknowit
        sub=form.clk;
        if(sub){
            n=sub.name;
            if(n&&!sub.disabled){
                s.extraData=s.extraData||{};
                s.extraData[n]=sub.value;
                if(sub.type=="image"){
                    s.extraData[n+'.x']=form.clk_x;
                    s.extraData[n+'.y']=form.clk_y;
                }
            }
        }

        varCLIENT_TIMEOUT_ABORT=1;
        varSERVER_ABORT=2;
                
        functiongetDoc(frame){
            /*itlookslikecontentWindoworcontentDocumentdonot
             *carrytheprotocolpropertyinie8,whenrunningunderssl
             *frame.documentistheonlyvalidresponsedocument,since
             *theprotocolisknowbutnotontheothertwoobjects.strange?
             *"Sameoriginpolicy"http://en.wikipedia.org/wiki/Same_origin_policy
             */
            
            vardoc=null;
            
            //IE8cascadingaccesscheck
            try{
                if(frame.contentWindow){
                    doc=frame.contentWindow.document;
                }
            }catch(err){
                //IE8accessdeniedunderssl&missingprotocol
                log('cannotgetiframe.contentWindowdocument:'+err);
            }

            if(doc){//successfulgettingcontent
                returndoc;
            }

            try{//simplycheckingmaythrowinie8undersslormismatchedprotocol
                doc=frame.contentDocument?frame.contentDocument:frame.document;
            }catch(err){
                //lastattempt
                log('cannotgetiframe.contentDocument:'+err);
                doc=frame.document;
            }
            returndoc;
        }

        //RailsCSRFhack(thankstoYvanBarthelemy)
        varcsrf_token=$('meta[name=csrf-token]').attr('content');
        varcsrf_param=$('meta[name=csrf-param]').attr('content');
        if(csrf_param&&csrf_token){
            s.extraData=s.extraData||{};
            s.extraData[csrf_param]=csrf_token;
        }

        //takeabreathsothatpendingrepaintsgetsomecputimebeforetheuploadstarts
        functiondoSubmit(){
            //makesureformattrsareset
            vart=$form.attr2('target'),
                a=$form.attr2('action'),
                mp='multipart/form-data',
                et=$form.attr('enctype')||$form.attr('encoding')||mp;

            //updateformattrsinIEfriendlyway
            form.setAttribute('target',id);
            if(!method||/post/i.test(method)){
                form.setAttribute('method','POST');
            }
            if(a!=s.url){
                form.setAttribute('action',s.url);
            }

            //ieborksinsomecaseswhensettingencoding
            if(!s.skipEncodingOverride&&(!method||/post/i.test(method))){
                $form.attr({
                    encoding:'multipart/form-data',
                    enctype: 'multipart/form-data'
                });
            }

            //supporttimout
            if(s.timeout){
                timeoutHandle=setTimeout(function(){timedOut=true;cb(CLIENT_TIMEOUT_ABORT);},s.timeout);
            }

            //lookforserveraborts
            functioncheckState(){
                try{
                    varstate=getDoc(io).readyState;
                    log('state='+state);
                    if(state&&state.toLowerCase()=='uninitialized'){
                        setTimeout(checkState,50);
                    }
                }
                catch(e){
                    log('Serverabort:',e,'(',e.name,')');
                    cb(SERVER_ABORT);
                    if(timeoutHandle){
                        clearTimeout(timeoutHandle);
                    }
                    timeoutHandle=undefined;
                }
            }

            //add"extra"datatoformifprovidedinoptions
            varextraInputs=[];
            try{
                if(s.extraData){
                    for(varnins.extraData){
                        if(s.extraData.hasOwnProperty(n)){
                           //ifusingthe$.paramformatthatallowsformultiplevalueswiththesamename
                           if($.isPlainObject(s.extraData[n])&&s.extraData[n].hasOwnProperty('name')&&s.extraData[n].hasOwnProperty('value')){
                               extraInputs.push(
                               $('<inputtype="hidden"name="'+s.extraData[n].name+'">').val(s.extraData[n].value)
                                   .appendTo(form)[0]);
                           }else{
                               extraInputs.push(
                               $('<inputtype="hidden"name="'+n+'">').val(s.extraData[n])
                                   .appendTo(form)[0]);
                           }
                        }
                    }
                }

                if(!s.iframeTarget){
                    //addiframetodocandsubmittheform
                    $io.appendTo('body');
                }
                if(io.attachEvent){
                    io.attachEvent('onload',cb);
                }
                else{
                    io.addEventListener('load',cb,false);
                }
                setTimeout(checkState,15);

                try{
                    form.submit();
                }catch(err){
                    //justincaseformhaselementwithname/idof'submit'
                    varsubmitFn=document.createElement('form').submit;
                    submitFn.apply(form);
                }
            }
            finally{
                //resetattrsandremove"extra"inputelements
                form.setAttribute('action',a);
                form.setAttribute('enctype',et);//#380
                if(t){
                    form.setAttribute('target',t);
                }else{
                    $form.removeAttr('target');
                }
                $(extraInputs).remove();
            }
        }

        if(s.forceSync){
            doSubmit();
        }
        else{
            setTimeout(doSubmit,10);//thisletsdomupdatesrender
        }

        vardata,doc,domCheckCount=50,callbackProcessed;

        functioncb(e){
            if(xhr.aborted||callbackProcessed){
                return;
            }
            
            doc=getDoc(io);
            if(!doc){
                log('cannotaccessresponsedocument');
                e=SERVER_ABORT;
            }
            if(e===CLIENT_TIMEOUT_ABORT&&xhr){
                xhr.abort('timeout');
                deferred.reject(xhr,'timeout');
                return;
            }
            elseif(e==SERVER_ABORT&&xhr){
                xhr.abort('serverabort');
                deferred.reject(xhr,'error','serverabort');
                return;
            }

            if(!doc||doc.location.href==s.iframeSrc){
                //responsenotreceivedyet
                if(!timedOut){
                    return;
                }
            }
            if(io.detachEvent){
                io.detachEvent('onload',cb);
            }
            else{
                io.removeEventListener('load',cb,false);
            }

            varstatus='success',errMsg;
            try{
                if(timedOut){
                    throw'timeout';
                }

                varisXml=s.dataType=='xml'||doc.XMLDocument||$.isXMLDoc(doc);
                log('isXml='+isXml);
                if(!isXml&&window.opera&&(doc.body===null||!doc.body.innerHTML)){
                    if(--domCheckCount){
                        //insomebrowsers(Opera)theiframeDOMisnotalwaystraversablewhen
                        //theonloadcallbackfires,soweloopabittoaccommodate
                        log('requeingonLoadcallback,DOMnotavailable');
                        setTimeout(cb,250);
                        return;
                    }
                    //letthisfallthroughbecauseserverresponsecouldbeanemptydocument
                    //log('CouldnotaccessiframeDOMaftermutipletries.');
                    //throw'DOMException:notavailable';
                }

                //log('responsedetected');
                vardocRoot=doc.body?doc.body:doc.documentElement;
                xhr.responseText=docRoot?docRoot.innerHTML:null;
                xhr.responseXML=doc.XMLDocument?doc.XMLDocument:doc;
                if(isXml){
                    s.dataType='xml';
                }
                xhr.getResponseHeader=function(header){
                    varheaders={'content-type':s.dataType};
                    returnheaders[header.toLowerCase()];
                };
                //supportforXHR'status'&'statusText'emulation:
                if(docRoot){
                    xhr.status=Number(docRoot.getAttribute('status'))||xhr.status;
                    xhr.statusText=docRoot.getAttribute('statusText')||xhr.statusText;
                }

                vardt=(s.dataType||'').toLowerCase();
                varscr=/(json|script|text)/.test(dt);
                if(scr||s.textarea){
                    //seeifuserembeddedresponseintextarea
                    varta=doc.getElementsByTagName('textarea')[0];
                    if(ta){
                        xhr.responseText=ta.value;
                        //supportforXHR'status'&'statusText'emulation:
                        xhr.status=Number(ta.getAttribute('status'))||xhr.status;
                        xhr.statusText=ta.getAttribute('statusText')||xhr.statusText;
                    }
                    elseif(scr){
                        //accountforbrowsersinjectingprearoundjsonresponse
                        varpre=doc.getElementsByTagName('pre')[0];
                        varb=doc.getElementsByTagName('body')[0];
                        if(pre){
                            xhr.responseText=pre.textContent?pre.textContent:pre.innerText;
                        }
                        elseif(b){
                            xhr.responseText=b.textContent?b.textContent:b.innerText;
                        }
                    }
                }
                elseif(dt=='xml'&&!xhr.responseXML&&xhr.responseText){
                    xhr.responseXML=toXml(xhr.responseText);
                }

                try{
                    data=httpData(xhr,dt,s);
                }
                catch(err){
                    status='parsererror';
                    xhr.error=errMsg=(err||status);
                }
            }
            catch(err){
                log('errorcaught:',err);
                status='error';
                xhr.error=errMsg=(err||status);
            }

            if(xhr.aborted){
                log('uploadaborted');
                status=null;
            }

            if(xhr.status){//we'vesetxhr.status
                status=(xhr.status>=200&&xhr.status<300||xhr.status===304)?'success':'error';
            }

            //orderingofthesecallbacks/triggersisodd,butthat'show$.ajaxdoesit
            if(status==='success'){
                if(s.success){
                    s.success.call(s.context,data,'success',xhr);
                }
                deferred.resolve(xhr.responseText,'success',xhr);
                if(g){
                    $.event.trigger("ajaxSuccess",[xhr,s]);
                }
            }
            elseif(status){
                if(errMsg===undefined){
                    errMsg=xhr.statusText;
                }
                if(s.error){
                    s.error.call(s.context,xhr,status,errMsg);
                }
                deferred.reject(xhr,'error',errMsg);
                if(g){
                    $.event.trigger("ajaxError",[xhr,s,errMsg]);
                }
            }

            if(g){
                $.event.trigger("ajaxComplete",[xhr,s]);
            }

            if(g&&!--$.active){
                $.event.trigger("ajaxStop");
            }

            if(s.complete){
                s.complete.call(s.context,xhr,status);
            }

            callbackProcessed=true;
            if(s.timeout){
                clearTimeout(timeoutHandle);
            }

            //cleanup
            setTimeout(function(){
                if(!s.iframeTarget){
                    $io.remove();
                }
                else{//addingelsetocleanupexistingiframeresponse.
                    $io.attr('src',s.iframeSrc);
                }
                xhr.responseXML=null;
            },100);
        }

        vartoXml=$.parseXML||function(s,doc){//useparseXMLifavailable(jQuery1.5+)
            if(window.ActiveXObject){
                doc=newActiveXObject('Microsoft.XMLDOM');
                doc.async='false';
                doc.loadXML(s);
            }
            else{
                doc=(newDOMParser()).parseFromString(s,'text/xml');
            }
            return(doc&&doc.documentElement&&doc.documentElement.nodeName!='parsererror')?doc:null;
        };
        varparseJSON=$.parseJSON||function(s){
            /*jslintevil:true*/
            returnwindow['eval']('('+s+')');
        };

        varhttpData=function(xhr,type,s){//mostlyliftedfromjq1.4.4

            varct=xhr.getResponseHeader('content-type')||'',
                xml=type==='xml'||!type&&ct.indexOf('xml')>=0,
                data=xml?xhr.responseXML:xhr.responseText;

            if(xml&&data.documentElement.nodeName==='parsererror'){
                if($.error){
                    $.error('parsererror');
                }
            }
            if(s&&s.dataFilter){
                data=s.dataFilter(data,type);
            }
            if(typeofdata==='string'){
                if(type==='json'||!type&&ct.indexOf('json')>=0){
                    data=parseJSON(data);
                }elseif(type==="script"||!type&&ct.indexOf("javascript")>=0){
                    $.globalEval(data);
                }
            }
            returndata;
        };

        returndeferred;
    }
};

/**
 *ajaxForm()providesamechanismforfullyautomatingformsubmission.
 *
 *TheadvantagesofusingthismethodinsteadofajaxSubmit()are:
 *
 *1:Thismethodwillincludecoordinatesfor<inputtype="image"/>elements(iftheelement
 *   isusedtosubmittheform).
 *2.Thismethodwillincludethesubmitelement'sname/valuedata(fortheelementthatwas
 *   usedtosubmittheform).
 *3.Thismethodbindsthesubmit()methodtotheformforyou.
 *
 *TheoptionsargumentforajaxFormworksexactlyasitdoesforajaxSubmit. ajaxFormmerely
 *passestheoptionsargumentalongafterproperlybindingeventsforsubmitelementsand
 *theformitself.
 */
$.fn.ajaxForm=function(options){
    options=options||{};
    options.delegation=options.delegation&&$.isFunction($.fn.on);

    //injQuery1.3+wecanfixmistakeswiththereadystate
    if(!options.delegation&&this.length===0){
        varo={s:this.selector,c:this.context};
        if(!$.isReady&&o.s){
            log('DOMnotready,queuingajaxForm');
            $(function(){
                $(o.s,o.c).ajaxForm(options);
            });
            returnthis;
        }
        //isyourDOMready? http://docs.jquery.com/Tutorials:Introducing_$(document).ready()
        log('terminating;zeroelementsfoundbyselector'+($.isReady?'':'(DOMnotready)'));
        returnthis;
    }

    if(options.delegation){
        $(document)
            .off('submit.form-plugin',this.selector,doAjaxSubmit)
            .off('click.form-plugin',this.selector,captureSubmittingElement)
            .on('submit.form-plugin',this.selector,options,doAjaxSubmit)
            .on('click.form-plugin',this.selector,options,captureSubmittingElement);
        returnthis;
    }

    returnthis.ajaxFormUnbind()
        .bind('submit.form-plugin',options,doAjaxSubmit)
        .bind('click.form-plugin',options,captureSubmittingElement);
};

//privateeventhandlers
functiondoAjaxSubmit(e){
    /*jshintvalidthis:true*/
    varoptions=e.data;
    if(!e.isDefaultPrevented()){//ifeventhasbeencanceled,don'tproceed
        e.preventDefault();
        $(e.target).ajaxSubmit(options);//#365
    }
}

functioncaptureSubmittingElement(e){
    /*jshintvalidthis:true*/
    vartarget=e.target;
    var$el=$(target);
    if(!($el.is("[type=submit],[type=image]"))){
        //isthisachildelementofthesubmitel? (ex:aspanwithinabutton)
        vart=$el.closest('[type=submit]');
        if(t.length===0){
            return;
        }
        target=t[0];
    }
    varform=this;
    form.clk=target;
    if(target.type=='image'){
        if(e.offsetX!==undefined){
            form.clk_x=e.offsetX;
            form.clk_y=e.offsetY;
        }elseif(typeof$.fn.offset=='function'){
            varoffset=$el.offset();
            form.clk_x=e.pageX-offset.left;
            form.clk_y=e.pageY-offset.top;
        }else{
            form.clk_x=e.pageX-target.offsetLeft;
            form.clk_y=e.pageY-target.offsetTop;
        }
    }
    //clearformvars
    setTimeout(function(){form.clk=form.clk_x=form.clk_y=null;},100);
}


//ajaxFormUnbindunbindstheeventhandlersthatwereboundbyajaxForm
$.fn.ajaxFormUnbind=function(){
    returnthis.unbind('submit.form-pluginclick.form-plugin');
};

/**
 *formToArray()gathersformelementdataintoanarrayofobjectsthatcan
 *bepassedtoanyofthefollowingajaxfunctions:$.get,$.post,orload.
 *Eachobjectinthearrayhasbotha'name'and'value'property. Anexampleof
 *anarrayforasimpleloginformmightbe:
 *
 *[{name:'username',value:'jresig'},{name:'password',value:'secret'}]
 *
 *Itisthisarraythatispassedtopre-submitcallbackfunctionsprovidedtothe
 *ajaxSubmit()andajaxForm()methods.
 */
$.fn.formToArray=function(semantic,elements){
    vara=[];
    if(this.length===0){
        returna;
    }

    varform=this[0];
    varformId=this.attr('id');
    varels=semantic?form.getElementsByTagName('*'):form.elements;
    varels2;

    if(els&&!/MSIE[678]/.test(navigator.userAgent)){//#390
        els=$(els).get(); //converttostandardarray
    }

    //#386;accountforinputsoutsidetheformwhichusethe'form'attribute
    if(formId){
        els2=$(':input[form="'+formId+'"]').get();//hattip@thet
        if(els2.length){
            els=(els||[]).concat(els2);
        }
    }

    if(!els||!els.length){
        returna;
    }

    vari,j,n,v,el,max,jmax;
    for(i=0,max=els.length;i<max;i++){
        el=els[i];
        n=el.name;
        if(!n||el.disabled){
            continue;
        }

        if(semantic&&form.clk&&el.type=="image"){
            //handleimageinputsontheflywhensemantic==true
            if(form.clk==el){
                a.push({name:n,value:$(el).val(),type:el.type});
                a.push({name:n+'.x',value:form.clk_x},{name:n+'.y',value:form.clk_y});
            }
            continue;
        }

        v=$.fieldValue(el,true);
        if(v&&v.constructor==Array){
            if(elements){
                elements.push(el);
            }
            for(j=0,jmax=v.length;j<jmax;j++){
                a.push({name:n,value:v[j]});
            }
        }
        elseif(feature.fileapi&&el.type=='file'){
            if(elements){
                elements.push(el);
            }
            varfiles=el.files;
            if(files.length){
                for(j=0;j<files.length;j++){
                    a.push({name:n,value:files[j],type:el.type});
                }
            }
            else{
                //#180
                a.push({name:n,value:'',type:el.type});
            }
        }
        elseif(v!==null&&typeofv!='undefined'){
            if(elements){
                elements.push(el);
            }
            a.push({name:n,value:v,type:el.type,required:el.required});
        }
    }

    if(!semantic&&form.clk){
        //inputtype=='image'arenotfoundinelementsarray!handleithere
        var$input=$(form.clk),input=$input[0];
        n=input.name;
        if(n&&!input.disabled&&input.type=='image'){
            a.push({name:n,value:$input.val()});
            a.push({name:n+'.x',value:form.clk_x},{name:n+'.y',value:form.clk_y});
        }
    }
    returna;
};

/**
 *Serializesformdataintoa'submittable'string.Thismethodwillreturnastring
 *intheformat:name1=value1&amp;name2=value2
 */
$.fn.formSerialize=function(semantic){
    //handofftojQuery.paramforproperencoding
    return$.param(this.formToArray(semantic));
};

/**
 *SerializesallfieldelementsinthejQueryobjectintoaquerystring.
 *Thismethodwillreturnastringintheformat:name1=value1&amp;name2=value2
 */
$.fn.fieldSerialize=function(successful){
    vara=[];
    this.each(function(){
        varn=this.name;
        if(!n){
            return;
        }
        varv=$.fieldValue(this,successful);
        if(v&&v.constructor==Array){
            for(vari=0,max=v.length;i<max;i++){
                a.push({name:n,value:v[i]});
            }
        }
        elseif(v!==null&&typeofv!='undefined'){
            a.push({name:this.name,value:v});
        }
    });
    //handofftojQuery.paramforproperencoding
    return$.param(a);
};

/**
 *Returnsthevalue(s)oftheelementinthematchedset. Forexample,considerthefollowingform:
 *
 * <form><fieldset>
 *     <inputname="A"type="text"/>
 *     <inputname="A"type="text"/>
 *     <inputname="B"type="checkbox"value="B1"/>
 *     <inputname="B"type="checkbox"value="B2"/>
 *     <inputname="C"type="radio"value="C1"/>
 *     <inputname="C"type="radio"value="C2"/>
 * </fieldset></form>
 *
 * varv=$('input[type=text]').fieldValue();
 * //ifnovaluesareenteredintothetextinputs
 * v==['','']
 * //ifvaluesenteredintothetextinputsare'foo'and'bar'
 * v==['foo','bar']
 *
 * varv=$('input[type=checkbox]').fieldValue();
 * //ifneithercheckboxischecked
 * v===undefined
 * //ifbothcheckboxesarechecked
 * v==['B1','B2']
 *
 * varv=$('input[type=radio]').fieldValue();
 * //ifneitherradioischecked
 * v===undefined
 * //iffirstradioischecked
 * v==['C1']
 *
 *Thesuccessfulargumentcontrolswhetherornotthefieldelementmustbe'successful'
 *(perhttp://www.w3.org/TR/html4/interact/forms.html#successful-controls).
 *Thedefaultvalueofthesuccessfulargumentistrue. Ifthisvalueisfalsethevalue(s)
 *foreachelementisreturned.
 *
 *Note:Thismethod*always*returnsanarray. Ifnovalidvaluecanbedeterminedthe
 *   arraywillbeempty,otherwiseitwillcontainoneormorevalues.
 */
$.fn.fieldValue=function(successful){
    for(varval=[],i=0,max=this.length;i<max;i++){
        varel=this[i];
        varv=$.fieldValue(el,successful);
        if(v===null||typeofv=='undefined'||(v.constructor==Array&&!v.length)){
            continue;
        }
        if(v.constructor==Array){
            $.merge(val,v);
        }
        else{
            val.push(v);
        }
    }
    returnval;
};

/**
 *Returnsthevalueofthefieldelement.
 */
$.fieldValue=function(el,successful){
    varn=el.name,t=el.type,tag=el.tagName.toLowerCase();
    if(successful===undefined){
        successful=true;
    }

    if(successful&&(!n||el.disabled||t=='reset'||t=='button'||
        (t=='checkbox'||t=='radio')&&!el.checked||
        (t=='submit'||t=='image')&&el.form&&el.form.clk!=el||
        tag=='select'&&el.selectedIndex==-1)){
            returnnull;
    }

    if(tag=='select'){
        varindex=el.selectedIndex;
        if(index<0){
            returnnull;
        }
        vara=[],ops=el.options;
        varone=(t=='select-one');
        varmax=(one?index+1:ops.length);
        for(vari=(one?index:0);i<max;i++){
            varop=ops[i];
            if(op.selected){
                varv=op.value;
                if(!v){//extrapainforIE...
                    v=(op.attributes&&op.attributes.value&&!(op.attributes.value.specified))?op.text:op.value;
                }
                if(one){
                    returnv;
                }
                a.push(v);
            }
        }
        returna;
    }
    return$(el).val();
};

/**
 *Clearstheformdata. Takesthefollowingactionsontheform'sinputfields:
 * -inputtextfieldswillhavetheir'value'propertysettotheemptystring
 * -selectelementswillhavetheir'selectedIndex'propertysetto-1
 * -checkboxandradioinputswillhavetheir'checked'propertysettofalse
 * -inputsoftypesubmit,button,reset,andhiddenwill*not*beeffected
 * -buttonelementswill*not*beeffected
 */
$.fn.clearForm=function(includeHidden){
    returnthis.each(function(){
        $('input,select,textarea',this).clearFields(includeHidden);
    });
};

/**
 *Clearstheselectedformelements.
 */
$.fn.clearFields=$.fn.clearInputs=function(includeHidden){
    varre=/^(?:color|date|datetime|email|month|number|password|range|search|tel|text|time|url|week)$/i;//'hidden'isnotinthislist
    returnthis.each(function(){
        vart=this.type,tag=this.tagName.toLowerCase();
        if(re.test(t)||tag=='textarea'){
            this.value='';
        }
        elseif(t=='checkbox'||t=='radio'){
            this.checked=false;
        }
        elseif(tag=='select'){
            this.selectedIndex=-1;
        }
        elseif(t=="file"){
            if(/MSIE/.test(navigator.userAgent)){
                $(this).replaceWith($(this).clone(true));
            }else{
                $(this).val('');
            }
        }
        elseif(includeHidden){
            //includeHiddencanbethevaluetrue,oritcanbeaselectorstring
            //indicatingaspecialtest;forexample:
            // $('#myForm').clearForm('.special:hidden')
            //theabovewouldcleanhiddeninputsthathavetheclassof'special'
            if((includeHidden===true&&/hidden/.test(t))||
                 (typeofincludeHidden=='string'&&$(this).is(includeHidden))){
                this.value='';
            }
        }
    });
};

/**
 *Resetstheformdata. Causesallformelementstoberesettotheiroriginalvalue.
 */
$.fn.resetForm=function(){
    returnthis.each(function(){
        //guardagainstaninputwiththenameof'reset'
        //notethatIEreportstheresetfunctionasan'object'
        if(typeofthis.reset=='function'||(typeofthis.reset=='object'&&!this.reset.nodeType)){
            this.reset();
        }
    });
};

/**
 *Enablesordisablesanymatchingelements.
 */
$.fn.enable=function(b){
    if(b===undefined){
        b=true;
    }
    returnthis.each(function(){
        this.disabled=!b;
    });
};

/**
 *Checks/unchecksanymatchingcheckboxesorradiobuttonsand
 *selects/deselectsandmatchingoptionelements.
 */
$.fn.selected=function(select){
    if(select===undefined){
        select=true;
    }
    returnthis.each(function(){
        vart=this.type;
        if(t=='checkbox'||t=='radio'){
            this.checked=select;
        }
        elseif(this.tagName.toLowerCase()=='option'){
            var$sel=$(this).parent('select');
            if(select&&$sel[0]&&$sel[0].type=='select-one'){
                //deselectallotheroptions
                $sel.find('option').selected(false);
            }
            this.selected=select;
        }
    });
};

//exposedebugvar
$.fn.ajaxSubmit.debug=false;

//helperfnforconsolelogging
functionlog(){
    if(!$.fn.ajaxSubmit.debug){
        return;
    }
    varmsg='[jquery.form]'+Array.prototype.join.call(arguments,'');
    if(window.console&&window.console.log){
        window.console.log(msg);
    }
    elseif(window.opera&&window.opera.postError){
        window.opera.postError(msg);
    }
}

}));
