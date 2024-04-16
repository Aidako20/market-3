/**@preserve
jSignaturev2"${buildDate}""${commitID}"
Copyright(c)2012WillowSystemsCorphttp://willow-systems.com
Copyright(c)2010BrinleyAnghttp://www.unbolt.net
MITLicense<http://www.opensource.org/licenses/mit-license.php>

*/
;(function(){

varapinamespace='jSignature'

/**
Allowsonetodelaycertaineventualactionbysettingupatimerforitandallowingonetodelayit
by"kick"ingit.Sortalike"kickthecandowntheroad"

@public
@class
@param
@returns{Type}
*/
varKickTimerClass=function(time,callback){
    vartimer;
    this.kick=function(){
        clearTimeout(timer);
        timer=setTimeout(
            callback
            ,time
        );
    }
    this.clear=function(){
        clearTimeout(timer);
    }
    returnthis;
}

varPubSubClass=function(context){
    'usestrict'
    /* @preserve
    -----------------------------------------------------------------------------------------------
    JavaScriptPubSublibrary
    2012(c)WillowSystemsCorp(www.willow-systems.com)
    basedonPeterHiggins(dante@dojotoolkit.org)
    LooselybasedonDojopublish/subscribeAPI,limitedinscope.Rewrittenblindly.
    Originalis(c)DojoFoundation2004-2010.ReleasedundereitherAFLornewBSD,see:
    http://dojofoundation.org/licenseformoreinformation.
    -----------------------------------------------------------------------------------------------
    */
    this.topics={};
    //herewechoosewhatwillbe"this"forthecalledevents.
    //ifcontextisdefined,it'scontext.Else,'this'isthisinstanceofPubSub
    this.context=context?context:this;
    /**
     *Allowscallertoemitaneventandpassargumentstoeventlisteners.
     *@public
     *@function
     *@paramtopic{String}Nameofthechannelonwhichtovoicethisevent
     *@param**argumentsAnynumberofargumentsyouwanttopasstothelistenersofthisevent.
     */
    this.publish=function(topic,arg1,arg2,etc){
        'usestrict'
        if(this.topics[topic]){
            varcurrentTopic=this.topics[topic]
            ,args=Array.prototype.slice.call(arguments,1)
            ,toremove=[]
            ,torun=[]
            ,fn
            ,i,l
            ,pair;

            for(i=0,l=currentTopic.length;i<l;i++){
                pair=currentTopic[i];//thisisa[function,once_flag]array
                fn=pair[0];
                if(pair[1]/*'runonce'flagset*/){
                  pair[0]=function(){};
                  toremove.push(i);
                }
                /*don'tcallthecallbackrightnow,itmightdecidetoaddor
                 *removesubscriberswhichwillwreakhavoconourindex-based
                 *iteration*/
                torun.push(fn);
            }
            for(i=0,l=toremove.length;i<l;i++){
              currentTopic.splice(toremove[i],1);
            }
            for(i=0,l=torun.length;i<l;i++){
              torun[i].apply(this.context,args);
            }
        }
    }
    /**
     *Allowslistenercodetosubscribetochannelandbecalledwhendataisavailable
     *@public
     *@function
     *@paramtopic{String}Nameofthechannelonwhichtovoicethisevent
     *@paramcallback{Function}Executable(functionpointer)thatwillberanwheneventisvoicedonthischannel.
     *@paramonce{Boolean}(optional.Falsebydefault)Flagindicatingifthefunctionistobetriggeredonlyonce.
     *@returns{Object}Atokenobjectthatcenbeusedforunsubscribing. 
     */
    this.subscribe=function(topic,callback,once){
        'usestrict'
        if(!this.topics[topic]){
            this.topics[topic]=[[callback,once]];
        }else{
            this.topics[topic].push([callback,once]);
        }
        return{
            "topic":topic,
            "callback":callback
        };
    };
    /**
     *Allowslistenercodetounsubscribefromachannel
     *@public
     *@function
     *@paramtoken{Object}Atokenobjectthatwasreturnedby`subscribe`method
     */
    this.unsubscribe=function(token){
        if(this.topics[token.topic]){
            varcurrentTopic=this.topics[token.topic];
            
            for(vari=0,l=currentTopic.length;i<l;i++){
                if(currentTopic[i]&&currentTopic[i][0]===token.callback){
                    currentTopic.splice(i,1);
                }
            }
        }
    }
}

///Returnsfront,backand"decor"colorsderivedfromelement(asjQueryobj)
functiongetColors($e){
    vartmp
    ,undef
    ,frontcolor=$e.css('color')
    ,backcolor
    ,e=$e[0];
    
    vartoOfDOM=false;
    while(e&&!backcolor&&!toOfDOM){
        try{
            tmp=$(e).css('background-color');
        }catch(ex){
            tmp='transparent';
        }
        if(tmp!=='transparent'&&tmp!=='rgba(0,0,0,0)'){
            backcolor=tmp;
        }
        toOfDOM=e.body;
        e=e.parentNode;
    }

    varrgbaregex=/rgb[a]*\((\d+),\s*(\d+),\s*(\d+)///modernbrowsers
    ,hexregex=/#([AaBbCcDdEeFf\d]{2})([AaBbCcDdEeFf\d]{2})([AaBbCcDdEeFf\d]{2})///IE8andless.
    ,frontcolorcomponents;

    //DecomposingFrontcolorintoR,G,Bints
    tmp=undef;
    tmp=frontcolor.match(rgbaregex);
    if(tmp){
        frontcolorcomponents={'r':parseInt(tmp[1],10),'g':parseInt(tmp[2],10),'b':parseInt(tmp[3],10)};
    }else{
        tmp=frontcolor.match(hexregex);
        if(tmp){
            frontcolorcomponents={'r':parseInt(tmp[1],16),'g':parseInt(tmp[2],16),'b':parseInt(tmp[3],16)};
        }
    }
//     if(!frontcolorcomponents){
//         frontcolorcomponents={'r':255,'g':255,'b':255}
//     }

    varbackcolorcomponents
    //DecomposingbackcolorintoR,G,Bints
    if(!backcolor){
        //HIghlyunlikelysincethismeansthatnobackgroundstylingwasappliedtoanyelementfromheretotopofdom.
        //we'llpickupbackcolorfromfrontcolor
        if(frontcolorcomponents){
            if(Math.max.apply(null,[frontcolorcomponents.r,frontcolorcomponents.g,frontcolorcomponents.b])>127){
                backcolorcomponents={'r':0,'g':0,'b':0};
            }else{
                backcolorcomponents={'r':255,'g':255,'b':255};
            }
        }else{
            //arg!!!frontcolorisinformatwedon'tunderstand(hsl,namedcolors)
            //Let'sjustgowithwhitebackground.
            backcolorcomponents={'r':255,'g':255,'b':255};
        }
    }else{
        tmp=undef;
        tmp=backcolor.match(rgbaregex);
        if(tmp){
            backcolorcomponents={'r':parseInt(tmp[1],10),'g':parseInt(tmp[2],10),'b':parseInt(tmp[3],10)};
        }else{
            tmp=backcolor.match(hexregex);
            if(tmp){
                backcolorcomponents={'r':parseInt(tmp[1],16),'g':parseInt(tmp[2],16),'b':parseInt(tmp[3],16)};
            }
        }
//         if(!backcolorcomponents){
//             backcolorcomponents={'r':0,'g':0,'b':0}
//         }
    }
    
    //DerivingDecorcolor
    //THisisLAZY!!!!BetterwaywouldbetouseHSLandadjustluminocity.However,thatcouldbeanoverkill.
    
    vartoRGBfn=function(o){return'rgb('+[o.r,o.g,o.b].join(',')+')'}
    ,decorcolorcomponents
    ,frontcolorbrightness
    ,adjusted;
    
    if(frontcolorcomponents&&backcolorcomponents){
        varbackcolorbrightness=Math.max.apply(null,[frontcolorcomponents.r,frontcolorcomponents.g,frontcolorcomponents.b]);
        
        frontcolorbrightness=Math.max.apply(null,[backcolorcomponents.r,backcolorcomponents.g,backcolorcomponents.b]);
        adjusted=Math.round(frontcolorbrightness+(-1*(frontcolorbrightness-backcolorbrightness)*0.75));//"dimming"thedifferencebetweenpenandback.
        decorcolorcomponents={'r':adjusted,'g':adjusted,'b':adjusted};//alwaysshadeofgray
    }elseif(frontcolorcomponents){
        frontcolorbrightness=Math.max.apply(null,[frontcolorcomponents.r,frontcolorcomponents.g,frontcolorcomponents.b]);
        varpolarity=+1;
        if(frontcolorbrightness>127){
            polarity=-1;
        }
        //shiftingby25%(64pointsonRGBscale)
        adjusted=Math.round(frontcolorbrightness+(polarity*96));//"dimming"thepen'scolorby75%togetdecorcolor.
        decorcolorcomponents={'r':adjusted,'g':adjusted,'b':adjusted};//alwaysshadeofgray
    }else{
        decorcolorcomponents={'r':191,'g':191,'b':191};//alwaysshadeofgray
    }

    return{
        'color':frontcolor
        ,'background-color':backcolorcomponents?toRGBfn(backcolorcomponents):backcolor
        ,'decor-color':toRGBfn(decorcolorcomponents)
    };
}

functionVector(x,y){
    this.x=x;
    this.y=y;
    this.reverse=function(){
        returnnewthis.constructor(
            this.x*-1
            ,this.y*-1
        );
    };
    this._length=null;
    this.getLength=function(){
        if(!this._length){
            this._length=Math.sqrt(Math.pow(this.x,2)+Math.pow(this.y,2));
        }
        returnthis._length;
    };
    
    varpolarity=function(e){
        returnMath.round(e/Math.abs(e));
    };
    this.resizeTo=function(length){
        //proportionallychangesx,ysuchthatthehypotenuse(vectorlength)is=newlength
        if(this.x===0&&this.y===0){
            this._length=0;
        }elseif(this.x===0){
            this._length=length;
            this.y=length*polarity(this.y);
        }elseif(this.y===0){
            this._length=length;
            this.x=length*polarity(this.x);
        }else{
            varproportion=Math.abs(this.y/this.x)
                ,x=Math.sqrt(Math.pow(length,2)/(1+Math.pow(proportion,2)))
                ,y=proportion*x;
            this._length=length;
            this.x=x*polarity(this.x);
            this.y=y*polarity(this.y);
        }
        returnthis;
    };
    
    /**
     *Calculatestheanglebetween'this'vectorandanother.
     *@public
     *@function
     *@returns{Number}TheanglebetweenthetwovectorsasmeasuredinPI.
     */
    this.angleTo=function(vectorB){
        vardivisor=this.getLength()*vectorB.getLength();
        if(divisor===0){
            return0;
        }else{
            //JavaScriptfloatingpointmathisscrewedup.
            //becauseofit,thecoreoftheformulacan,onoccasion,havevalues
            //over1.0andbelow-1.0.
            returnMath.acos(
                Math.min(
                    Math.max(
                        (this.x*vectorB.x+this.y*vectorB.y)/divisor
                        ,-1.0
                    )
                    ,1.0
                )
            )/Math.PI;
        }
    };
}

functionPoint(x,y){
    this.x=x;
    this.y=y;
    
    this.getVectorToCoordinates=function(x,y){
        returnnewVector(x-this.x,y-this.y);
    };
    this.getVectorFromCoordinates=function(x,y){
        returnthis.getVectorToCoordinates(x,y).reverse();
    };
    this.getVectorToPoint=function(point){
        returnnewVector(point.x-this.x,point.y-this.y);
    };
    this.getVectorFromPoint=function(point){
        returnthis.getVectorToPoint(point).reverse();
    };
}

/*
 *Aboutdatastructure:
 *Wedon'tstore/dealwith"pictures"thissignaturecapturecodecaptures"vectors"
 *
 *Wedon'tstorebitmaps.Westore"strokes"asarraysofarrays.(Actually,arraysofobjectscontainingarraysofcoordinates.
 *
 *Stroke=mousedown+mousemoved*n(+mouseupbutwedon'trecordthatasthatwasthe"end/lackofmovement"indicator)
 *
 *Vectors=notclassicalvectorswherenumbersindicatedshiftrelativelastposition.Ourvectorsareactuallycoordinatesagainsttopleftofcanvas.
 *         wecouldcalctheclassicalvectors,butkeepingthetheactualcoordinatesallowsus(throughMath.max/min)
 *         tocalcthesizeofresultingdrawingveryquickly.Ifwewantclassicalvectorslater,wecanalwaysgettheminbackendcode.
 *
 *So,thedatastructure:
 *
 *vardata=[
 * {//strokestarts
 *     x:[101,98,57,43]//xpoints
 *     ,y:[1,23,65,87]//ypoints
 * }//strokeends
 * ,{//strokestarts
 *     x:[55,56,57,58]//xpoints
 *     ,y:[101,97,54,4]//ypoints
 * }//strokeends
 * ,{//strokeconsistingofjustadot
 *     x:[53]//xpoints
 *     ,y:[151]//ypoints
 * }//strokeends
 *]
 *
 *wedon'tcareorstorestrokewidth(it'scanvas-size-relative),color,shadowvalues.Thesecanbeadded/changedonwhimpost-capture.
 *
 */
functionDataEngine(storageObject,context,startStrokeFn,addToStrokeFn,endStrokeFn){
    this.data=storageObject;//weexpectthistobeaninstanceofArray
    this.context=context;

    if(storageObject.length){
        //wehavedatatorender
        varnumofstrokes=storageObject.length
        ,stroke
        ,numofpoints;
        
        for(vari=0;i<numofstrokes;i++){
            stroke=storageObject[i];
            numofpoints=stroke.x.length;
            startStrokeFn.call(context,stroke);
            for(varj=1;j<numofpoints;j++){
                addToStrokeFn.call(context,stroke,j);
            }
            endStrokeFn.call(context,stroke);
        }
    }

    this.changed=function(){};
    
    this.startStrokeFn=startStrokeFn;
    this.addToStrokeFn=addToStrokeFn;
    this.endStrokeFn=endStrokeFn;

    this.inStroke=false;
    
    this._lastPoint=null;
    this._stroke=null;
    this.startStroke=function(point){
        if(point&&typeof(point.x)=="number"&&typeof(point.y)=="number"){
            this._stroke={'x':[point.x],'y':[point.y]};
            this.data.push(this._stroke);
            this._lastPoint=point;
            this.inStroke=true;
            //'this'doesnotworksameinsidesetTimeout(
            varstroke=this._stroke
            ,fn=this.startStrokeFn
            ,context=this.context;
            setTimeout(
                //someIE'sdon'tsupportpassingargspersetTimeoutAPI.Havetocreateclosureeverytimeinstead.
                function(){fn.call(context,stroke)}
                ,3
            );
            returnpoint;
        }else{
            returnnull;
        }
    };
    //that"5"attheveryendofthisifisimportanttoexplain.
    //wedoNOTrenderlinksbetweentwocapturedpoints(inthemiddleofthestroke)ifthedistanceisshorterthanthatnumber.
    //notonlydoweNOTrenderit,wealsodoNOTcapture(add)theseintermediatepointstostorage.
    //whenclusteringoftheseistootight,itproducesnoiseontheline,which,becauseofsmoothing,makeslinestoocurvy.
    //maybe,later,wecanexposethisasaconfigurablesettingofsomesort.
    this.addToStroke=function(point){
        if(this.inStroke&&
            typeof(point.x)==="number"&&
            typeof(point.y)==="number"&&
            //calculatesabsoluteshiftindiagonalpixelsawayfromoriginalpoint
            (Math.abs(point.x-this._lastPoint.x)+Math.abs(point.y-this._lastPoint.y))>4
        ){
            varpositionInStroke=this._stroke.x.length;
            this._stroke.x.push(point.x);
            this._stroke.y.push(point.y);
            this._lastPoint=point;
            
            varstroke=this._stroke
            ,fn=this.addToStrokeFn
            ,context=this.context;
            setTimeout(
                //someIE'sdon'tsupportpassingargspersetTimeoutAPI.Havetocreateclosureeverytimeinstead.
                function(){fn.call(context,stroke,positionInStroke)}
                ,3
            );
            returnpoint;
        }else{
            returnnull;
        }
    };
    this.endStroke=function(){
        varc=this.inStroke;
        this.inStroke=false;
        this._lastPoint=null;
        if(c){
            varstroke=this._stroke
            ,fn=this.endStrokeFn//'this'doesnotworksameinsidesetTimeout(
            ,context=this.context
            ,changedfn=this.changed;
            setTimeout(
                //someIE'sdon'tsupportpassingargspersetTimeoutAPI.Havetocreateclosureeverytimeinstead.
                function(){
                    fn.call(context,stroke);
                    changedfn.call(context);
                }
                ,3
            );
            returntrue;
        }else{
            returnnull;
        }
    };
}

varbasicDot=function(ctx,x,y,size){
    varfillStyle=ctx.fillStyle;
    ctx.fillStyle=ctx.strokeStyle;
    ctx.fillRect(x+size/-2,y+size/-2,size,size);
    ctx.fillStyle=fillStyle;
}
,basicLine=function(ctx,startx,starty,endx,endy){
    ctx.beginPath();
    ctx.moveTo(startx,starty);
    ctx.lineTo(endx,endy);
    ctx.closePath();
    ctx.stroke();
}
,basicCurve=function(ctx,startx,starty,endx,endy,cp1x,cp1y,cp2x,cp2y){
    ctx.beginPath();
    ctx.moveTo(startx,starty);
    ctx.bezierCurveTo(cp1x,cp1y,cp2x,cp2y,endx,endy);
    ctx.closePath();
    ctx.stroke();
}
,strokeStartCallback=function(stroke){
    //this=jSignatureClassinstance
    basicDot(this.canvasContext,stroke.x[0],stroke.y[0],this.settings.lineWidth);
}
,strokeAddCallback=function(stroke,positionInStroke){
    //this=jSignatureClassinstance

    //Becausewearefunkythisway,herewedrawTWOcurves.
    //1.POSSIBLY"thisline"-spanningfrompointrightbeforeus,tothislatestpoint.
    //2.POSSIBLY"priorcurve"-spanningfrom"latestpoint"totheonebeforeit.
    
    //Whyyouask?
    //longlines(oneswithmanypixelsbetweenthem)donotlookgoodwhentheyarepartofalargecurvystroke.
    //Youknow,thejaggedycrocodilespineinsteadofapretty,smoothcurve.Yuck!
    //Wewanttoapproximateprettycurvesin-placeofthoseuglylines.
    //Toapproximateaverynicecurveweneedtoknowthedirectionoflinebeforeandafter.
    //Hence,onlonglinesweactuallywaitforanotherpointbeyondittocomebackfrom
    //mousemovedbeforewedrawthiscurve.
    
    //Sofor"priorcurve"tobecalc'edweneed4points
    // A,B,C,D(weareonDnow,Ais3pointsinthepast.)
    //and3lines:
    // pre-line(frompointsAtoB),
    // thisline(frompointsBtoC),(wecallit"this"becauseifitwasnotyet,it'stheonlyonewecandrawforsure.)
    // post-line(frompointsCtoD)(eventhroughDpointis'current'wedon'tknowhowwecandrawityet)
    //
    //Well,actually,wedon'tneedto*know*thepointA,justthevectorA->B
    varCpoint=newPoint(stroke.x[positionInStroke-1],stroke.y[positionInStroke-1])
        ,Dpoint=newPoint(stroke.x[positionInStroke],stroke.y[positionInStroke])
        ,CDvector=Cpoint.getVectorToPoint(Dpoint);
        
    //Again,wehaveachanceheretodrawTWOthings:
    // BCCurve(onlyifit'slong,becauseifitwasshort,itwasdrawnbypreviouscallback)and
    // CDLine(onlyifit'sshort)
    
    //So,let'sstartwithBCcurve.
    //ifthereisonly2pointsinstrokearray,wedon'thave"history"longenoughtohavepointB,letalonepointA.
    //FallingthroughtodrawinglineCDisproper,asthat'stheonlylinewehavepointsfor.
    if(positionInStroke>1){
        //weareherewhenthereareatleast3pointsinstrokearray.
        varBpoint=newPoint(stroke.x[positionInStroke-2],stroke.y[positionInStroke-2])
        ,BCvector=Bpoint.getVectorToPoint(Cpoint)
        ,ABvector;
        if(BCvector.getLength()>this.lineCurveThreshold){
            //Yey!Prettycurves,herewecome!
            if(positionInStroke>2){
                //weareherewhenatleast4pointsinstrokearray.
                ABvector=(newPoint(stroke.x[positionInStroke-3],stroke.y[positionInStroke-3])).getVectorToPoint(Bpoint);
            }else{
                ABvector=newVector(0,0);
            }

            varminlenfraction=0.05
            ,maxlen=BCvector.getLength()*0.35
            ,ABCangle=BCvector.angleTo(ABvector.reverse())
            ,BCDangle=CDvector.angleTo(BCvector.reverse())
            ,BCP1vector=newVector(ABvector.x+BCvector.x,ABvector.y+BCvector.y).resizeTo(
                Math.max(minlenfraction,ABCangle)*maxlen
            )
            ,CCP2vector=(newVector(BCvector.x+CDvector.x,BCvector.y+CDvector.y)).reverse().resizeTo(
                Math.max(minlenfraction,BCDangle)*maxlen
            );
            
            basicCurve(
                this.canvasContext
                ,Bpoint.x
                ,Bpoint.y
                ,Cpoint.x
                ,Cpoint.y
                ,Bpoint.x+BCP1vector.x
                ,Bpoint.y+BCP1vector.y
                ,Cpoint.x+CCP2vector.x
                ,Cpoint.y+CCP2vector.y
            );
        }
    }
    if(CDvector.getLength()<=this.lineCurveThreshold){
        basicLine(
            this.canvasContext
            ,Cpoint.x
            ,Cpoint.y
            ,Dpoint.x
            ,Dpoint.y
        );
    }
}
,strokeEndCallback=function(stroke){
    //this=jSignatureClassinstance

    //HerewetidyupthingsleftunfinishedinlaststrokeAddCallbackrun.

    //What'sPOTENTIALLYleftunfinishedthereisthecurvebetweenthelastpoints
    //inthestroke,ifthelenofthatlineismorethanlineCurveThreshold
    //IfthelastlinewasshorterthanlineCurveThreshold,itwasdrawnthere,andthere
    //isnothingforusheretodo.
    //Wecanalsobecalledwhenthereisonlyonepointinthestroke(meaning,the
    //strokewasjustadot),inwhichcase,again,thereisnothingforustodo.
                
    //Sofor"thiscurve"tobecalc'edweneed3points
    // A,B,C
    //and2lines:
    // pre-line(frompointsAtoB),
    // thisline(frompointsBtoC)
    //Well,actually,wedon'tneedto*know*thepointA,justthevectorA->B
    //so,wereallyneedpointsB,CandABvector.
    varpositionInStroke=stroke.x.length-1;
    
    if(positionInStroke>0){
        //thereareatleast2pointsinthestroke.weareinbusiness.
        varCpoint=newPoint(stroke.x[positionInStroke],stroke.y[positionInStroke])
            ,Bpoint=newPoint(stroke.x[positionInStroke-1],stroke.y[positionInStroke-1])
            ,BCvector=Bpoint.getVectorToPoint(Cpoint)
            ,ABvector;
        if(BCvector.getLength()>this.lineCurveThreshold){
            //yep.Thisonewasleftundrawninpriorcallback.Havetodrawitnow.
            if(positionInStroke>1){
                //wehaveatleast3elemsinstroke
                ABvector=(newPoint(stroke.x[positionInStroke-2],stroke.y[positionInStroke-2])).getVectorToPoint(Bpoint);
                varBCP1vector=newVector(ABvector.x+BCvector.x,ABvector.y+BCvector.y).resizeTo(BCvector.getLength()/2);
                basicCurve(
                    this.canvasContext
                    ,Bpoint.x
                    ,Bpoint.y
                    ,Cpoint.x
                    ,Cpoint.y
                    ,Bpoint.x+BCP1vector.x
                    ,Bpoint.y+BCP1vector.y
                    ,Cpoint.x
                    ,Cpoint.y
                );
            }else{
                //SincethereisnoABleg,thereisnocurvetodraw.Thislineisstill"long"butnocurve.
                basicLine(
                    this.canvasContext
                    ,Bpoint.x
                    ,Bpoint.y
                    ,Cpoint.x
                    ,Cpoint.y
                );
            }
        }
    }
}


/*
vargetDataStats=function(){
    varstrokecnt=strokes.length
        ,stroke
        ,pointid
        ,pointcnt
        ,x,y
        ,maxX=Number.NEGATIVE_INFINITY
        ,maxY=Number.NEGATIVE_INFINITY
        ,minX=Number.POSITIVE_INFINITY
        ,minY=Number.POSITIVE_INFINITY
    for(strokeid=0;strokeid<strokecnt;strokeid++){
        stroke=strokes[strokeid]
        pointcnt=stroke.length
        for(pointid=0;pointid<pointcnt;pointid++){
            x=stroke.x[pointid]
            y=stroke.y[pointid]
            if(x>maxX){
                maxX=x
            }elseif(x<minX){
                minX=x
            }
            if(y>maxY){
                maxY=y
            }elseif(y<minY){
                minY=y
            }
        }
    }
    return{'maxX':maxX,'minX':minX,'maxY':maxY,'minY':minY}
}
*/

functionconditionallyLinkCanvasResizeToWindowResize(jSignatureInstance,settingsWidth,apinamespace,globalEvents){
    'usestrict'
    if(settingsWidth==='ratio'||settingsWidth.split('')[settingsWidth.length-1]==='%'){
        
        this.eventTokens[apinamespace+'.parentresized']=globalEvents.subscribe(
            apinamespace+'.parentresized'
            ,(function(eventTokens,$parent,originalParentWidth,sizeRatio){
                'usestrict'

                returnfunction(){
                    'usestrict'

                    varw=$parent.width();
                    if(w!==originalParentWidth){
                    
                        //UNsubscribingthisparticularinstanceofsignaturepadonly.
                        //thereisaseparate`eventTokens`pereachinstanceofsignaturepad
                        for(varkeyineventTokens){
                            if(eventTokens.hasOwnProperty(key)){
                                globalEvents.unsubscribe(eventTokens[key]);
                                deleteeventTokens[key];
                            }
                        }

                        varsettings=jSignatureInstance.settings;
                        jSignatureInstance.$parent.children().remove();
                        for(varkeyinjSignatureInstance){
                            if(jSignatureInstance.hasOwnProperty(key)){
                                deletejSignatureInstance[key];
                            }
                        }
                        
                        //scaledatatonewsignaturepadsize
                        settings.data=(function(data,scale){
                            varnewData=[];
                            varo,i,l,j,m,stroke;
                            for(i=0,l=data.length;i<l;i++){
                                stroke=data[i];
                                
                                o={'x':[],'y':[]};
                                
                                for(j=0,m=stroke.x.length;j<m;j++){
                                    o.x.push(stroke.x[j]*scale);
                                    o.y.push(stroke.y[j]*scale);
                                }
                            
                                newData.push(o);
                            }
                            returnnewData;
                        })(
                            settings.data
                            ,w*1.0/originalParentWidth
                        )
                        
                        $parent[apinamespace](settings);
                    }
                }
            })(
                this.eventTokens
                ,this.$parent
                ,this.$parent.width()
                ,this.canvas.width*1.0/this.canvas.height
            )
        )
    }
};


functionjSignatureClass(parent,options,instanceExtensions){

    var$parent=this.$parent=$(parent)
    ,eventTokens=this.eventTokens={}
    ,events=this.events=newPubSubClass(this)
    ,globalEvents=$.fn[apinamespace]('globalEvents')
    ,settings={
        'width':'ratio'
        ,'height':'ratio'
        ,'sizeRatio':4//onlyusedwhenheight='ratio'
        ,'color':'#000'
        ,'background-color':'#fff'
        ,'decor-color':'#eee'
        ,'show-stroke':true
        ,'lineWidth':0
        ,'minFatFingerCompensation':-10
        ,'showUndoButton':false
        ,'readOnly':false
        ,'data':[]
    };
    
    $.extend(settings,getColors($parent));
    if(options){
        $.extend(settings,options);
    }
    this.settings=settings;

    for(varextensionNameininstanceExtensions){
        if(instanceExtensions.hasOwnProperty(extensionName)){
            instanceExtensions[extensionName].call(this,extensionName);
        }
    }

    this.events.publish(apinamespace+'.initializing');

    //these,whenenabled,willhoverabovethesigarea.HenceweappendthemtoDOMbeforecanvas.
    this.$controlbarUpper=(function(){
        varcontrolbarstyle='padding:0!important;margin:0!important;'+
            'width:100%!important;height:0!important;-ms-touch-action:none;touch-action:none;'+
            'margin-top:-1em!important;margin-bottom:1em!important;';
        return$('<divstyle="'+controlbarstyle+'"></div>').appendTo($parent);
    })();

    this.isCanvasEmulator=false;//willbeflippedbyinitializerwhenneeded.
    varcanvas=this.canvas=this.initializeCanvas(settings)
    ,$canvas=$(canvas);

    this.$controlbarLower=(function(){
        varcontrolbarstyle='padding:0!important;margin:0!important;'+
            'width:100%!important;height:0!important;-ms-touch-action:none;touch-action:none;'+
            'margin-top:-1.5em!important;margin-bottom:1.5em!important;position:relative;';
        return$('<divstyle="'+controlbarstyle+'"></div>').appendTo($parent);
    })();

    this.canvasContext=canvas.getContext("2d");

    //MostofourexposedAPIwillbelookingforthis:
    $canvas.data(apinamespace+'.this',this);

    settings.lineWidth=(function(defaultLineWidth,canvasWidth){
        if(!defaultLineWidth){
            returnMath.max(
                Math.round(canvasWidth/400)/*+1pixelforeveryextra300pxofwidth.*/
                ,2/*minimumlinewidth*/
            );
        }else{
            returndefaultLineWidth;
        }
    })(settings.lineWidth,canvas.width);

    this.lineCurveThreshold=settings.lineWidth*3;

    //Addcustomclassifdefined
    if(settings.cssclass&&$.trim(settings.cssclass)!=""){
        $canvas.addClass(settings.cssclass);
    }

    //usedforshiftingthedrawingpointupontouchdevices,soonecanseethedrawingabovethefinger.
    this.fatFingerCompensation=0;

    varmovementHandlers=(function(jSignatureInstance){

        //================================
        //mousedown,move,uphandlers:

        //shifts-adjustmentvaluesinviewportpixelsdrivedfrompositionofcanvasonthepage
        varshiftX
        ,shiftY
        ,setStartValues=function(){
            vartos=$(jSignatureInstance.canvas).offset()
            shiftX=tos.left*-1
            shiftY=tos.top*-1
        }
        ,getPointFromEvent=function(e){
            varfirstEvent=(e.changedTouches&&e.changedTouches.length>0?e.changedTouches[0]:e);
            //AlldevicesitriedreportcorrectcoordinatesinpageX,Y
            //AndroidChrome2.3.x,3.1,3.2.,OperaMobile, safariiOS4.x,
            //Windows:Chrome,FF,IE9,Safari
            //NoneofthatscrollshiftcalcvsscreenXYothersigsdoisneeded.
            //...oh,yeah,the"fatFinger.."isfortabletssothatpeopleseewhattheydraw.
            returnnewPoint(
                Math.round(firstEvent.pageX+shiftX)
                ,Math.round(firstEvent.pageY+shiftY)+jSignatureInstance.fatFingerCompensation
            );
        }
        ,timer=newKickTimerClass(
            750
            ,function(){jSignatureInstance.dataEngine.endStroke();}
        );

        this.drawEndHandler=function(e){
            if(!jSignatureInstance.settings.readOnly){
                try{e.preventDefault();}catch(ex){}
                timer.clear();
                jSignatureInstance.dataEngine.endStroke();
            }
        };
        this.drawStartHandler=function(e){
            if(!jSignatureInstance.settings.readOnly){
                e.preventDefault();
                //forperformancewecachetheoffsets
                //werecalctheseonlyatthebeginningthestroke        
                setStartValues();
                jSignatureInstance.dataEngine.startStroke(getPointFromEvent(e));
                timer.kick();
            }
        };
        this.drawMoveHandler=function(e){
            if(!jSignatureInstance.settings.readOnly){
                e.preventDefault();
                if(!jSignatureInstance.dataEngine.inStroke){
                    return;
                }
                jSignatureInstance.dataEngine.addToStroke(getPointFromEvent(e));
                timer.kick();
            }
        };

        returnthis;

    }).call({},this)

    //
    //================================

    ;(function(drawEndHandler,drawStartHandler,drawMoveHandler){
        varcanvas=this.canvas
        ,$canvas=$(canvas)
        ,undef;
        if(this.isCanvasEmulator){
            $canvas.bind('mousemove.'+apinamespace,drawMoveHandler);
            $canvas.bind('mouseup.'+apinamespace,drawEndHandler);
            $canvas.bind('mousedown.'+apinamespace,drawStartHandler);
        }else{
            canvas.addEventListener('touchstart',function(e){
                canvas.onmousedown=canvas.onmouseup=canvas.onmousemove=undef;

                this.fatFingerCompensation=(
                    settings.minFatFingerCompensation&&
                    settings.lineWidth*-3>settings.minFatFingerCompensation
                )?settings.lineWidth*-3:settings.minFatFingerCompensation;

                drawStartHandler(e);

                canvas.addEventListener('touchend',drawEndHandler);
                canvas.addEventListener('touchstart',drawStartHandler);
                canvas.addEventListener('touchmove',drawMoveHandler);
            });
            canvas.addEventListener('mousedown',function(e){
                canvas.ontouchstart=canvas.ontouchend=canvas.ontouchmove=undef;

                drawStartHandler(e);

                canvas.addEventListener('mousedown',drawStartHandler);
                canvas.addEventListener('mouseup',drawEndHandler);
                canvas.addEventListener('mousemove',drawMoveHandler);
            });
            if(window.navigator.msPointerEnabled){
                canvas.onmspointerdown=drawStartHandler;
                canvas.onmspointerup=drawEndHandler;
                canvas.onmspointermove=drawMoveHandler;
            }
        }
    }).call(
        this
        ,movementHandlers.drawEndHandler
        ,movementHandlers.drawStartHandler
        ,movementHandlers.drawMoveHandler
    )

    //=========================================
    //variouseventhandlers

    //onmouseout+mouseupcanvasdidnotknowthatmouseUPfired.ContinuedtodrawdespitemouseUP.
    //itisbettrthan
    //$canvas.bind('mouseout',drawEndHandler)
    //becausewedon'twanttobreakthestrokewhereuseraccidentallygetsousideandwantstogetbackinquickly.
    eventTokens[apinamespace+'.windowmouseup']=globalEvents.subscribe(
        apinamespace+'.windowmouseup'
        ,movementHandlers.drawEndHandler
    );

    this.events.publish(apinamespace+'.attachingEventHandlers');

    //Ifwehaveproportionalwidth,wesignuptoeventsbroadcasting"windowresized"andcheckingif
    //parent'swidthchanged.Ifso,we(1)extractsettings+datafromcurrentsignaturepad,
    //(2)removesignaturepadfromparent,and(3)reinitnewsignaturepadatnewsizewithsamesettings,(rescaled)data.
    conditionallyLinkCanvasResizeToWindowResize.call(
        this
        ,this
        ,settings.width.toString(10)
        ,apinamespace,globalEvents
    );
    
    //endofeventhandlers.
    //===============================

    this.resetCanvas(settings.data);

    //resetCanvasrendersthedataonthescreenandfiresONE"change"event
    //ifthereisdata.Ifyouhavecontrolsthatrelyon"change"firing
    //attachthemtosomethingthatrunsbeforethis.resetCanvas,like
    //apinamespace+'.attachingEventHandlers'thatfiresabithigher.
    this.events.publish(apinamespace+'.initialized');

    returnthis;
}//endofinitBase

//=========================================================================
//jSignatureClass'smethodsandsupportingfn's

jSignatureClass.prototype.resetCanvas=function(data,dontClear){
    varcanvas=this.canvas
    ,settings=this.settings
    ,ctx=this.canvasContext
    ,isCanvasEmulator=this.isCanvasEmulator
    ,cw=canvas.width
    ,ch=canvas.height;
    
    //preparingcolors,drawingarea
    if(!dontClear){
        ctx.clearRect(0,0,cw+30,ch+30);
    }

    ctx.shadowColor=ctx.fillStyle=settings['background-color']
    if(isCanvasEmulator){
        //FLashCanvasfillswithBlackbydefault,coveringuptheparentdiv'sbackground
        //hencewerefill
        ctx.fillRect(0,0,cw+30,ch+30);
    }

    ctx.lineWidth=Math.ceil(parseInt(settings.lineWidth,10));
    ctx.lineCap=ctx.lineJoin="round";
    
    //signatureline
    if(null!=settings['decor-color']&&settings['show-stroke']){
        ctx.strokeStyle=settings['decor-color'];
        ctx.shadowOffsetX=0;
        ctx.shadowOffsetY=0;
        varlineoffset=Math.round(ch/5);
        basicLine(ctx,lineoffset*1.5,ch-lineoffset,cw-(lineoffset*1.5),ch-lineoffset);
    }
    ctx.strokeStyle=settings.color;

    if(!isCanvasEmulator){
        ctx.shadowColor=ctx.strokeStyle;
        ctx.shadowOffsetX=ctx.lineWidth*0.5;
        ctx.shadowOffsetY=ctx.lineWidth*-0.6;
        ctx.shadowBlur=0;
    }
    
    //settingupnewdataEngine

    if(!data){data=[];}
    
    vardataEngine=this.dataEngine=newDataEngine(
        data
        ,this
        ,strokeStartCallback
        ,strokeAddCallback
        ,strokeEndCallback
    );

    settings.data=data;//onwindowresizehandlerusesit,ithink.
    $(canvas).data(apinamespace+'.data',data)
        .data(apinamespace+'.settings',settings);

    //wefire"change"eventoneverychangeindata.
    //settingthisup:
    dataEngine.changed=(function(target,events,apinamespace){
        'usestrict'
        returnfunction(){
            events.publish(apinamespace+'.change');
            target.trigger('change');
        }
    })(this.$parent,this.events,apinamespace);
    //let'striggerchangeonalldatareloads
    dataEngine.changed();

    //importfilterswillbepassingthisbackasindicationof"werendered"
    returntrue;
};

functioninitializeCanvasEmulator(canvas){
    if(canvas.getContext){
        returnfalse;
    }else{
        //forcaseswhenjSignature,FlashCanvasisinserted
        //fromonewindowintoanother(childiframe)
        //'window'and'FlashCanvas'maybestuckbehind
        //inthatotherparentwindow.
        //weneedtofindit
        varwindow=canvas.ownerDocument.parentWindow;
        varFC=window.FlashCanvas?
            canvas.ownerDocument.parentWindow.FlashCanvas:
            (
                typeofFlashCanvas==="undefined"?
                undefined:
                FlashCanvas
            );

        if(FC){
            canvas=FC.initElement(canvas);
            
            varzoom=1;
            //FlashCanvasusesflashwhichhasthisannoyinghabitofNOTscalingwithpagezoom.
            //Itmatchespixel-to-pixeltoscreeninstead.
            //SincewearetargetingONLYIE7,8withFlashCanvas,wewilltestthezoomonlytheIE8,IE7way
            if(window&&window.screen&&window.screen.deviceXDPI&&window.screen.logicalXDPI){
                zoom=window.screen.deviceXDPI*1.0/window.screen.logicalXDPI;
            }
            if(zoom!==1){
                try{
                    //WeeffectivelyabusethebrokennessofFlashCanvasandforcetheflashrenderingsurfaceto
                    //occupylargerpixeldimensionsthanthewrapping,scaledupDIVandCanvaselems.
                    $(canvas).children('object').get(0).resize(Math.ceil(canvas.width*zoom),Math.ceil(canvas.height*zoom));
                    //Andbyapplying"scale"transformationwecantalk"browserpixels"toFlashCanvas
                    //andhaveittranslatethe"browserpixels"to"screenpixels"
                    canvas.getContext('2d').scale(zoom,zoom);
                    //Notetoself:don'treuseCanvaselement.Repeated"scale"arecumulative.
                }catch(ex){}
            }
            returntrue;
        }else{
            thrownewError("Canvaselementdoesnotsupport2dcontext.jSignaturecannotproceed.");
        }
    }

}

jSignatureClass.prototype.initializeCanvas=function(settings){
    //===========
    //Init+Sizingcode

    varcanvas=document.createElement('canvas')
    ,$canvas=$(canvas);

    //Wecannotworkwithcirculardependency
    if(settings.width===settings.height&&settings.height==='ratio'){
        settings.width='100%';
    }

    $canvas.css({
        'margin':0,
        'padding':0,
        'border':'none',
        'height':settings.height==='ratio'||!settings.height?1:settings.height.toString(10),
        'width':settings.width==='ratio'||!settings.width?1:settings.width.toString(10),
        '-ms-touch-action':'none',
        'touch-action':'none',
        'background-color':settings['background-color'],
    });

    $canvas.appendTo(this.$parent);

    //wecouldnotdothisuntilcanvasisrendered(appendedtoDOM)
    if(settings.height==='ratio'){
        $canvas.css(
            'height'
            ,Math.round($canvas.width()/settings.sizeRatio)
        );
    }elseif(settings.width==='ratio'){
        $canvas.css(
            'width'
            ,Math.round($canvas.height()*settings.sizeRatio)
        );
    }

    $canvas.addClass(apinamespace);

    //canvas'sdrawingarearesolutionisindependentfromcanvas'ssize.
    //pixelsarejustscaledupordownwheninternalresolutiondoesnot
    //matchexternalsize.So...

    canvas.width=$canvas.width();
    canvas.height=$canvas.height();
    
    //SpecialcaseSizingcode

    this.isCanvasEmulator=initializeCanvasEmulator(canvas);

    //EndofSizingCode
    //===========

    //normallyselectpreventerwouldbeshort,but
    //CanvasemulatoronIEdoesNOTprovidevalueforEvent.Hencethisconvolutedline.
    canvas.onselectstart=function(e){if(e&&e.preventDefault){e.preventDefault()};if(e&&e.stopPropagation){e.stopPropagation()};returnfalse;};

    returncanvas;
}


varGlobalJSignatureObjectInitializer=function(window){

    varglobalEvents=newPubSubClass();
    
    //common"windowresized"eventlistener.
    //jSignatureinstanceswillsubscribetothischanel.
    //toresizethemselveswhenneeded.
    ;(function(globalEvents,apinamespace,$,window){
        'usestrict'

        varresizetimer
        ,runner=function(){
            globalEvents.publish(
                apinamespace+'.parentresized'
            )
        };

        //jSignatureknowshowtoresizeitscontentwhenitsparentisresized
        //windowresizeistheonlywaywecancatchresizeeventsthough...
        $(window).bind('resize.'+apinamespace,function(){
            if(resizetimer){
                clearTimeout(resizetimer);
            }
            resizetimer=setTimeout(
                runner
                ,500
            );
        })
        //whenmouseexistscanvaselementand"up"soutside,wecannotcatchitwith
        //callbacksattachedtocanvas.Thiscatchesitoutside.
        .bind('mouseup.'+apinamespace,function(e){
            globalEvents.publish(
                apinamespace+'.windowmouseup'
            )
        });

    })(globalEvents,apinamespace,$,window)

    varjSignatureInstanceExtensions={
        /*
        'exampleExtension':function(extensionName){
            //wearecalledveryearlyininstance'slife.
            //rightafterthesettingsareresolvedand
            //jSignatureInstance.eventsiscreated
            //andrightbeforefirst("jSignature.initializing")eventiscalled.
            //Youdon'treallyneedtomanupilate
            //jSignatureInstancedirectly,justattach
            //abunchofeventstojSignatureInstance.events
            //(lookatthesourceofjSignatureClasstoseewhenthesefire)
            //andyourspecialpiecesofcodewillattachbythemselves.

            //thisfunctionrunseverytimeanewinstanceissetup.
            //thismeanseveryvaryoucreatewillliveonlyforoneinstance
            //unlessyouattachittosomethingoutside,like"window."
            //andpickituplaterfromthere.

            //whenglobalEvents'eventsfire,'this'isglobalEventsobject
            //whenjSignatureInstance'seventsfire,'this'isjSignatureInstance

            //Here,
            //this=isnewjSignatureClass'sinstance.

            //ThewayyouCOULDapprochsettingthisupis:
            //ifyouhavemultistepsetup,attacheventto"jSignature.initializing"
            //thatattachesothereventstobefiredfurtherlowertheinitstream.
            //Or,ifyouknowforsureyourelyononlyonejSignatureInstance'sevent,
            //justattachtoitdirectly

            this.events.subscribe(
                //nameoftheevent
                apinamespace+'.initializing'
                //eventhandlers,canpassargstoo,butinmajorityofcases,
                //'this'whichisjSignatureClassobjectinstancepointerisenoughtogetby.
                ,function(){
                    if(this.settings.hasOwnProperty('non-existentsettingcategory?')){
                        console.log(extensionName+'ishere')
                    }
                }
            )
        }
        */
    };

    varexportplugins={
        'default':function(data){returnthis.toDataURL()}
        ,'native':function(data){returndata}
        ,'image':function(data){
            /*this=canvaselem*/
            varimagestring=this.toDataURL();
            
            if(typeofimagestring==='string'&&
                imagestring.length>4&&
                imagestring.slice(0,5)==='data:'&&
                imagestring.indexOf(',')!==-1){
                
                varsplitterpos=imagestring.indexOf(',');

                return[
                    imagestring.slice(5,splitterpos)
                    ,imagestring.substr(splitterpos+1)
                ];
            }
            return[];
        }
    };

    //willbepartof"importplugins"
    function_renderImageOnCanvas(data,formattype,rerendercallable){
        'usestrict'
        //#1.DoNOTrelyonthis.NoworkyonIE
        //  (urlmaxlen+lackofbase64decoder+possiblyotherissues)
        //#2.ThisdoesNOTaffectwhatiscapturedas"signature"asfarasvectordatais
        //concerned.Thisistreatedsameas"signatureline"-i.e.completelyignored
        //theonlytimeyouseeimportedimagedataexportedisifyouexportasimage.

        //wedoNOTcallrerendercallablehere(unlikeinotherimportplugins)
        //becauseimportingimagedoesabsolutelynothingtotheunderlyingvectordatastorage
        //Thiscouldbeawayto"import"oldsignaturesstoredasimages
        //Thiscouldalsobeawaytoimportextradecorintosignaturearea.
        
        varimg=newImage()
        //this=CanvasDOMelem.NotjQueryobject.NotCanvas'sparentdiv.
        ,c=this;

        img.onload=function(){
            varctx=c.getContext("2d");
            varoldShadowColor=ctx.shadowColor;
            ctx.shadowColor="transparent";
            ctx.drawImage(
                img,0,0
                ,(img.width<c.width)?img.width:c.width
                ,(img.height<c.height)?img.height:c.height
            );
            ctx.shadowColor=oldShadowColor;
        };

        img.src='data:'+formattype+','+data;
    }

    varimportplugins={
        'native':function(data,formattype,rerendercallable){
            //weexpectdataasArrayofobjectsofarrayshere-whatever'default'EXPORTpluginspitsout.
            //returningTruthytoindicatewearegood,allupdated.
            rerendercallable(data);
        }
        ,'image':_renderImageOnCanvas
        ,'image/png;base64':_renderImageOnCanvas
        ,'image/jpeg;base64':_renderImageOnCanvas
        ,'image/jpg;base64':_renderImageOnCanvas
    };

    function_clearDrawingArea(data,dontClear){
        this.find('canvas.'+apinamespace)
            .add(this.filter('canvas.'+apinamespace))
            .data(apinamespace+'.this').resetCanvas(data,dontClear);
        returnthis;
    }

    function_setDrawingData(data,formattype){
        varundef;

        if(formattype===undef&&typeofdata==='string'&&data.substr(0,5)==='data:'){
            formattype=data.slice(5).split(',')[0];
            //5charsof"data:"+mimetypelen+1","char=allskipped.
            data=data.slice(6+formattype.length);
            if(formattype===data){
                return;
            }
        }

        var$canvas=this.find('canvas.'+apinamespace).add(this.filter('canvas.'+apinamespace));

        if(!importplugins.hasOwnProperty(formattype)){
            thrownewError(apinamespace+"isunabletofindimportpluginwithforformat'"+String(formattype)+"'");
        }elseif($canvas.length!==0){
            importplugins[formattype].call(
                $canvas[0]
                ,data
                ,formattype
                ,(function(jSignatureInstance){
                    returnfunction(){returnjSignatureInstance.resetCanvas.apply(jSignatureInstance,arguments)}
                })($canvas.data(apinamespace+'.this'))
            );
        }

        returnthis;
    }

    varelementIsOrphan=function(e){
        vartopOfDOM=false;
        e=e.parentNode;
        while(e&&!topOfDOM){
            topOfDOM=e.body;
            e=e.parentNode;
        }
        return!topOfDOM;
    }

    //Theseareexposedasmethodsunder$obj.jSignature('methodname',*args)
    varplugins={'export':exportplugins,'import':importplugins,'instance':jSignatureInstanceExtensions}
    ,methods={
        'init':function(options){
            returnthis.each(function(){
                if(!elementIsOrphan(this)){
                    newjSignatureClass(this,options,jSignatureInstanceExtensions);
                }
            })
        }
        ,'getSettings':function(){
            returnthis.find('canvas.'+apinamespace)
                .add(this.filter('canvas.'+apinamespace))
                .data(apinamespace+'.this').settings;
        }
        ,'isModified':function(){
            returnthis.find('canvas.'+apinamespace)
                .add(this.filter('canvas.'+apinamespace))
                .data(apinamespace+'.this')
                .dataEngine
                ._stroke!==null;
        }
        ,'updateSetting':function(param,val,forFuture){
            var$canvas=this.find('canvas.'+apinamespace)
                            .add(this.filter('canvas.'+apinamespace))
                            .data(apinamespace+'.this');
            $canvas.settings[param]=val;
            $canvas.resetCanvas((forFuture?null:$canvas.settings.data),true);
            return$canvas.settings[param];
        }
        //aroundsincev1
        ,'clear':_clearDrawingArea
        //wasmistakenlyintroducedinsteadof'clear'inv2
        ,'reset':_clearDrawingArea
        ,'addPlugin':function(pluginType,pluginName,callable){
            if(plugins.hasOwnProperty(pluginType)){
                plugins[pluginType][pluginName]=callable;
            }
            returnthis;
        }
        ,'listPlugins':function(pluginType){
            varanswer=[];
            if(plugins.hasOwnProperty(pluginType)){
                varo=plugins[pluginType];
                for(varkino){
                    if(o.hasOwnProperty(k)){
                        answer.push(k);
                    }
                }
            }
            returnanswer;
        }
        ,'getData':function(formattype){
            varundef,$canvas=this.find('canvas.'+apinamespace).add(this.filter('canvas.'+apinamespace));
            if(formattype===undef){
                formattype='default';
            }
            if($canvas.length!==0&&exportplugins.hasOwnProperty(formattype)){             
                returnexportplugins[formattype].call(
                    $canvas.get(0)//canvasdomelem
                    ,$canvas.data(apinamespace+'.data')//rawsignaturedataasarrayofobjectsofarrays
                    ,$canvas.data(apinamespace+'.settings')
                );
            }
        }
        //aroundsincev1.Tookonlyonearg-data-url-formattedstringwith(likelypngof)signatureimage
        ,'importData':_setDrawingData
        //wasmistakenlyintroducedinsteadof'importData'inv2
        ,'setData':_setDrawingData
        //thisisoneandsameinstanceforalljSignature.
        ,'globalEvents':function(){returnglobalEvents}
        ,'disable':function(){
            this.find("input").attr("disabled",1);
            this.find('canvas.'+apinamespace)
                .addClass("disabled")
                .data(apinamespace+'.this')
                .settings
                .readOnly=true;
        }
        ,'enable':function(){
            this.find("input").removeAttr("disabled");
            this.find('canvas.'+apinamespace)
                .removeClass("disabled")
                .data(apinamespace+'.this')
                .settings
                .readOnly=false;
        }
        //therewillbeaseparateoneforeachjSignatureinstance.
        ,'events':function(){
            returnthis.find('canvas.'+apinamespace)
                    .add(this.filter('canvas.'+apinamespace))
                    .data(apinamespace+'.this').events;
        }
    }//endofmethodsdeclaration.
    
    $.fn[apinamespace]=function(method){
        'usestrict'
        if(!method||typeofmethod==='object'){
            returnmethods.init.apply(this,arguments);
        }elseif(typeofmethod==='string'&&methods[method]){
            returnmethods[method].apply(this,Array.prototype.slice.call(arguments,1));
        }else{
            $.error('Method'+ String(method)+'doesnotexistonjQuery.'+apinamespace);
        }
    }

}//endofGlobalJSignatureObjectInitializer

GlobalJSignatureObjectInitializer(window)

})();
