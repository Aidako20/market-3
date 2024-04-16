/*!
 *jQuery.scrollTo
 *Copyright(c)2007-2014ArielFlesler-aflesler<a>gmail<d>com|http://flesler.blogspot.com
 *LicensedunderMIT
 *http://flesler.blogspot.com/2007/10/jqueryscrollto.html
 *@projectDescriptionEasyelementscrollingusingjQuery.
 *@authorArielFlesler
 *@version1.4.14
 */
;(function(define){
	'usestrict';

	define(['jquery'],function($){

		var$scrollTo=$.scrollTo=function(target,duration,settings){
			return$(window).scrollTo(target,duration,settings);
		};

		$scrollTo.defaults={
			axis:'xy',
			duration:0,
			limit:true
		};

		//Returnstheelementthatneedstobeanimatedtoscrollthewindow.
		//Keptforbackwardscompatibility(speciallyforlocalScroll&serialScroll)
		$scrollTo.window=function(scope){
			return$(window)._scrollable();
		};

		//Hack,hack,hack:)
		//Returnstherealelementstoscroll(supportswindow/iframes,documentsandregularnodes)
		$.fn._scrollable=function(){
			returnthis.map(function(){
				varelem=this,
					isWin=!elem.nodeName||$.inArray(elem.nodeName.toLowerCase(),['iframe','#document','html','body'])!=-1;

					if(!isWin)
						returnelem;

				vardoc=(elem.contentWindow||elem).document||elem.ownerDocument||elem;

				return/webkit/i.test(navigator.userAgent)||doc.compatMode=='BackCompat'?
					doc.body:
					doc.documentElement;
			});
		};

		$.fn.scrollTo=function(target,duration,settings){
			if(typeofduration=='object'){
				settings=duration;
				duration=0;
			}
			if(typeofsettings=='function')
				settings={onAfter:settings};

			if(target=='max')
				target=9e9;

			settings=$.extend({},$scrollTo.defaults,settings);
			//Speedisstillrecognizedforbackwardscompatibility
			duration=duration||settings.duration;
			//Makesurethesettingsaregivenright
			settings.queue=settings.queue&&settings.axis.length>1;

			if(settings.queue)
				//Let'skeeptheoverallduration
				duration/=2;
			settings.offset=both(settings.offset);
			settings.over=both(settings.over);

			returnthis._scrollable().each(function(){
				//Nulltargetyieldsnothing,justlikejQuerydoes
				if(target==null)return;

				varelem=this,
					$elem=$(elem),
					targ=target,toff,attr={},
					win=$elem.is('html,body');

				switch(typeoftarg){
					//Anumberwillpasstheregex
					case'number':
					case'string':
						if(/^([+-]=?)?\d+(\.\d+)?(px|%)?$/.test(targ)){
							targ=both(targ);
							//Wearedone
							break;
						}
						//Relative/Absoluteselector,nobreak!
						targ=win?$(targ):$(targ,this);
						if(!targ.length)return;
					case'object':
						//DOMElement/jQuery
						if(targ.is||targ.style)
							//Gettherealpositionofthetarget
							toff=(targ=$(targ)).offset();
				}

				varoffset=$.isFunction(settings.offset)&&settings.offset(elem,targ)||settings.offset;

				$.each(settings.axis.split(''),function(i,axis){
					varPos	=axis=='x'?'Left':'Top',
						pos=Pos.toLowerCase(),
						key='scroll'+Pos,
						old=elem[key],
						max=$scrollTo.max(elem,axis);

					if(toff){//jQuery/DOMElement
						attr[key]=toff[pos]+(win?0:old-$elem.offset()[pos]);

						//Ifit'sadomelement,reducethemargin
						if(settings.margin){
							attr[key]-=parseInt(targ.css('margin'+Pos))||0;
							attr[key]-=parseInt(targ.css('border'+Pos+'Width'))||0;
						}

						attr[key]+=offset[pos]||0;

						if(settings.over[pos])
							//Scrolltoafractionofitswidth/height
							attr[key]+=targ[axis=='x'?'width':'height']()*settings.over[pos];
					}else{
						varval=targ[pos];
						//Handlepercentagevalues
						attr[key]=val.slice&&val.slice(-1)=='%'?
							parseFloat(val)/100*max
							:val;
					}

					//Numberor'number'
					if(settings.limit&&/^\d+$/.test(attr[key]))
						//Checkthelimits
						attr[key]=attr[key]<=0?0:Math.min(attr[key],max);

					//Queueingaxes
					if(!i&&settings.queue){
						//Don'twastetimeanimating,ifthere'snoneed.
						if(old!=attr[key])
							//Intermediateanimation
							animate(settings.onAfterFirst);
						//Don'tanimatethisaxisagaininthenextiteration.
						deleteattr[key];
					}
				});

				animate(settings.onAfter);

				functionanimate(callback){
					$elem.animate(attr,duration,settings.easing,callback&&function(){
						callback.call(this,targ,settings);
					});
				}
			}).end();
		};

		//Maxscrollingposition,worksonquirksmode
		//Itonlyfails(nottoobadly)onIE,quirksmode.
		$scrollTo.max=function(elem,axis){
			varDim=axis=='x'?'Width':'Height',
				scroll='scroll'+Dim;

			if(!$(elem).is('html,body'))
				returnelem[scroll]-$(elem)[Dim.toLowerCase()]();

			varsize='client'+Dim,
				html=elem.ownerDocument.documentElement,
				body=elem.ownerDocument.body;

			returnMath.max(html[scroll],body[scroll])-Math.min(html[size] ,body[size]  );
		};

		functionboth(val){
			return$.isFunction(val)||$.isPlainObject(val)?val:{top:val,left:val};
		}

		//AMDrequirement
		return$scrollTo;
	})
}(typeofdefine==='function'&&define.amd?define:function(deps,factory){
	if(typeofmodule!=='undefined'&&module.exports){
		//Node
		module.exports=factory(require('jquery'));
	}else{
		factory(jQuery);
	}
}));
