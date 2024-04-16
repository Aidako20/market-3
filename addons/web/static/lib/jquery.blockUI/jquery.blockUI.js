/*!
 *jQueryblockUIplugin
 *Version2.70.0-2014.11.23
 *RequiresjQueryv1.7orlater
 *
 *Examplesat:http://malsup.com/jquery/block/
 *Copyright(c)2007-2013M.Alsup
 *DuallicensedundertheMITandGPLlicenses:
 *http://www.opensource.org/licenses/mit-license.php
 *http://www.gnu.org/licenses/gpl.html
 *
 *ThankstoAmir-HosseinSobhiforsomeexcellentcontributions!
 */

;(function(){
/*jshinteqeqeq:falsecurly:falselatedef:false*/
"usestrict";

	functionsetup($){
		$.fn._fadeIn=$.fn.fadeIn;

		varnoOp=$.noop||function(){};

		//thisbitistoensurewedon'tcallsetExpressionwhenweshouldn't(withextramuscletohandle
		//confusinguserAgentstringsonVista)
		varmsie=/MSIE/.test(navigator.userAgent);
		varie6 =/MSIE6.0/.test(navigator.userAgent)&&!/MSIE8.0/.test(navigator.userAgent);
		varmode=document.documentMode||0;
		varsetExpr=$.isFunction(document.createElement('div').style.setExpression);

		//global$methodsforblocking/unblockingtheentirepage
		$.blockUI  =function(opts){install(window,opts);};
		$.unblockUI=function(opts){remove(window,opts);};

		//conveniencemethodforquickgrowl-likenotifications (http://www.google.com/search?q=growl)
		$.growlUI=function(title,message,timeout,onClose){
			var$m=$('<divclass="growlUI"></div>');
			if(title)$m.append('<h1>'+title+'</h1>');
			if(message)$m.append('<h2>'+message+'</h2>');
			if(timeout===undefined)timeout=3000;

			//Addedbykonapun:Settimeoutto30secondsifthisgrowlismousedover,likenormaltoastnotifications
			varcallBlock=function(opts){
				opts=opts||{};

				$.blockUI({
					message:$m,
					fadeIn:typeofopts.fadeIn !=='undefined'?opts.fadeIn :700,
					fadeOut:typeofopts.fadeOut!=='undefined'?opts.fadeOut:1000,
					timeout:typeofopts.timeout!=='undefined'?opts.timeout:timeout,
					centerY:false,
					showOverlay:false,
					onUnblock:onClose,
					css:$.blockUI.defaults.growlCSS
				});
			};

			callBlock();
			varnonmousedOpacity=$m.css('opacity');
			$m.mouseover(function(){
				callBlock({
					fadeIn:0,
					timeout:30000
				});

				vardisplayBlock=$('.blockMsg');
				displayBlock.stop();//cancelfadeoutifithasstarted
				displayBlock.fadeTo(300,1);//makeiteasiertoreadthemessagebyremovingtransparency
			}).mouseout(function(){
				$('.blockMsg').fadeOut(1000);
			});
			//Endkonapunadditions
		};

		//pluginmethodforblockingelementcontent
		$.fn.block=function(opts){
			if(this[0]===window){
				$.blockUI(opts);
				returnthis;
			}
			varfullOpts=$.extend({},$.blockUI.defaults,opts||{});
			this.each(function(){
				var$el=$(this);
				if(fullOpts.ignoreIfBlocked&&$el.data('blockUI.isBlocked'))
					return;
				$el.unblock({fadeOut:0});
			});

			returnthis.each(function(){
				if($.css(this,'position')=='static'){
					this.style.position='relative';
					$(this).data('blockUI.static',true);
				}
				this.style.zoom=1;//force'hasLayout'inie
				install(this,opts);
			});
		};

		//pluginmethodforunblockingelementcontent
		$.fn.unblock=function(opts){
			if(this[0]===window){
				$.unblockUI(opts);
				returnthis;
			}
			returnthis.each(function(){
				remove(this,opts);
			});
		};

		$.blockUI.version=2.70;//2ndgenerationblockingatnoextracost!

		//overridetheseinyourcodetochangethedefaultbehaviorandstyle
		$.blockUI.defaults={
			//messagedisplayedwhenblocking(usenullfornomessage)
			message: '<h1>Pleasewait...</h1>',

			title:null,		//titlestring;onlyusedwhentheme==true
			draggable:true,	//onlyusedwhentheme==true(requiresjquery-ui.jstobeloaded)

			theme:false,//settotruetousewithjQueryUIthemes

			//stylesforthemessagewhenblocking;ifyouwishtodisable
			//theseanduseanexternalstylesheetthendothisinyourcode:
			//$.blockUI.defaults.css={};
			css:{
				padding:	0,
				margin:		0,
				width:		'30%',
				top:		'40%',
				left:		'35%',
				textAlign:	'center',
				color:		'#000',
				border:		'3pxsolid#aaa',
				backgroundColor:'#fff',
				cursor:		'wait'
			},

			//minimalstylesetusedwhenthemesareused
			themedCSS:{
				width:	'30%',
				top:	'40%',
				left:	'35%'
			},

			//stylesfortheoverlay
			overlayCSS: {
				backgroundColor:	'#000',
				opacity:			0.6,
				cursor:				'wait'
			},

			//styletoreplacewaitcursorbeforeunblockingtocorrectissue
			//oflingeringwaitcursor
			cursorReset:'default',

			//stylesappliedwhenusing$.growlUI
			growlCSS:{
				width:		'350px',
				top:		'10px',
				left:		'',
				right:		'10px',
				border:		'none',
				padding:	'5px',
				opacity:	0.6,
				cursor:		'default',
				color:		'#fff',
				backgroundColor:'#000',
				'-webkit-border-radius':'10px',
				'-moz-border-radius':	'10px',
				'border-radius':		'10px'
			},

			//IEissues:'about:blank'failsonHTTPSandjavascript:falseiss-l-o-w
			//(hattiptoJorgeH.N.deVasconcelos)
			/*jshintscripturl:true*/
			iframeSrc:/^https/i.test(window.location.href||'')?'javascript:false':'about:blank',

			//forceusageofiframeinnon-IEbrowsers(handyforblockingapplets)
			forceIframe:false,

			//z-indexfortheblockingoverlay
			baseZ:1000,

			//setthesetotruetohavethemessageautomaticallycentered
			centerX:true,//<--onlyeffectselementblocking(pageblockcontrolledviacssabove)
			centerY:true,

			//allowbodyelementtobestetchedinie6;thismakesblockinglookbetter
			//on"short"pages. disableifyouwishtopreventchangestothebodyheight
			allowBodyStretch:true,

			//enableifyouwantkeyandmouseeventstobedisabledforcontentthatisblocked
			bindEvents:true,

			//bedefaultblockUIwillsupresstabnavigationfromleavingblockingcontent
			//(ifbindEventsistrue)
			constrainTabKey:true,

			//fadeIntimeinmillis;setto0todisablefadeInonblock
			fadeIn: 200,

			//fadeOuttimeinmillis;setto0todisablefadeOutonunblock
			fadeOut: 400,

			//timeinmillistowaitbeforeauto-unblocking;setto0todisableauto-unblock
			timeout:0,

			//disableifyoudon'twanttoshowtheoverlay
			showOverlay:true,

			//iftrue,focuswillbeplacedinthefirstavailableinputfieldwhen
			//pageblocking
			focusInput:true,

            //elementsthatcanreceivefocus
            focusableElements:':input:enabled:visible',

			//suppressestheuseofoverlaystylesonFF/Linux(duetoperformanceissueswithopacity)
			//nolongerneededin2012
			//applyPlatformOpacityRules:true,

			//callbackmethodinvokedwhenfadeInhascompletedandblockingmessageisvisible
			onBlock:null,

			//callbackmethodinvokedwhenunblockinghascompleted;thecallbackis
			//passedtheelementthathasbeenunblocked(whichisthewindowobjectforpage
			//blocks)andtheoptionsthatwerepassedtotheunblockcall:
			//	onUnblock(element,options)
			onUnblock:null,

			//callbackmethodinvokedwhentheoverlayareaisclicked.
			//settingthiswillturnthecursortoapointer,otherwisecursordefinedinoverlayCsswillbeused.
			onOverlayClick:null,

			//don'task;ifyoureallymustknow:http://groups.google.com/group/jquery-en/browse_thread/thread/36640a8730503595/2f6a79a77a78e493#2f6a79a77a78e493
			quirksmodeOffsetHack:4,

			//classnameofthemessageblock
			blockMsgClass:'blockMsg',

			//ifitisalreadyblocked,thenignoreit(don'tunblockandreblock)
			ignoreIfBlocked:false
		};

		//privatedataandfunctionsfollow...

		varpageBlock=null;
		varpageBlockEls=[];

		functioninstall(el,opts){
			varcss,themedCSS;
			varfull=(el==window);
			varmsg=(opts&&opts.message!==undefined?opts.message:undefined);
			opts=$.extend({},$.blockUI.defaults,opts||{});

			if(opts.ignoreIfBlocked&&$(el).data('blockUI.isBlocked'))
				return;

			opts.overlayCSS=$.extend({},$.blockUI.defaults.overlayCSS,opts.overlayCSS||{});
			css=$.extend({},$.blockUI.defaults.css,opts.css||{});
			if(opts.onOverlayClick)
				opts.overlayCSS.cursor='pointer';

			themedCSS=$.extend({},$.blockUI.defaults.themedCSS,opts.themedCSS||{});
			msg=msg===undefined?opts.message:msg;

			//removethecurrentblock(ifthereisone)
			if(full&&pageBlock)
				remove(window,{fadeOut:0});

			//ifanexistingelementisbeingusedastheblockingcontentthenwecapture
			//itscurrentplaceintheDOM(andcurrentdisplaystyle)sowecanrestore
			//itwhenweunblock
			if(msg&&typeofmsg!='string'&&(msg.parentNode||msg.jquery)){
				varnode=msg.jquery?msg[0]:msg;
				vardata={};
				$(el).data('blockUI.history',data);
				data.el=node;
				data.parent=node.parentNode;
				data.display=node.style.display;
				data.position=node.style.position;
				if(data.parent)
					data.parent.removeChild(node);
			}

			$(el).data('blockUI.onUnblock',opts.onUnblock);
			varz=opts.baseZ;

			//blockUIuses3layersforblocking,forsimplicitytheyareallusedoneveryplatform;
			//layer1istheiframelayerwhichisusedtosupressbleedthroughofunderlyingcontent
			//layer2istheoverlaylayerwhichhasopacityandawaitcursor(bydefault)
			//layer3isthemessagecontentthatisdisplayedwhileblocking
			varlyr1,lyr2,lyr3,s;
			if(msie||opts.forceIframe)
				lyr1=$('<iframeclass="blockUI"style="z-index:'+(z++)+';display:none;border:none;margin:0;padding:0;position:absolute;width:100%;height:100%;top:0;left:0"src="'+opts.iframeSrc+'"></iframe>');
			else
				lyr1=$('<divclass="blockUI"style="display:none"></div>');

			if(opts.theme)
				lyr2=$('<divclass="blockUIblockOverlayui-widget-overlay"style="z-index:'+(z++)+';display:none"></div>');
			else
				lyr2=$('<divclass="blockUIblockOverlay"style="z-index:'+(z++)+';display:none;border:none;margin:0;padding:0;width:100%;height:100%;top:0;left:0"></div>');

			if(opts.theme&&full){
				s='<divclass="blockUI'+opts.blockMsgClass+'blockPageui-dialogui-widgetui-corner-all"style="z-index:'+(z+10)+';display:none;position:fixed">';
				if(opts.title){
					s+='<divclass="ui-widget-headerui-dialog-titlebarui-corner-allblockTitle">'+(opts.title||'&nbsp;')+'</div>';
				}
				s+='<divclass="ui-widget-contentui-dialog-content"></div>';
				s+='</div>';
			}
			elseif(opts.theme){
				s='<divclass="blockUI'+opts.blockMsgClass+'blockElementui-dialogui-widgetui-corner-all"style="z-index:'+(z+10)+';display:none;position:absolute">';
				if(opts.title){
					s+='<divclass="ui-widget-headerui-dialog-titlebarui-corner-allblockTitle">'+(opts.title||'&nbsp;')+'</div>';
				}
				s+='<divclass="ui-widget-contentui-dialog-content"></div>';
				s+='</div>';
			}
			elseif(full){
				s='<divclass="blockUI'+opts.blockMsgClass+'blockPage"style="z-index:'+(z+10)+';display:none;position:fixed"></div>';
			}
			else{
				s='<divclass="blockUI'+opts.blockMsgClass+'blockElement"style="z-index:'+(z+10)+';display:none;position:absolute"></div>';
			}
			lyr3=$(s);

			//ifwehaveamessage,styleit
			if(msg){
				if(opts.theme){
					lyr3.css(themedCSS);
					lyr3.addClass('ui-widget-content');
				}
				else
					lyr3.css(css);
			}

			//styletheoverlay
			if(!opts.theme/*&&(!opts.applyPlatformOpacityRules)*/)
				lyr2.css(opts.overlayCSS);
			lyr2.css('position',full?'fixed':'absolute');

			//makeiframelayertransparentinIE
			if(msie||opts.forceIframe)
				lyr1.css('opacity',0.0);

			//$([lyr1[0],lyr2[0],lyr3[0]]).appendTo(full?'body':el);
			varlayers=[lyr1,lyr2,lyr3],$par=full?$('body'):$(el);
			$.each(layers,function(){
				this.appendTo($par);
			});

			if(opts.theme&&opts.draggable&&$.fn.draggable){
				lyr3.draggable({
					handle:'.ui-dialog-titlebar',
					cancel:'li'
				});
			}

			//ie7mustuseabsolutepositioninginquirksmodeandtoaccountforactivexissues(whenscrolling)
			varexpr=setExpr&&(!$.support.boxModel||$('object,embed',full?null:el).length>0);
			if(ie6||expr){
				//givebody100%height
				if(full&&opts.allowBodyStretch&&$.support.boxModel)
					$('html,body').css('height','100%');

				//fixie6issuewhenblockedelementhasaborderwidth
				if((ie6||!$.support.boxModel)&&!full){
					vart=sz(el,'borderTopWidth'),l=sz(el,'borderLeftWidth');
					varfixT=t?'(0-'+t+')':0;
					varfixL=l?'(0-'+l+')':0;
				}

				//simulatefixedposition
				$.each(layers,function(i,o){
					vars=o[0].style;
					s.position='absolute';
					if(i<2){
						if(full)
							s.setExpression('height','Math.max(document.body.scrollHeight,document.body.offsetHeight)-(jQuery.support.boxModel?0:'+opts.quirksmodeOffsetHack+')+"px"');
						else
							s.setExpression('height','this.parentNode.offsetHeight+"px"');
						if(full)
							s.setExpression('width','jQuery.support.boxModel&&document.documentElement.clientWidth||document.body.clientWidth+"px"');
						else
							s.setExpression('width','this.parentNode.offsetWidth+"px"');
						if(fixL)s.setExpression('left',fixL);
						if(fixT)s.setExpression('top',fixT);
					}
					elseif(opts.centerY){
						if(full)s.setExpression('top','(document.documentElement.clientHeight||document.body.clientHeight)/2-(this.offsetHeight/2)+(blah=document.documentElement.scrollTop?document.documentElement.scrollTop:document.body.scrollTop)+"px"');
						s.marginTop=0;
					}
					elseif(!opts.centerY&&full){
						vartop=(opts.css&&opts.css.top)?parseInt(opts.css.top,10):0;
						varexpression='((document.documentElement.scrollTop?document.documentElement.scrollTop:document.body.scrollTop)+'+top+')+"px"';
						s.setExpression('top',expression);
					}
				});
			}

			//showthemessage
			if(msg){
				if(opts.theme)
					lyr3.find('.ui-widget-content').append(msg);
				else
					lyr3.append(msg);
				if(msg.jquery||msg.nodeType)
					$(msg).show();
			}

			if((msie||opts.forceIframe)&&opts.showOverlay)
				lyr1.show();//opacityiszero
			if(opts.fadeIn){
				varcb=opts.onBlock?opts.onBlock:noOp;
				varcb1=(opts.showOverlay&&!msg)?cb:noOp;
				varcb2=msg?cb:noOp;
				if(opts.showOverlay)
					lyr2._fadeIn(opts.fadeIn,cb1);
				if(msg)
					lyr3._fadeIn(opts.fadeIn,cb2);
			}
			else{
				if(opts.showOverlay)
					lyr2.show();
				if(msg)
					lyr3.show();
				if(opts.onBlock)
					opts.onBlock.bind(lyr3)();
			}

			//bindkeyandmouseevents
			bind(1,el,opts);

			if(full){
				pageBlock=lyr3[0];
				pageBlockEls=$(opts.focusableElements,pageBlock);
				if(opts.focusInput)
					setTimeout(focus,20);
			}
			else
				center(lyr3[0],opts.centerX,opts.centerY);

			if(opts.timeout){
				//auto-unblock
				varto=setTimeout(function(){
					if(full)
						$.unblockUI(opts);
					else
						$(el).unblock(opts);
				},opts.timeout);
				$(el).data('blockUI.timeout',to);
			}
		}

		//removetheblock
		functionremove(el,opts){
			varcount;
			varfull=(el==window);
			var$el=$(el);
			vardata=$el.data('blockUI.history');
			varto=$el.data('blockUI.timeout');
			if(to){
				clearTimeout(to);
				$el.removeData('blockUI.timeout');
			}
			opts=$.extend({},$.blockUI.defaults,opts||{});
			bind(0,el,opts);//unbindevents

			if(opts.onUnblock===null){
				opts.onUnblock=$el.data('blockUI.onUnblock');
				$el.removeData('blockUI.onUnblock');
			}

			varels;
			if(full)//crazyselectortohandleoddfielderrorsinie6/7
				els=$('body').children().filter('.blockUI').add('body>.blockUI');
			else
				els=$el.find('>.blockUI');

			//fixcursorissue
			if(opts.cursorReset){
				if(els.length>1)
					els[1].style.cursor=opts.cursorReset;
				if(els.length>2)
					els[2].style.cursor=opts.cursorReset;
			}

			if(full)
				pageBlock=pageBlockEls=null;

			if(opts.fadeOut){
				count=els.length;
				els.stop().fadeOut(opts.fadeOut,function(){
					if(--count===0)
						reset(els,data,opts,el);
				});
			}
			else
				reset(els,data,opts,el);
		}

		//moveblockingelementbackintotheDOMwhereitstarted
		functionreset(els,data,opts,el){
			var$el=$(el);
			if($el.data('blockUI.isBlocked'))
				return;

			els.each(function(i,o){
				//removeviaDOMcallssowedon'tloseeventhandlers
				if(this.parentNode)
					this.parentNode.removeChild(this);
			});

			if(data&&data.el){
				data.el.style.display=data.display;
				data.el.style.position=data.position;
				data.el.style.cursor='default';//#59
				if(data.parent)
					data.parent.appendChild(data.el);
				$el.removeData('blockUI.history');
			}

			if($el.data('blockUI.static')){
				$el.css('position','static');//#22
			}

			if(typeofopts.onUnblock=='function')
				opts.onUnblock(el,opts);

			//fixissueinSafari6whereblockartifactsremainuntilreflow
			varbody=$(document.body),w=body.width(),cssW=body[0].style.width;
			body.width(w-1).width(w);
			body[0].style.width=cssW;
		}

		//bind/unbindthehandler
		functionbind(b,el,opts){
			varfull=el==window,$el=$(el);

			//don'tbotherunbindingifthereisnothingtounbind
			if(!b&&(full&&!pageBlock||!full&&!$el.data('blockUI.isBlocked')))
				return;

			$el.data('blockUI.isBlocked',b);

			//don'tbindeventswhenoverlayisnotinuseorifbindEventsisfalse
			if(!full||!opts.bindEvents||(b&&!opts.showOverlay))
				return;

			//bindanchorsandinputsformouseandkeyevents
			varevents='mousedownmouseupkeydownkeypresskeyuptouchstarttouchendtouchmove';
			if(b)
				$(document).bind(events,opts,handler);
			else
				$(document).unbind(events,handler);

		//formerimpl...
		//		var$e=$('a,:input');
		//		b?$e.bind(events,opts,handler):$e.unbind(events,handler);
		}

		//eventhandlertosuppresskeyboard/mouseeventswhenblocking
		functionhandler(e){
			//allowtabnavigation(conditionally)
			if(e.type==='keydown'&&e.keyCode&&e.keyCode==9){
				if(pageBlock&&e.data.constrainTabKey){
					varels=pageBlockEls;
					varfwd=!e.shiftKey&&e.target===els[els.length-1];
					varback=e.shiftKey&&e.target===els[0];
					if(fwd||back){
						setTimeout(function(){focus(back);},10);
						returnfalse;
					}
				}
			}
			varopts=e.data;
			vartarget=$(e.target);
			if(target.hasClass('blockOverlay')&&opts.onOverlayClick)
				opts.onOverlayClick(e);

			//alloweventswithinthemessagecontent
			if(target.parents('div.'+opts.blockMsgClass).length>0)
				returntrue;

			//alloweventsforcontentthatisnotbeingblocked
			returntarget.parents().children().filter('div.blockUI').length===0;
		}

		functionfocus(back){
			if(!pageBlockEls)
				return;
			vare=pageBlockEls[back===true?pageBlockEls.length-1:0];
			if(e)
				e.focus();
		}

		functioncenter(el,x,y){
			varp=el.parentNode,s=el.style;
			varl=((p.offsetWidth-el.offsetWidth)/2)-sz(p,'borderLeftWidth');
			vart=((p.offsetHeight-el.offsetHeight)/2)-sz(p,'borderTopWidth');
			if(x)s.left=l>0?(l+'px'):'0';
			if(y)s.top =t>0?(t+'px'):'0';
		}

		functionsz(el,p){
			returnparseInt($.css(el,p),10)||0;
		}

	}


	/*globaldefine:true*/
	if(typeofdefine==='function'&&define.amd&&define.amd.jQuery){
		define(['jquery'],setup);
	}else{
		setup(jQuery);
	}

})();
